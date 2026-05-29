"""
Hallucination Detector - 幻觉检测

真正串联内部模块:
- RuleEngine: 规则检查
- SelfConsistencyChecker: 一致性检查
- SourceTracer: 知识溯源

三检测器加权: 规则0.4+一致性0.3+溯源0.3，归一化

Phase 2 升级：
- 8类幻觉分型器
- Misgrounding检测（引用正确但解读错误）
- 更精细的风险评估
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Optional, List

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


class HallucinationType(str, Enum):
    """8类幻觉分型"""

    FACTUAL_INCORRECTNESS = "factual_incorrectness"
    CONTEXTUAL_INCONSISTENCY = "contextual_inconsistency"
    LOGICAL_CONTRADICTION = "logical_contradiction"
    UNVERIFIABLE_CLAIM = "unverifiable_claim"
    MISGROUNDING = "misgrounding"
    SEMANTIC_DISTORTION = "semantic_distortion"
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"
    CIRCULAR_REASONING = "circular_reasoning"


@dataclass
class HallucinationEvidence:
    """幻觉证据"""

    hallucination_type: HallucinationType
    confidence: float
    description: str
    position: Optional[int] = None
    supporting_details: dict = field(default_factory=dict)


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
    detected_types: list[HallucinationType] = field(default_factory=list)
    evidences: list[HallucinationEvidence] = field(default_factory=list)


@dataclass
class DetectionResult:
    """检测结果"""

    weighted_score: float
    risk_level: RiskLevel
    details: dict = field(default_factory=dict)
    segments: list[SegmentResult] = field(default_factory=list)
    detected_types: list[HallucinationType] = field(default_factory=list)
    evidences: list[HallucinationEvidence] = field(default_factory=list)


class HallucinationDetector:
    """
    幻觉检测器 - Phase 2 升级版本

    8类幻觉分型:
    1. FACTUAL_INCORRECTNESS - 事实错误
    2. CONTEXTUAL_INCONSISTENCY - 上下文不一致
    3. LOGICAL_CONTRADICTION - 逻辑矛盾
    4. UNVERIFIABLE_CLAIM - 无法验证的断言
    5. MISGROUNDING - 错误接地（引用正确但解读错误）
    6. SEMANTIC_DISTORTION - 语义扭曲
    7. TEMPORAL_INCONSISTENCY - 时间不一致
    8. CIRCULAR_REASONING - 循环论证

    Usage::
        detector = HallucinationDetector()
        result = detector.detect("根据GB12345标准规定...")
        print(result.risk_level, result.weighted_score)
        
        # 获取检测到的幻觉类型
        for evidence in result.evidences:
            print(evidence.hallucination_type, evidence.description)
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

        self._setup_hallucination_patterns()

    def _setup_hallucination_patterns(self) -> None:
        """设置幻觉检测模式"""
        self.FACTUAL_PATTERNS = [
            (r"GB\d{5,}", "虚假标准编号"),
            (r"根据内部知识", "无来源引用"),
            (r"研究表明[^。！？]*$", "无具体研究来源"),
        ]

        self.CONTRADICTION_PAIRS = [
            ("是", "不是"),
            ("有", "没有"),
            ("可以", "不可以"),
            ("应该", "不应该"),
            ("必须", "不必"),
            ("需要", "无需"),
            ("禁止", "允许"),
            ("不得", "可以"),
        ]

        self.TEMPORAL_PATTERNS = [
            (r"205[0-9]年", "未来年份"),
            (r"204[0-9]年", "未来年份"),
            (r"将于(\d{4})年", "未来计划"),
        ]

        self.MISGROUNDING_PATTERNS = [
            ("根据", "但"),
            ("依据", "然而"),
            ("规定", "可以"),
        ]

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

    def detect(self, text: str, references: Optional[List[str]] = None) -> DetectionResult:
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

        detected_types, evidences = self._detect_hallucination_types(text, references)

        risk_level = self._compute_risk_level(weighted_score, detected_types)

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
            detected_types=detected_types,
            evidences=evidences,
        )

    def detect_segmented(self, text: str, references: Optional[List[str]] = None) -> DetectionResult:
        """分段检测幻觉"""
        segments = self._split_sentences(text)
        segment_results = []
        all_detected_types = []
        all_evidences = []

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

            detected_types, evidences = self._detect_hallucination_types(segment, references)
            all_detected_types.extend(detected_types)
            all_evidences.extend(evidences)

            is_hallucination = score > self.risk_threshold or len(detected_types) > 0

            segment_results.append(
                SegmentResult(
                    text=segment,
                    is_hallucination=is_hallucination,
                    confidence=score,
                    matched_sources=trace_result["sources"],
                    rule_score=rule_score,
                    consistency_score=consistency_score,
                    trace_score=trace_result["score"],
                    detected_types=detected_types,
                    evidences=evidences,
                )
            )

        if not segment_results:
            return DetectionResult(weighted_score=0.0, risk_level=RiskLevel.LOW)

        avg_score = sum(r.confidence for r in segment_results) / len(segment_results)
        risk_level = self._compute_risk_level(avg_score, all_detected_types)

        return DetectionResult(
            weighted_score=avg_score,
            risk_level=risk_level,
            segments=segment_results,
            detected_types=list(set(all_detected_types)),
            evidences=all_evidences,
        )

    def _detect_hallucination_types(self, text: str, references: Optional[List[str]] = None) -> tuple[list[HallucinationType], list[HallucinationEvidence]]:
        """检测8类幻觉类型"""
        detected_types = []
        evidences = []

        if not text:
            return detected_types, evidences

        # 1. FACTUAL_INCORRECTNESS - 事实错误
        for pattern, desc in self.FACTUAL_PATTERNS:
            import re
            if re.search(pattern, text):
                detected_types.append(HallucinationType.FACTUAL_INCORRECTNESS)
                evidences.append(HallucinationEvidence(
                    hallucination_type=HallucinationType.FACTUAL_INCORRECTNESS,
                    confidence=0.9,
                    description=f"检测到{desc}: {pattern}",
                ))
                break

        # 2. CONTEXTUAL_INCONSISTENCY - 上下文不一致
        if len(text) > 30:
            chunks = [text[i:i+10] for i in range(0, len(text), 10)]
            unique_chunks = set(chunks)
            if len(unique_chunks) <= len(chunks) // 2:
                detected_types.append(HallucinationType.CONTEXTUAL_INCONSISTENCY)
                evidences.append(HallucinationEvidence(
                    hallucination_type=HallucinationType.CONTEXTUAL_INCONSISTENCY,
                    confidence=0.7,
                    description="文本存在重复或不一致的上下文",
                ))

        # 3. LOGICAL_CONTRADICTION - 逻辑矛盾
        contradiction_pairs = self.CONTRADICTION_PAIRS + [
            ("有害", "无害"),
            ("有毒", "无害"),
        ]
        for pos, neg in contradiction_pairs:
            if pos in text and neg in text:
                detected_types.append(HallucinationType.LOGICAL_CONTRADICTION)
                evidences.append(HallucinationEvidence(
                    hallucination_type=HallucinationType.LOGICAL_CONTRADICTION,
                    confidence=0.85,
                    description=f"检测到矛盾对: '{pos}' 和 '{neg}'",
                ))
                break

        # 4. UNVERIFIABLE_CLAIM - 无法验证的断言
        claim_keywords = ["专家认为", "数据显示", "研究表明", "众所周知", "显然"]
        has_claim = any(kw in text for kw in claim_keywords)
        has_source = any(kw in text for kw in ["根据", "依据", "参考", "来源"])
        if has_claim and not has_source:
            detected_types.append(HallucinationType.UNVERIFIABLE_CLAIM)
            evidences.append(HallucinationEvidence(
                hallucination_type=HallucinationType.UNVERIFIABLE_CLAIM,
                confidence=0.75,
                description="存在无法验证的断言，缺少引用来源",
            ))

        # 5. MISGROUNDING - 错误接地
        if references:
            for ref in references:
                misgrounding = self._detect_misgrounding(text, ref)
                if misgrounding["detected"]:
                    detected_types.append(HallucinationType.MISGROUNDING)
                    evidences.append(HallucinationEvidence(
                        hallucination_type=HallucinationType.MISGROUNDING,
                        confidence=misgrounding["confidence"],
                        description=f"Misgrounding: {misgrounding['reason']}",
                        supporting_details={"reference": ref[:50] + "..." if len(ref) > 50 else ref},
                    ))

        # 6. SEMANTIC_DISTORTION - 语义扭曲
        text_lower = text.lower()
        distortion_patterns = [
            (("应当", "可以"), "语气弱化"),
            (("可以", "应当"), "语气强化"),
            (("禁止", "允许"), "语义反转"),
            (("允许", "禁止"), "语义反转"),
        ]
        for (original, distorted), desc in distortion_patterns:
            if original in text_lower and distorted in text_lower:
                detected_types.append(HallucinationType.SEMANTIC_DISTORTION)
                evidences.append(HallucinationEvidence(
                    hallucination_type=HallucinationType.SEMANTIC_DISTORTION,
                    confidence=0.8,
                    description=f"语义扭曲: {desc}",
                ))
                break

        # 7. TEMPORAL_INCONSISTENCY - 时间不一致
        import re
        from datetime import datetime
        current_year = datetime.now().year
        for pattern, desc in self.TEMPORAL_PATTERNS:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if groups and groups[0]:
                    try:
                        year = int(groups[0])
                        if year > current_year + 5:
                            detected_types.append(HallucinationType.TEMPORAL_INCONSISTENCY)
                            evidences.append(HallucinationEvidence(
                                hallucination_type=HallucinationType.TEMPORAL_INCONSISTENCY,
                                confidence=0.9,
                                description=f"时间不一致: 引用未来年份{year}",
                            ))
                    except ValueError:
                        pass
                else:
                    detected_types.append(HallucinationType.TEMPORAL_INCONSISTENCY)
                    evidences.append(HallucinationEvidence(
                        hallucination_type=HallucinationType.TEMPORAL_INCONSISTENCY,
                        confidence=0.85,
                        description=f"时间不一致: {desc}",
                    ))
                break

        # 8. CIRCULAR_REASONING - 循环论证
        circular_patterns = ["因为.*所以.*因为", "结论是.*因为.*结论"]
        for pattern in circular_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected_types.append(HallucinationType.CIRCULAR_REASONING)
                evidences.append(HallucinationEvidence(
                    hallucination_type=HallucinationType.CIRCULAR_REASONING,
                    confidence=0.8,
                    description="检测到循环论证模式",
                ))
                break

        return list(set(detected_types)), evidences

    def _detect_misgrounding(self, claim: str, reference: str) -> dict:
        """检测Misgrounding（错误接地）"""
        claim_lower = claim.lower()
        ref_lower = reference.lower()

        detected = False
        confidence = 0.0
        reason = ""

        citation_terms = ["根据", "依据", "规定", "条款", "GB", "标准"]
        has_citation = any(term in claim_lower for term in citation_terms)

        if has_citation:
            if "不" in claim_lower and "不" not in ref_lower:
                detected = True
                confidence += 0.4
                reason = "结论包含否定词，但引用原文中没有"

            if "可以" in claim_lower and "应当" in ref_lower:
                detected = True
                confidence += 0.3
                reason = "结论使用'可以'但原文使用'应当'，语气弱化"

            if "应当" in claim_lower and "可以" in ref_lower:
                detected = True
                confidence += 0.3
                reason = "结论使用'应当'但原文使用'可以'，语气强化"

        return {
            "detected": detected,
            "confidence": min(1.0, confidence),
            "reason": reason if reason else "未检测到Misgrounding",
        }

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

    def _compute_risk_level(self, score: float, detected_types: list[HallucinationType]) -> RiskLevel:
        """计算风险等级（考虑幻觉类型）"""
        base_risk = score

        for h_type in detected_types:
            if h_type == HallucinationType.MISGROUNDING:
                base_risk += 0.1
            elif h_type == HallucinationType.LOGICAL_CONTRADICTION:
                base_risk += 0.1
            elif h_type == HallucinationType.FACTUAL_INCORRECTNESS:
                base_risk += 0.05

        base_risk = min(1.0, base_risk)

        if base_risk < 0.3:
            return RiskLevel.LOW
        elif base_risk < 0.5:
            return RiskLevel.MEDIUM
        elif base_risk < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def _split_sentences(self, text: str) -> list[str]:
        """分割句子"""
        import re

        sentences = re.split(r"[。！？；\n]+", text)
        return [s.strip() for s in sentences if s.strip()]

    def get_hallucination_summary(self, result: DetectionResult) -> dict:
        """获取幻觉检测摘要"""
        type_counts = {}
        for h_type in result.detected_types:
            type_counts[h_type.value] = type_counts.get(h_type.value, 0) + 1

        return {
            "risk_level": result.risk_level.value,
            "score": result.weighted_score,
            "detected_types": list(type_counts.keys()),
            "type_counts": type_counts,
            "evidence_count": len(result.evidences),
        }