"""Hallucination Detector 测试 - Phase 2 升级版本"""
import pytest
from taiji_verify.detection.hallucination_detector import (
    HallucinationDetector, RiskLevel, DetectionResult, SegmentResult,
    HallucinationType, HallucinationEvidence,
)


class TestHallucinationDetectorInit:
    """幻觉检测器初始化测试"""

    def test_default_init(self):
        detector = HallucinationDetector()
        assert detector is not None
        assert detector.rule_weight == 0.4
        assert detector.consistency_weight == 0.3
        assert detector.trace_weight == 0.3

    def test_custom_weights(self):
        detector = HallucinationDetector(
            rule_weight=0.5,
            consistency_weight=0.3,
            trace_weight=0.2,
        )
        assert detector.rule_weight == 0.5
        assert detector.consistency_weight == 0.3
        assert detector.trace_weight == 0.2


class TestDetectionBasic:
    """基础检测功能测试"""

    def test_detect_with_weighted_score(self):
        detector = HallucinationDetector()
        text = "根据GB12345标准，环境质量应符合规定要求"
        result = detector.detect(text)
        assert hasattr(result, 'weighted_score')
        assert hasattr(result, 'risk_level')
        assert isinstance(result.risk_level, RiskLevel)

    def test_risk_level_threshold(self):
        detector = HallucinationDetector(risk_threshold=0.8)
        result = detector.detect("测试文本内容")
        assert isinstance(result.risk_level, RiskLevel)

    def test_segmented_detection(self):
        detector = HallucinationDetector()
        text = "第一句内容。第二句内容。第三句内容。"
        result = detector.detect_segmented(text)
        assert len(result.segments) >= 3


class TestHallucinationTypes:
    """8类幻觉分型测试"""

    def test_detect_factual_incorrectness(self):
        detector = HallucinationDetector()
        result = detector.detect("根据GB999999标准规定")
        assert HallucinationType.FACTUAL_INCORRECTNESS in result.detected_types

    def test_detect_contextual_inconsistency(self):
        detector = HallucinationDetector()
        long_text = "重复内容重复内容重复内容重复内容重复内容重复内容重复内容重复内容重复内容重复内容"
        result = detector.detect(long_text)
        assert HallucinationType.CONTEXTUAL_INCONSISTENCY in result.detected_types

    def test_detect_logical_contradiction(self):
        detector = HallucinationDetector()
        result = detector.detect("该物质有毒但也无害")
        assert HallucinationType.LOGICAL_CONTRADICTION in result.detected_types

    def test_detect_unverifiable_claim(self):
        detector = HallucinationDetector()
        result = detector.detect("专家认为这是正确的")
        assert HallucinationType.UNVERIFIABLE_CLAIM in result.detected_types

    def test_detect_misgrounding(self):
        detector = HallucinationDetector()
        references = ["GB12345规定企业应当减排"]
        result = detector.detect("根据GB12345规定，企业可以排放", references=references)
        assert HallucinationType.MISGROUNDING in result.detected_types

    def test_detect_semantic_distortion(self):
        detector = HallucinationDetector()
        result = detector.detect("应当禁止但允许排放")
        assert HallucinationType.SEMANTIC_DISTORTION in result.detected_types

    def test_detect_temporal_inconsistency(self):
        detector = HallucinationDetector()
        result = detector.detect("该法律将于2050年颁布")
        assert HallucinationType.TEMPORAL_INCONSISTENCY in result.detected_types

    def test_detect_circular_reasoning(self):
        detector = HallucinationDetector()
        result = detector.detect("因为A所以B，因为B所以A")
        assert HallucinationType.CIRCULAR_REASONING in result.detected_types


class TestMisgroundingDetection:
    """Misgrounding检测测试"""

    def test_misgrounding_with_references(self):
        detector = HallucinationDetector()
        references = ["GB12345规定企业应当减排"]
        result = detector.detect(
            "根据GB12345规定，企业可以自由排放",
            references=references
        )
        assert len(result.evidences) > 0
        assert any(e.hallucination_type == HallucinationType.MISGROUNDING for e in result.evidences)

    def test_no_misgrounding_valid(self):
        detector = HallucinationDetector()
        references = ["GB12345规定企业应当减排"]
        result = detector.detect(
            "根据GB12345规定，企业应当减排",
            references=references
        )
        assert HallucinationType.MISGROUNDING not in result.detected_types

    def test_misgrounding_negation(self):
        detector = HallucinationDetector()
        references = ["GB12345规定企业可以排放"]
        result = detector.detect(
            "根据GB12345规定，企业不得排放",
            references=references
        )
        assert HallucinationType.MISGROUNDING in result.detected_types


class TestDetectionResult:
    """检测结果测试"""

    def test_detection_result_structure(self):
        detector = HallucinationDetector()
        result = detector.detect("测试文本")
        assert isinstance(result, DetectionResult)
        assert hasattr(result, 'weighted_score')
        assert hasattr(result, 'risk_level')
        assert hasattr(result, 'details')
        assert hasattr(result, 'detected_types')
        assert hasattr(result, 'evidences')

    def test_segment_result_structure(self):
        detector = HallucinationDetector()
        result = detector.detect_segmented("测试文本")
        assert len(result.segments) > 0
        segment = result.segments[0]
        assert isinstance(segment, SegmentResult)
        assert hasattr(segment, 'text')
        assert hasattr(segment, 'is_hallucination')
        assert hasattr(segment, 'detected_types')
        assert hasattr(segment, 'evidences')


class TestRiskLevel:
    """风险等级测试"""

    def test_risk_level_low(self):
        detector = HallucinationDetector()
        result = detector.detect("正常的文本内容")
        assert result.risk_level == RiskLevel.LOW or result.risk_level == RiskLevel.MEDIUM

    def test_risk_level_high_with_hallucination(self):
        detector = HallucinationDetector()
        result = detector.detect("根据GB999999标准规定")
        assert HallucinationType.FACTUAL_INCORRECTNESS in result.detected_types
        assert len(result.evidences) > 0

    def test_risk_level_with_misgrounding(self):
        detector = HallucinationDetector()
        references = ["GB12345规定企业应当减排"]
        result = detector.detect(
            "根据GB12345规定，企业可以自由排放",
            references=references
        )
        assert HallucinationType.MISGROUNDING in result.detected_types
        assert len(result.evidences) >= 2


class TestHallucinationEvidence:
    """幻觉证据测试"""

    def test_evidence_creation(self):
        evidence = HallucinationEvidence(
            hallucination_type=HallucinationType.FACTUAL_INCORRECTNESS,
            confidence=0.9,
            description="测试证据",
        )
        assert evidence.hallucination_type == HallucinationType.FACTUAL_INCORRECTNESS
        assert evidence.confidence == 0.9
        assert evidence.description == "测试证据"

    def test_evidence_in_detection(self):
        detector = HallucinationDetector()
        result = detector.detect("根据GB999999标准规定")
        assert len(result.evidences) > 0
        evidence = result.evidences[0]
        assert isinstance(evidence, HallucinationEvidence)


class TestHallucinationSummary:
    """幻觉摘要测试"""

    def test_get_hallucination_summary(self):
        detector = HallucinationDetector()
        result = detector.detect("根据GB999999标准规定")
        summary = detector.get_hallucination_summary(result)
        assert 'risk_level' in summary
        assert 'score' in summary
        assert 'detected_types' in summary
        assert 'type_counts' in summary
        assert 'evidence_count' in summary

    def test_summary_with_multiple_types(self):
        detector = HallucinationDetector()
        references = ["GB12345规定企业应当减排"]
        result = detector.detect(
            "根据GB999999标准规定，企业可以自由排放",
            references=references
        )
        summary = detector.get_hallucination_summary(result)
        assert len(summary['detected_types']) >= 2


class TestSegmentedDetection:
    """分段检测测试"""

    def test_segmented_detection_multiple_sentences(self):
        detector = HallucinationDetector()
        text = "正常句子。根据GB999999标准规定。另一个正常句子。"
        result = detector.detect_segmented(text)
        assert len(result.segments) == 3
        assert any(s.is_hallucination for s in result.segments)

    def test_segmented_detection_with_references(self):
        detector = HallucinationDetector()
        references = ["GB12345规定企业应当减排"]
        text = "根据GB12345规定，企业可以排放。正常句子。"
        result = detector.detect_segmented(text, references=references)
        assert len(result.segments) == 2
        assert result.segments[0].is_hallucination is True


class TestHallucinationTypeValues:
    """幻觉类型枚举值测试"""

    def test_hallucination_type_values(self):
        assert HallucinationType.FACTUAL_INCORRECTNESS.value == "factual_incorrectness"
        assert HallucinationType.CONTEXTUAL_INCONSISTENCY.value == "contextual_inconsistency"
        assert HallucinationType.LOGICAL_CONTRADICTION.value == "logical_contradiction"
        assert HallucinationType.UNVERIFIABLE_CLAIM.value == "unverifiable_claim"
        assert HallucinationType.MISGROUNDING.value == "misgrounding"
        assert HallucinationType.SEMANTIC_DISTORTION.value == "semantic_distortion"
        assert HallucinationType.TEMPORAL_INCONSISTENCY.value == "temporal_inconsistency"
        assert HallucinationType.CIRCULAR_REASONING.value == "circular_reasoning"


class TestIntegration:
    """集成测试"""

    def test_detect_and_summary_workflow(self):
        detector = HallucinationDetector()
        result = detector.detect("根据GB999999标准规定")
        summary = detector.get_hallucination_summary(result)
        assert summary['evidence_count'] == len(result.evidences)

    def test_segmented_and_full_detection(self):
        detector = HallucinationDetector()
        text = "正常句子。根据GB999999标准规定。"
        full_result = detector.detect(text)
        segmented_result = detector.detect_segmented(text)
        
        assert full_result.weighted_score == pytest.approx(
            sum(s.confidence for s in segmented_result.segments) / len(segmented_result.segments),
            rel=0.1
        )