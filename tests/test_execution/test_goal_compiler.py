"""
Goal Compiler Tests
"""

import pytest
from taiji_verify.execution.goal_compiler import (
    GoalCompiler, TruthObject, ClaimCeiling, VerificationGate
)


class TestGoalCompiler:
    """目标编译器测试"""

    def test_create_truth_objects(self):
        """测试创建真理对象"""
        compiler = GoalCompiler()
        objects = compiler.create_truth_objects("碳排放权交易管理办法")
        assert len(objects) > 0
        assert all(isinstance(obj, TruthObject) for obj in objects)

    def test_create_claim_ceilings(self):
        """测试创建声明上限"""
        compiler = GoalCompiler()
        ceilings = compiler.create_claim_ceilings("碳排放权交易")
        assert len(ceilings) > 0

    def test_extended_compile(self):
        """测试扩展编译"""
        compiler = GoalCompiler()
        result = compiler.compile_extended("分析碳排放权交易政策")
        assert result.truth_objects is not None
        assert result.verification_gates is not None
