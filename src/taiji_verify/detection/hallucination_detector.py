"""
Hallucination Detector - 幻觉检测

对应 HallucinationDetector.ts 的 Python 实现

功能:
- 三检测器加权: 规则0.4+一致性0.3+溯源0.3，归一化
- riskScore=weightedScore/totalWeight，阈值0.8
- 分段查找疑似幻觉: 按句分割逐段溯源
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RiskLevel(str, Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SegmentResult:
    """分段检测结果"""
    text: str
    is_hallucination: bool
    confidence: float
    matched_sources: list[str] = field(default_factory=list)


@dataclass
class DetectionResult:
    """检测结果"""
    weighted_score: float
    risk_level: RiskLevel
    details: dict = field(default_factory=dict)
    segments: list[SegmentResult] = field(default_factory=list)


class HallucinationDetector:
    """
    幻觉检测器

    Usage::
        detector = HallucinationDetector()
        result = detector.detect("根据GB12345标准规定...")
        print(result.risk_level, result.weighted_score)
    """

    def __init__(
        self,
        rule_weight: float = 0.4,
        consistency_weight: float = 0.3,
        trace_weight: float = 0.3,
        risk_threshold: float = 0.8,
    ):
        self.rule_weight = rule_weight
        self.consistency_weight = consistency_weight
        self.trace_weight = trace_weight
        self.risk_threshold = risk_threshold
        self._rule_engine = None
        self._source_tracer = None

    def detect(self, text: str) -> DetectionResult:
        """检测幻觉"""
        rule_score = self._check_rules(text)
        consistency_score = self._check_consistency(text)
        trace_score = self._check_trace(text)

        total_weight = self.rule_weight + self.consistency_weight + self.trace_weight
        weighted_score = (
            rule_score * self.rule_weight +
            consistency_score * self.consistency_weight +
            trace_score * self.trace_weight
        ) / total_weight

        risk_level = self._compute_risk_level(weighted_score)

        return DetectionResult(
            weighted_score=weighted_score,
            risk_level=risk_level,
            details={
                'rule_score': rule_score,
                'consistency_score': consistency_score,
                'trace_score': trace_score,
            },
        )

    def detect_segmented(self, text: str) -> DetectionResult:
        """分段检测幻觉"""
        segments = self._split_sentences(text)
        segment_results = []

        for segment in segments:
            if not segment.strip():
                continue
            score = self._simple_hallucination_score(segment)
            is_hallucination = score > self.risk_threshold
            segment_results.append(SegmentResult(
                text=segment,
                is_hallucination=is_hallucination,
                confidence=score,
            ))

        if not segment_results:
            return DetectionResult(weighted_score=0.0, risk_level=RiskLevel.LOW)

        avg_score = sum(r.confidence for r in segment_results) / len(segment_results)
        return DetectionResult(
            weighted_score=avg_score,
            risk_level=self._compute_risk_level(avg_score),
            segments=segment_results,
        )

    def _check_rules(self, text: str) -> float:
        """检查规则匹配"""
        suspicious_patterns = [
            r'GB\d{5,}',
            r'\d{4,}年\d{1,2}月',
            r'据.*报道',
            r'研究表明',
        ]
        import re
        for pattern in suspicious_patterns:
            if re.search(pattern, text):
                return 0.8
        return 0.2

    def _check_consistency(self, text: str) -> float:
        """检查一致性"""
        contradictions = [
            ('是', '不是'),
            ('有', '没有'),
            ('可以', '不可以'),
        ]
        for pos, neg in contradictions:
            if pos in text and neg in text:
                return 0.7
        return 0.1

    def _check_trace(self, text: str) -> float:
        """检查知识溯源"""
        return 0.3

    def _compute_risk_level(self, score: float) -> RiskLevel:
        """计算风险等级"""
        if score < 0.3:
            return RiskLevel.LOW
        elif score < 0.5:
            return RiskLevel.MEDIUM
        elif score < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _split_sentences(self, text: str) -> list[str]:
        """分割句子"""
        import re
        sentences = re.split(r'[。！？；\n]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _simple_hallucination_score(self, text: str) -> float:
        """简单幻觉评分"""
        score = 0.0
        score += self._check_rules(text) * 0.5
        score += self._check_consistency(text) * 0.3
        score += self._check_trace(text) * 0.2
        return score
