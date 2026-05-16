"""
Checkpoint - 记忆检查点

save/restore/gate_check。门控：某些转换只在特定ΔS区间允许。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime


@dataclass
class Checkpoint:
    """检查点"""
    id: str
    step_name: str
    data: dict
    delta_s: float
    gate_zone: str
    timestamp: float


class CheckpointManager:
    """
    检查点管理器

    Usage::
        manager = CheckpointManager()
        manager.save("step1", {"data": "value"}, delta_s=0.5)
        checkpoint = manager.restore("step1")
        assert checkpoint.data["data"] == "value"
    """

    def __init__(self):
        self._checkpoints: dict[str, Checkpoint] = {}

    def save(
        self,
        step_name: str,
        data: dict,
        delta_s: float,
        gate_zone: str = "TRANSIT",
    ) -> str:
        """保存检查点"""
        checkpoint_id = f"{step_name}_{len(self._checkpoints)}"
        checkpoint = Checkpoint(
            id=checkpoint_id,
            step_name=step_name,
            data=data,
            delta_s=delta_s,
            gate_zone=gate_zone,
            timestamp=datetime.now().timestamp(),
        )
        self._checkpoints[checkpoint_id] = checkpoint
        return checkpoint_id

    def restore(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """恢复检查点"""
        return self._checkpoints.get(checkpoint_id)

    def gate_check(self, from_zone: str, to_zone: str) -> bool:
        """
        门控检查

        允许的转换:
        - SAFE -> SAFE, TRANSIT
        - TRANSIT -> SAFE, TRANSIT, RISK
        - RISK -> TRANSIT, RISK, DANGER
        - DANGER -> RISK, DANGER
        """
        allowed_transitions = {
            "SAFE": ["SAFE", "TRANSIT"],
            "TRANSIT": ["SAFE", "TRANSIT", "RISK"],
            "RISK": ["TRANSIT", "RISK", "DANGER"],
            "DANGER": ["RISK", "DANGER"],
        }

        return to_zone in allowed_transitions.get(from_zone, [])

    def list_checkpoints(self) -> list[Checkpoint]:
        """列出所有检查点"""
        return list(self._checkpoints.values())

    def clear(self) -> None:
        """清除所有检查点"""
        self._checkpoints.clear()

    def get_latest(self) -> Optional[Checkpoint]:
        """获取最新检查点"""
        if not self._checkpoints:
            return None
        return list(self._checkpoints.values())[-1]
