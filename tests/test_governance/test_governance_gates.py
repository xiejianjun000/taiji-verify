"""
Governance Gates Tests
"""

import pytest
from taiji_verify.governance.governance_gates import (
    GovernanceGate, GateType, GateResult, GateState
)


class TestGovernanceGates:
    """治理门测试"""

    def test_gate1_problem_formation(self):
        """测试问题构成门"""
        gate = GovernanceGate(GateType.PROBLEM_FORMATION)
        result = gate.evaluate("这是一个有效的问题描述？")
        assert isinstance(result.state, GateState)

    def test_gate2_world_alignment(self):
        """测试世界对齐门"""
        gate = GovernanceGate(GateType.WORLD_ALIGNMENT)
        result = gate.evaluate("地球是圆的")
        assert result.passed is True

    def test_gate3_collapse_geometry(self):
        """测试崩溃几何门"""
        gate = GovernanceGate(GateType.COLLAPSE_GEOMETRY)
        result = gate.evaluate("正常输出内容")
        assert result.passed is True

    def test_all_7_gates(self):
        """测试全部7个门"""
        for gate_type in GateType:
            gate = GovernanceGate(gate_type)
            result = gate.evaluate("测试输入")
            assert isinstance(result.passed, bool)

    def test_gate_result_structure(self):
        """测试门结果结构"""
        gate = GovernanceGate(GateType.PROBLEM_FORMATION)
        result = gate.evaluate("有效问题")
        assert hasattr(result, 'passed')
        assert hasattr(result, 'state')
        assert hasattr(result, 'reason')
