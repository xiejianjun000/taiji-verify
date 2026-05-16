"""SymptomMap 病候图测试"""
import pytest

class TestSymptomMap:
    def test_symptom_map_init(self):
        from taiji_verify.symptom_map import SymptomMap
        symptom_map = SymptomMap()
        assert symptom_map is not None

    def test_failure_level(self):
        from taiji_verify.symptom_map import FailureLevel
        assert FailureLevel.RAG is not None
        assert FailureLevel.REASONING is not None
        assert len(FailureLevel) > 0

    def test_failure_pattern(self):
        from taiji_verify.symptom_map import FailurePattern
        assert len(FailurePattern) >= 16  # 应该有16种失败模式类型
