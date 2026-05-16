"""
Hallucination Detector Tests
"""

import pytest
from unittest.mock import Mock, patch
from taiji_verify.detection.hallucination_detector import (
    HallucinationDetector,
    RiskLevel,
    DetectionResult,
    SegmentResult,
)


class TestRiskLevel:
    def test_risk_level_values(self):
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"


class TestSegmentResult:
    def test_segment_result_creation(self):
        segment = SegmentResult(
            text="测试文本",
            is_hallucination=True,
            confidence=0.8,
            matched_sources=["source1"],
            rule_score=0.7,
            consistency_score=0.6,
            trace_score=0.5,
        )
        assert segment.text == "测试文本"
        assert segment.is_hallucination is True
        assert segment.confidence == 0.8
        assert "source1" in segment.matched_sources


class TestDetectionResult:
    def test_detection_result_creation(self):
        result = DetectionResult(
            weighted_score=0.6,
            risk_level=RiskLevel.HIGH,
            details={"test": "data"},
            segments=[],
        )
        assert result.weighted_score == 0.6
        assert result.risk_level == RiskLevel.HIGH


class TestHallucinationDetector:
    """幻觉检测器测试"""

    def test_init_default(self):
        detector = HallucinationDetector()
        assert detector.rule_weight == 0.4
        assert detector.consistency_weight == 0.3
        assert detector.trace_weight == 0.3
        assert detector.risk_threshold == 0.8

    def test_init_custom_weights(self):
        detector = HallucinationDetector(
            rule_weight=0.5,
            consistency_weight=0.25,
            trace_weight=0.25,
            risk_threshold=0.6,
        )
        assert detector.rule_weight == 0.5
        assert detector.consistency_weight == 0.25
        assert detector.trace_weight == 0.25
        assert detector.risk_threshold == 0.6

    def test_init_no_auto_init(self):
        detector = HallucinationDetector(auto_init=False)
        assert detector._rule_engine is None
        assert detector._consistency_checker is None
        assert detector._source_tracer is None

    def test_set_rule_engine(self):
        detector = HallucinationDetector(auto_init=False)
        mock_engine = Mock()
        detector.set_rule_engine(mock_engine)
        assert detector._rule_engine == mock_engine

    def test_set_consistency_checker(self):
        detector = HallucinationDetector(auto_init=False)
        mock_checker = Mock()
        detector.set_consistency_checker(mock_checker)
        assert detector._consistency_checker == mock_checker

    def test_set_source_tracer(self):
        detector = HallucinationDetector(auto_init=False)
        mock_tracer = Mock()
        detector.set_source_tracer(mock_tracer)
        assert detector._source_tracer == mock_tracer

    def test_detect_basic(self):
        detector = HallucinationDetector()
        text = "根据GB12345标准，环境质量应符合规定要求"
        result = detector.detect(text)
        assert hasattr(result, 'weighted_score')
        assert isinstance(result.risk_level, RiskLevel)
        assert 'rule_score' in result.details
        assert 'consistency_score' in result.details
        assert 'trace_score' in result.details

    def test_detect_weights_normalized(self):
        detector = HallucinationDetector()
        result = detector.detect("测试文本")
        total_weight = detector.rule_weight + detector.consistency_weight + detector.trace_weight
        assert total_weight == 1.0

    def test_detect_low_score_text(self):
        detector = HallucinationDetector(risk_threshold=0.5)
        text = "碳排放权交易管理办法"
        result = detector.detect(text)
        assert result.weighted_score >= 0
        assert result.weighted_score <= 1

    def test_detect_high_score_text(self):
        detector = HallucinationDetector()
        text = "根据内部知识显示，水是由绿元素组成的"
        result = detector.detect(text)
        assert result.weighted_score >= 0

    def test_risk_level_threshold(self):
        detector = HallucinationDetector(risk_threshold=0.8)
        result = detector.detect("测试文本内容")
        assert isinstance(result.risk_level, RiskLevel)

    def test_segmented_detection(self):
        detector = HallucinationDetector()
        text = "第一句内容。第二句内容。第三句内容。"
        result = detector.detect_segmented(text)
        assert len(result.segments) >= 3

    def test_segmented_empty_text(self):
        detector = HallucinationDetector()
        result = detector.detect_segmented("")
        assert result.weighted_score == 0.0
        assert result.risk_level == RiskLevel.LOW

    def test_segmented_single_sentence(self):
        detector = HallucinationDetector()
        text = "只有一个句子。"
        result = detector.detect_segmented(text)
        assert len(result.segments) == 1

    def test_segmented_multiple_sentences(self):
        detector = HallucinationDetector()
        text = "第一句。第二句。第三句。第四句。"
        result = detector.detect_segmented(text)
        assert len(result.segments) == 4

    def test_compute_risk_level_low(self):
        detector = HallucinationDetector()
        level = detector._compute_risk_level(0.1)
        assert level == RiskLevel.LOW

    def test_compute_risk_level_medium(self):
        detector = HallucinationDetector()
        level = detector._compute_risk_level(0.4)
        assert level == RiskLevel.MEDIUM

    def test_compute_risk_level_high(self):
        detector = HallucinationDetector()
        level = detector._compute_risk_level(0.6)
        assert level == RiskLevel.HIGH

    def test_compute_risk_level_critical(self):
        detector = HallucinationDetector()
        level = detector._compute_risk_level(0.9)
        assert level == RiskLevel.CRITICAL

    def test_split_sentences(self):
        detector = HallucinationDetector()
        text = "第一句。第二句！第三句？第四句；第五句\n第六句"
        sentences = detector._split_sentences(text)
        assert len(sentences) >= 5

    def test_split_sentences_empty(self):
        detector = HallucinationDetector()
        sentences = detector._split_sentences("")
        assert len(sentences) == 0

    def test_split_sentences_only_delimiters(self):
        detector = HallucinationDetector()
        sentences = detector._split_sentences("。！？；\n")
        assert len(sentences) == 0

    def test_check_rules_with_engine(self):
        detector = HallucinationDetector(auto_init=False)
        mock_engine = Mock()
        mock_engine.verify.return_value = Mock(passed=False, confidence=0.5)
        detector.set_rule_engine(mock_engine)
        score = detector._check_rules("测试文本")
        assert score == 0.8
        mock_engine.verify.assert_called_once_with("测试文本")

    def test_check_rules_passed(self):
        detector = HallucinationDetector(auto_init=False)
        mock_engine = Mock()
        mock_engine.verify.return_value = Mock(passed=True, confidence=0.8)
        detector.set_rule_engine(mock_engine)
        score = detector._check_rules("测试文本")
        assert abs(score - 0.2) < 0.001

    def test_check_consistency_with_checker(self):
        detector = HallucinationDetector(auto_init=False)
        mock_checker = Mock()
        mock_checker.batch_consistency.return_value = Mock(avg_similarity=0.7)
        detector.set_consistency_checker(mock_checker)
        score = detector._check_consistency("测试文本")
        assert abs(score - 0.3) < 0.001

    def test_check_trace_with_tracer(self):
        detector = HallucinationDetector(auto_init=False)
        mock_tracer = Mock()
        mock_tracer.query.return_value = Mock(matched_entry_ids=["source1"], coverage=0.6)
        detector.set_source_tracer(mock_tracer)
        score = detector._check_trace("测试文本")
        assert score == 0.4

    def test_check_trace_no_match(self):
        detector = HallucinationDetector(auto_init=False)
        mock_tracer = Mock()
        mock_tracer.query.return_value = Mock(matched_entry_ids=[], coverage=0.0)
        detector.set_source_tracer(mock_tracer)
        score = detector._check_trace("测试文本")
        assert score == 0.8

    def test_check_trace_segment(self):
        detector = HallucinationDetector(auto_init=False)
        mock_tracer = Mock()
        mock_tracer.query.return_value = Mock(matched_entry_ids=["s1"], coverage=0.5)
        detector.set_source_tracer(mock_tracer)
        result = detector._check_trace_segment("测试文本")
        assert "score" in result
        assert "sources" in result
        assert result["score"] == 0.5

    def test_check_consistency_segment(self):
        detector = HallucinationDetector(auto_init=False)
        mock_checker = Mock()
        mock_checker.batch_consistency.return_value = Mock(avg_similarity=0.8)
        detector.set_consistency_checker(mock_checker)
        score = detector._check_consistency_segment("测试文本")
        assert abs(score - 0.2) < 0.001

    def test_empty_text(self):
        detector = HallucinationDetector()
        result = detector.detect("")
        assert result.weighted_score >= 0

    def test_weighted_score_calculation(self):
        detector = HallucinationDetector(auto_init=False)
        mock_engine = Mock()
        mock_engine.verify.return_value = Mock(passed=True, confidence=0.9)
        detector.set_rule_engine(mock_engine)

        mock_checker = Mock()
        mock_checker.batch_consistency.return_value = Mock(avg_similarity=0.95)
        detector.set_consistency_checker(mock_checker)

        mock_tracer = Mock()
        mock_tracer.query.return_value = Mock(matched_entry_ids=["s1"], coverage=0.9)
        detector.set_source_tracer(mock_tracer)

        result = detector.detect("测试文本")
        expected_score = (0.1 * 0.4 + 0.05 * 0.3 + 0.1 * 0.3) / 1.0
        assert abs(result.weighted_score - expected_score) < 0.01
