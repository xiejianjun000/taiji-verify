"""
Leak Auditor Tests
"""

import pytest
from taiji_verify.execution.leak_auditor import LeakAuditor, AuditResult, LayerStatus


class TestLeakAuditor:
    """泄漏审计器测试"""

    def test_check_upstream_completion(self):
        """测试检查上游完成"""
        auditor = LeakAuditor()
        result = auditor.check("layer_2_detection", "output_text")
        assert isinstance(result, AuditResult)
        assert hasattr(result, 'leak_detected')

    def test_block_downstream_if_incomplete(self):
        """测试阻止下游"""
        auditor = LeakAuditor()
        auditor.mark_incomplete("layer_2_detection")
        result = auditor.check("layer_3_reasoning", "output")
        assert result.leak_detected is True

    def test_allow_downstream_when_complete(self):
        """测试允许下游"""
        auditor = LeakAuditor()
        auditor.mark_complete("layer_1_core")
        auditor.mark_complete("layer_2_detection")
        result = auditor.check("layer_3_reasoning", "output")
        assert result.leak_detected is False

    def test_mark_status(self):
        """测试状态标记"""
        auditor = LeakAuditor()
        auditor.mark_failed("layer_2_detection")
        assert auditor.get_layer_status("layer_2_detection") == LayerStatus.FAILED
