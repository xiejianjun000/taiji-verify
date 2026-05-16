"""
Hallucination Detector - 幻觉检测

真正串联内部模块:
- RuleEngine: 规则检查
- SelfConsistencyChecker: 一致性检查
- SourceTracer: 知识溯源

三检测器加权: 规则0.4+一致性0.3+溯源0.3，归一化
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from taiji_verify.detection.rule_engine import RuleEngine
    from taiji_verify.detection.consistency import SelfConsistencyChecker
    from taiji_verify.detection.source_tracer import SourceTracer


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
    rule_score: float = 0.0
    consistency_score: float = 0.0
    trace_score: float = 0.0


@dataclass
class DetectionResult:
    """检测结果"""

    weighted_score: float
    risk_level: RiskLevel
    details: dict = field(default_factory=dict)
    segments: list[SegmentResult] = field(default_factory=list)


class HallucinationDetector:
    """
    幻觉检测器 - 自动初始化内部模块

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
        auto_init: bool = True,
    ):
        self.rule_weight = rule_weight
        self.consistency_weight = consistency_weight
        self.trace_weight = trace_weight
        self.risk_threshold = risk_threshold

        if auto_init:
            self._init_default_modules()
        else:
            self._rule_engine = None
            self._consistency_checker = None
            self._source_tracer = None

    def _init_default_modules(self) -> None:
        """自动初始化默认模块"""
        from taiji_verify.detection.rule_engine import RuleEngine
        from taiji_verify.detection.consistency import SelfConsistencyChecker
        from taiji_verify.detection.source_tracer import SourceTracer

        self._rule_engine = RuleEngine()
        self._consistency_checker = SelfConsistencyChecker()
        self._source_tracer = SourceTracer()

    def set_rule_engine(self, engine: "RuleEngine") -> None:
        """注入RuleEngine"""
        self._rule_engine = engine

    def set_consistency_checker(self, checker: "SelfConsistencyChecker") -> None:
        """注入SelfConsistencyChecker"""
        self._consistency_checker = checker

    def set_source_tracer(self, tracer: "SourceTracer") -> None:
        """注入SourceTracer"""
        self._source_tracer = tracer

    def detect(self, text: str) -> DetectionResult:
        """检测幻觉"""
        rule_score = self._check_rules(text)
        consistency_score = self._check_consistency(text)
        trace_score = self._check_trace(text)

        total_weight = self.rule_weight + self.consistency_weight + self.trace_weight
        weighted_score = (
            rule_score * self.rule_weight
            + consistency_score * self.consistency_weight
            + trace_score * self.trace_weight
        ) / total_weight

        risk_level = self._compute_risk_level(weighted_score)

        return DetectionResult(
            weighted_score=weighted_score,
            risk_level=risk_level,
            details={
                "rule_score": rule_score,
                "consistency_score": consistency_score,
                "trace_score": trace_score,
                "weights": {
                    "rule": self.rule_weight,
                    "consistency": self.consistency_weight,
                    "trace": self.trace_weight,
                },
            },
        )

    def detect_segmented(self, text: str) -> DetectionResult:
        """分段检测幻觉"""
        segments = self._split_sentences(text)
        segment_results = []

        for segment in segments:
            if not segment.strip():
                continue

            rule_score = self._check_rules(segment)
            consistency_score = self._check_consistency_segment(segment)
            trace_result = self._check_trace_segment(segment)

            total_weight = self.rule_weight + self.consistency_weight + self.trace_weight
            score = (
                rule_score * self.rule_weight
                + consistency_score * self.consistency_weight
                + trace_result["score"] * self.trace_weight
            ) / total_weight

            is_hallucination = score > self.risk_threshold

            segment_results.append(
                SegmentResult(
                    text=segment,
                    is_hallucination=is_hallucination,
                    confidence=score,
                    matched_sources=trace_result["sources"],
                    rule_score=rule_score,
                    consistency_score=consistency_score,
                    trace_score=trace_result["score"],
                )
            )

        if not segment_results:
            return DetectionResult(weighted_score=0.0, risk_level=RiskLevel.LOW)

        avg_score = sum(r.confidence for r in segment_results) / len(segment_results)
        return DetectionResult(
            weighted_score=avg_score,
            risk_level=self._compute_risk_level(avg_score),
            segments=segment_results,
        )

    def _check_rules(self, text: str) -> float:
        """使用RuleEngine检查规则"""
        if self._rule_engine is not None:
            result = self._rule_engine.verify(text)
            if not result.passed:
                return 0.8
            return 1.0 - result.confidence

        suspicious_patterns = [
            r"GB\d{5,}",
            r"\d{4,}年\d{1,2}月",
            r"据.*报道",
            r"研究表明",
        ]
        import re

        for pattern in suspicious_patterns:
            if re.search(pattern, text):
                return 0.8
        return 0.2

    def _check_consistency(self, text: str) -> float:
        """使用SelfConsistencyChecker检查一致性"""
        if self._consistency_checker is not None:
            result = self._consistency_checker.batch_consistency([text, text])
            return 1.0 - result.avg_similarity

        contradictions = [
            ("是", "不是"),
            ("有", "没有"),
            ("可以", "不可以"),
        ]
        for pos, neg in contradictions:
            if pos in text and neg in text:
                return 0.7
        return 0.1

    def _check_consistency_segment(self, segment: str) -> float:
        """检查分段一致性"""
        if self._consistency_checker is not None:
            result = self._consistency_checker.batch_consistency([segment, segment])
            return 1.0 - result.avg_similarity

        return self._check_consistency(segment)

    def _check_trace(self, text: str) -> float:
        """使用SourceTracer检查溯源"""
        if self._source_tracer is not None:
            result = self._source_tracer.query(text)
            if result.matched_entry_ids:
                coverage = result.coverage
                return max(0.0, 1.0 - coverage)
            return 0.8

        return 0.3

    def _check_trace_segment(self, segment: str) -> dict:
        """检查分段溯源"""
        if self._source_tracer is not None:
            result = self._source_tracer.query(segment)
            if result.matched_entry_ids:
                return {
                    "score": max(0.0, 1.0 - result.coverage),
                    "sources": result.matched_entry_ids,
                }
            return {"score": 0.8, "sources": []}

        return {"score": 0.3, "sources": []}

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

        sentences = re.split(r"[。！？；\n]+", text)
        return [s.strip() for s in sentences if s.strip()]
