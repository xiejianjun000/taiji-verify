"""FailureModeDetector 失败模式检测测试"""
import pytest

class TestFailureModes:
    def test_failure_modes_init(self):
        from taiji_verify.failure_modes import FailureModeDetector
        detector = FailureModeDetector()
        assert detector is not None

    def test_failure_severity(self):
        from taiji_verify.failure_modes import FailureSeverity
        assert FailureSeverity.CRITICAL is not None
        assert FailureSeverity.ERROR is not None
        assert FailureSeverity.WARNING is not None

    def test_failure_mode(self):
        from taiji_verify.failure_modes import FailureMode
        # 检查FailureMode存在
        assert FailureMode is not None
