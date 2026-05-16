"""
Hallucination Detector Tests
"""

import pytest
from taiji_verify.detection.hallucination_detector import (
    HallucinationDetector, RiskLevel, DetectionResult, SegmentResult
)


class TestHallucinationDetector:
    """幻觉检测器测试"""

    def test_detect_with_weighted_score(self):
        """测试加权评分检测"""
        detector = HallucinationDetector()
        text = "根据GB12345标准，环境质量应符合规定要求"
        result = detector.detect(text)
        assert hasattr(result, 'weighted_score')
        assert isinstance(result.risk_level, RiskLevel)

    def test_risk_level_threshold(self):
        """测试风险等级阈值"""
        detector = HallucinationDetector(risk_threshold=0.8)
        detector.rule_weight = 0.4
        detector.consistency_weight = 0.3
        detector.trace_weight = 0.3
        result = detector.detect("测试文本内容")
        assert isinstance(result.risk_level, RiskLevel)

    def test_segmented_detection(self):
        """测试分段检测"""
        detector = HallucinationDetector()
        text = "第一句内容。第二句内容。第三句内容。"
        result = detector.detect_segmented(text)
        assert len(result.segments) >= 3

    def test_risk_levels(self):
        """测试风险等级"""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.CRITICAL.value == "critical"

    def test_empty_text(self):
        """测试空文本"""
        detector = HallucinationDetector()
        result = detector.detect("")
        assert result.weighted_score >= 0
