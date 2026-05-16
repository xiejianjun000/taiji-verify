"""
Coupler - 耦合器

仅当ΔS下降或趋势向下时允许推进。
强制局部移动与全局张力合约。
"""

from __future__ import annotations

from typing import Optional


class ContractViolation(Exception):
    """合约违反异常"""
    pass


class Coupler:
    """
    耦合器

    Usage::
        coupler = Coupler()
        assert coupler.check_progression(0.8, 0.5) is True
        assert coupler.check_progression(0.5, 0.8) is False
    """

    def check_progression(self, current_delta: float, next_delta: float) -> bool:
        """
        检查推进是否允许

        Args:
            current_delta: 当前ΔS
            next_delta: 下一个ΔS

        Returns:
            是否允许推进
        """
        return next_delta <= current_delta

    def enforce_contract(
        self,
        current_delta: float,
        next_delta: float,
        local_force: float,
        global_tension: float,
    ) -> bool:
        """
        强制合约

        Args:
            current_delta: 当前ΔS
            next_delta: 下一个ΔS
            local_force: 局部力
            global_tension: 全局张力

        Returns:
            是否通过合约

        Raises:
            ContractViolation: 当合约违反时
        """
        progression_allowed = self.check_progression(current_delta, next_delta)

        if not progression_allowed:
            tension_ratio = global_tension / (local_force + 1e-10)
            if tension_ratio < 0.5:
                raise ContractViolation(
                    f"ΔS从{current_delta}增加到{next_delta}，违反合约。"
                    f"局部力={local_force}, 全局张力={global_tension}"
                )
            return False

        return True

    def compute_coupling_strength(
        self,
        delta_s1: float,
        delta_s2: float,
    ) -> float:
        """
        计算耦合强度

        Args:
            delta_s1: ΔS1
            delta_s2: ΔS2

        Returns:
            耦合强度 ∈ [0, 1]
        """
        diff = abs(delta_s1 - delta_s2)
        return max(0.0, 1.0 - diff)

    def validate_continuity(
        self,
        delta_sequence: list[float],
    ) -> tuple[bool, list[int]]:
        """
        验证连续性

        Args:
            delta_sequence: ΔS序列

        Returns:
            (是否连续, 违反索引列表)
        """
        violations = []

        for i in range(1, len(delta_sequence)):
            if delta_sequence[i] > delta_sequence[i - 1] + 0.1:
                violations.append(i)

        return len(violations) == 0, violations
