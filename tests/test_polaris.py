"""Polaris 北辰编译器测试"""
import pytest

class TestPolaris:
    def test_compiler_init(self):
        from taiji_verify.polaris import PolarisCompiler
        compiler = PolarisCompiler()
        assert compiler is not None

    def test_task_type(self):
        from taiji_verify.polaris import TaskType
        assert TaskType.ATOMIC is not None
        assert TaskType.COMPOSITE is not None
        assert TaskType.CONDITIONAL is not None

    def test_task_state(self):
        from taiji_verify.polaris import TaskState
        assert TaskState.PENDING is not None
        assert TaskState.COMPLETED is not None
