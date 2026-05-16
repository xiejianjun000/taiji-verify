"""
Detection Layer - Taiji Verify Layer 2

包含：
- rule_engine: 规则引擎
- consistency: 自一致性检查
- source_tracer: 知识溯源
- hallucination_detector: 幻觉检测
- stream_guard: 流式守卫
- eco_rules: 生态环境规则
"""

from taiji_verify.detection.rule_engine import (
    Rule,
    RuleEngine,
    VerificationRule,
    VerificationResult,
    SymbolConsistencyResult,
    KnowledgeEntry,
    KnowledgeMatch,
)
from taiji_verify.detection.consistency import (
    SelfConsistencyChecker,
    SimilarityResult,
    SamplingConfig,
)
from taiji_verify.detection.source_tracer import (
    SourceTracer,
    TraceResult,
)
from taiji_verify.detection.hallucination_detector import (
    HallucinationDetector,
    RiskLevel,
    DetectionResult,
    SegmentResult,
)
from taiji_verify.detection.stream_guard import (
    StreamGuard,
    GuardConfig,
    GuardResult,
)
from taiji_verify.detection.eco_rules import (
    EcoRule,
    FakeStandardRule,
    TimeTravelRule,
    SelfContradictionRule,
    WrongLegalStatusRule,
    FakeHistoryRule,
    get_all_rules,
)

__all__ = [
    "Rule",
    "RuleEngine",
    "VerificationRule",
    "VerificationResult",
    "SymbolConsistencyResult",
    "KnowledgeEntry",
    "KnowledgeMatch",
    "SelfConsistencyChecker",
    "SimilarityResult",
    "SamplingConfig",
    "SourceTracer",
    "TraceResult",
    "HallucinationDetector",
    "RiskLevel",
    "DetectionResult",
    "SegmentResult",
    "StreamGuard",
    "GuardConfig",
    "GuardResult",
    "EcoRule",
    "FakeStandardRule",
    "TimeTravelRule",
    "SelfContradictionRule",
    "WrongLegalStatusRule",
    "FakeHistoryRule",
    "get_all_rules",
]
