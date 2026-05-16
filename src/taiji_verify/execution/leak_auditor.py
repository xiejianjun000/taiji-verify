"""
Leak Auditor - 泄漏审计

防止上游未验证完成时启动下游工作。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class LayerStatus(str, Enum):
    """层级状态"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AuditResult:
    """审计结果"""

    leak_detected: bool
    upstream_status: LayerStatus
    reason: str
    details: dict = field(default_factory=dict)


class LeakAuditor:
    """
    泄漏审计器

    Usage::
        auditor = LeakAuditor()
        auditor.mark_complete("layer_2")
        result = auditor.check("layer_3_reasoning", "output")
        assert result.leak_detected is False
    """

    LAYER_ORDER = [
        "layer_1_core",
        "layer_2_detection",
        "layer_3_reasoning",
        "layer_4_diagnosis",
        "layer_5_governance",
        "layer_6_execution",
    ]

    def __init__(self):
        self._layer_status: dict[str, LayerStatus] = {
            layer: LayerStatus.PENDING for layer in self.LAYER_ORDER
        }

    def mark_complete(self, layer_name: str) -> None:
        """标记完成"""
        if layer_name in self._layer_status:
            self._layer_status[layer_name] = LayerStatus.COMPLETED

    def mark_incomplete(self, layer_name: str) -> None:
        """标记未完成"""
        if layer_name in self._layer_status:
            self._layer_status[layer_name] = LayerStatus.PENDING

    def mark_failed(self, layer_name: str) -> None:
        """标记失败"""
        if layer_name in self._layer_status:
            self._layer_status[layer_name] = LayerStatus.FAILED

    def check(self, layer_name: str, output: str) -> AuditResult:
        """检查泄漏"""
        if layer_name not in self.LAYER_ORDER:
            return AuditResult(
                leak_detected=False,
                upstream_status=LayerStatus.PENDING,
                reason="未知层级",
            )

        layer_index = self.LAYER_ORDER.index(layer_name)

        for i in range(layer_index):
            upstream = self.LAYER_ORDER[i]
            status = self._layer_status.get(upstream, LayerStatus.PENDING)

            if status != LayerStatus.COMPLETED:
                return AuditResult(
                    leak_detected=True,
                    upstream_status=status,
                    reason=f"上游{upstream}未完成",
                    details={"blocking_layer": upstream},
                )

        return AuditResult(
            leak_detected=False,
            upstream_status=LayerStatus.COMPLETED,
            reason="所有上游已完成",
        )

    def get_layer_status(self, layer_name: str) -> LayerStatus:
        """获取层级状态"""
        return self._layer_status.get(layer_name, LayerStatus.PENDING)

    def reset(self) -> None:
        """重置"""
        self._layer_status = {layer: LayerStatus.PENDING for layer in self.LAYER_ORDER}
