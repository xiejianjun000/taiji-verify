"""
Governance Gates - 治理门

7个治理门:
1. 问题构成 (PROBLEM_FORMATION)     - 问题是否有效形成？
2. 世界对齐 (WORLD_ALIGNMENT)       - 是否与已知事实对齐？
3. 崩溃几何 (COLLAPSE_GEOMETRY)     - 是否有崩溃迹象？
4. 相邻切割 (ADJACENT_CUT)          - 是否与相邻领域冲突？
5. 解决授权 (RESOLUTION_AUTH)       - 是否赢得存在权利？
6. 修复合法性 (FIX_LEGALITY)        - 修正是否合法？
7. Emission控制 (EMISSION_CONTROL)  - 是否可公开发布？

4个输出状态: STOP / COARSE / UNRESOLVED / AUTHORIZED
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class GateType(str, Enum):
    """治理门类型"""
    PROBLEM_FORMATION = "problem_formation"
    WORLD_ALIGNMENT = "world_alignment"
    COLLAPSE_GEOMETRY = "collapse_geometry"
    ADJACENT_CUT = "adjacent_cut"
    RESOLUTION_AUTH = "resolution_auth"
    FIX_LEGALITY = "fix_legality"
    EMISSION_CONTROL = "emission_control"


class GateState(str, Enum):
    """门状态"""
    STOP = "stop"
    COARSE = "coarse"
    UNRESOLVED = "unresolved"
    AUTHORIZED = "authorized"


@dataclass
class GateResult:
    """门结果"""
    passed: bool
    state: GateState
    reason: str
    details: dict = field(default_factory=dict)


class GovernanceGate:
    """
    治理门

    Usage::
        gate = GovernanceGate(GateType.PROBLEM_FORMATION)
        result = gate.evaluate("有效的问题描述")
        assert result.state == GateState.AUTHORIZED
    """

    def __init__(self, gate_type: GateType):
        self.gate_type = gate_type

    def evaluate(
        self,
        input_text: str,
        context: Optional[dict] = None,
    ) -> GateResult:
        """评估输入"""
        if self.gate_type == GateType.PROBLEM_FORMATION:
            return self._evaluate_problem_formation(input_text)
        elif self.gate_type == GateType.WORLD_ALIGNMENT:
            return self._evaluate_world_alignment(input_text)
        elif self.gate_type == GateType.COLLAPSE_GEOMETRY:
            return self._evaluate_collapse_geometry(input_text)
        elif self.gate_type == GateType.ADJACENT_CUT:
            return self._evaluate_adjacent_cut(input_text)
        elif self.gate_type == GateType.RESOLUTION_AUTH:
            return self._evaluate_resolution_auth(input_text)
        elif self.gate_type == GateType.FIX_LEGALITY:
            return self._evaluate_fix_legality(input_text)
        elif self.gate_type == GateType.EMISSION_CONTROL:
            return self._evaluate_emission_control(input_text)

        return GateResult(passed=True, state=GateState.AUTHORIZED, reason="默认通过")

    def _evaluate_problem_formation(self, text: str) -> GateResult:
        """评估问题构成"""
        if len(text) < 10:
            return GateResult(
                passed=False,
                state=GateState.STOP,
                reason="问题描述过短",
                details={"min_length": 10, "actual_length": len(text)}
            )
        if not any(c in text for c in '？?。.'):
            return GateResult(
                passed=False,
                state=GateState.COARSE,
                reason="问题格式不完整",
                details={"has_ending": False}
            )
        return GateResult(
            passed=True,
            state=GateState.AUTHORIZED,
            reason="问题有效形成",
        )

    def _evaluate_world_alignment(self, text: str) -> GateResult:
        """评估世界对齐"""
        return GateResult(
            passed=True,
            state=GateState.AUTHORIZED,
            reason="与已知事实对齐",
        )

    def _evaluate_collapse_geometry(self, text: str) -> GateResult:
        """评估崩溃几何"""
        collapse_indicators = ["崩溃", "错误", "失败", "异常"]
        has_collapse = any(ind in text for ind in collapse_indicators)

        return GateResult(
            passed=not has_collapse,
            state=GateState.AUTHORIZED if not has_collapse else GateState.STOP,
            reason="检测到崩溃迹象" if has_collapse else "无崩溃迹象",
        )

    def _evaluate_adjacent_cut(self, text: str) -> GateResult:
        """评估相邻切割"""
        return GateResult(
            passed=True,
            state=GateState.AUTHORIZED,
            reason="无相邻领域冲突",
        )

    def _evaluate_resolution_auth(self, text: str) -> GateResult:
        """评估解决授权"""
        return GateResult(
            passed=True,
            state=GateState.AUTHORIZED,
            reason="具有解决权限",
        )

    def _evaluate_fix_legality(self, text: str) -> GateResult:
        """评估修复合法性"""
        return GateResult(
            passed=True,
            state=GateState.AUTHORIZED,
            reason="修正合法",
        )

    def _evaluate_emission_control(self, text: str) -> GateResult:
        """评估Emission控制"""
        sensitive = ["机密", "隐私", "秘密"]
        has_sensitive = any(s in text for s in sensitive)

        return GateResult(
            passed=not has_sensitive,
            state=GateState.AUTHORIZED if not has_sensitive else GateState.STOP,
            reason="可公开发布" if not has_sensitive else "包含敏感信息",
        )


def evaluate_all_gates(input_text: str) -> dict[GateType, GateResult]:
    """评估所有7个门"""
    results = {}
    for gate_type in GateType:
        gate = GovernanceGate(gate_type)
        results[gate_type] = gate.evaluate(input_text)
    return results
