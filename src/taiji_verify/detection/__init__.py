"""
Detection Layer - Taiji Verify Layer 2

包含：
- rule_engine: 规则引擎
- consistency: 自一致性检查
- source_tracer: 知识溯源
- hallucination_detector: 幻觉检测
- stream_guard: 流式守卫
- eco_rules: 生态环境规则
- attribution_verifier: 归因验证（SAA能力）
- cross_model_verifier: ARIS交叉模型验证器
- neural_symbolic: 神经符号双轨验证器
- rag_score: RAG质量评分器
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
from taiji_verify.detection.attribution_verifier import (
    AttributionVerifier,
    AttributionResult,
    AttributionLevel,
    StrictAttributedAccuracy,
    KnowledgeEntry as AttributionKnowledgeEntry,
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
    RuleEngine as EcoRuleEngine,
    get_all_rules,
    get_rules_by_dimension,
    get_rules_by_mode,
    get_statistics,
    get_rule_count,
)
from taiji_verify.detection.cross_model_verifier import (
    ModelProvider,
    MockProvider,
    DeepSeekProvider,
    QwenProvider,
    GLMProvider,
    CrossModelResult,
    CrossModelVerifier,
    CrossModelVerdict,
)
from taiji_verify.detection.neural_symbolic import (
    TrackType,
    TrackResult,
    DualTrackResult,
    NeuralSymbolicVerifier,
)
from taiji_verify.detection.rag_score import (
    RAGScoreDimension,
    RAGDimensionScore,
    RAGScoreResult,
    RAGScorer,
)

__all__ = [
    # Rule Engine
    "Rule",
    "RuleEngine",
    "VerificationRule",
    "VerificationResult",
    "SymbolConsistencyResult",
    "KnowledgeEntry",
    "KnowledgeMatch",
    # Consistency
    "SelfConsistencyChecker",
    "SimilarityResult",
    "SamplingConfig",
    # Source Tracer
    "SourceTracer",
    "TraceResult",
    # Attribution Verifier (SAA)
    "AttributionVerifier",
    "AttributionResult",
    "AttributionLevel",
    "StrictAttributedAccuracy",
    "AttributionKnowledgeEntry",
    # Hallucination Detector
    "HallucinationDetector",
    "RiskLevel",
    "DetectionResult",
    "SegmentResult",
    # Stream Guard
    "StreamGuard",
    "GuardConfig",
    "GuardResult",
    # Eco Rules
    "EcoRule",
    "EcoRuleEngine",
    "get_all_rules",
    "get_rules_by_dimension",
    "get_rules_by_mode",
    "get_statistics",
    "get_rule_count",
    # Cross Model Verifier (ARIS)
    "ModelProvider",
    "MockProvider",
    "DeepSeekProvider",
    "QwenProvider",
    "GLMProvider",
    "CrossModelResult",
    "CrossModelVerifier",
    "CrossModelVerdict",
    # Neural Symbolic
    "TrackType",
    "TrackResult",
    "DualTrackResult",
    "NeuralSymbolicVerifier",
    # RAG Score
    "RAGScoreDimension",
    "RAGDimensionScore",
    "RAGScoreResult",
    "RAGScorer",
]
