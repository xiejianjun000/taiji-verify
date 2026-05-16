"""
Coupler Tests
"""

import pytest
from taiji_verify.reasoning.coupler import Coupler, ContractViolation


class TestCoupler:
    """耦合器测试"""

    def test_coupler_delta_s_decrease_only(self):
        """测试ΔS下降检查"""
        coupler = Coupler()
        assert coupler.check_progression(0.8, 0.5) is True
        assert coupler.check_progression(0.5, 0.8) is False
        assert coupler.check_progression(0.5, 0.5) is True

    def test_contract_enforcement_raises(self):
        """测试合约强制（违反合约时抛异常）"""
        coupler = Coupler()
        with pytest.raises(ContractViolation):
            coupler.enforce_contract(
                current_delta=0.5,
                next_delta=0.8,
                local_force=1.0,
                global_tension=0.3
            )

    def test_contract_enforcement_returns_false(self):
        """测试合约强制（违反合约但张力足够时不抛异常）"""
        coupler = Coupler()
        result = coupler.enforce_contract(
            current_delta=0.5,
            next_delta=0.8,
            local_force=1.0,
            global_tension=0.6
        )
        assert result is False

    def test_contract_allows_progression(self):
        """测试合约允许推进"""
        coupler = Coupler()
        result = coupler.enforce_contract(
            current_delta=0.8,
            next_delta=0.5,
            local_force=1.0,
            global_tension=0.3
        )
        assert result is True

    def test_coupling_strength(self):
        """测试耦合强度"""
        coupler = Coupler()
        strength = coupler.compute_coupling_strength(0.3, 0.4)
        assert 0 < strength <= 1.0

    def test_validate_continuity(self):
        """测试连续性验证"""
        coupler = Coupler()
        continuous, violations = coupler.validate_continuity([0.1, 0.2, 0.3])
        assert continuous is True
        assert len(violations) == 0
