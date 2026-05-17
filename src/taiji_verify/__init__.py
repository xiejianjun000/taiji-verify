"""
Taiji Verify 模块 - 太极验证系统

包含：
- delta_s: 阴阳距计算 (Delta S)
- kun_guard: 坤守 - 语义残差修正
- qian_advance: 乾进 - 语义演进建模
- fu_return: 复归 - 崩溃逆转
- xun_tune: 巽调 - 注意力调节
- guan_observe: 观变 - 状态追踪
- polaris: 北辰编译器 - 目标编译器
- symptom_map: 病候图 - 16种失败模式检测
- engine: 太极验证主引擎
- failure_modes: 失败模式检测器
"""

from taiji_verify.delta_s import (
    DeltaSCalculator,
    DeltaSResult,
    GateZone,
    AnchorExtension,
)
from taiji_verify.kun_guard import (
    KunGuard,
    KunGuardResult,
    HazardLevel,
    KnowledgeAnchor,
)
from taiji_verify.qian_advance import (
    QianAdvance,
    QianAdvanceResult,
    PerturbationResult,
)
from taiji_verify.fu_return import (
    FuReturn,
    RecoveryResult,
    RecoveryState,
    CrashingEvent,
)
from taiji_verify.xun_tune import (
    XunTune,
    AttentionModulation,
    TunedOutput,
)
from taiji_verify.guan_observe import (
    GuanObserve,
    StateSnapshot,
    TrendAnalysis,
    AnomalyEvent,
    ChangeType,
)
from taiji_verify.polaris import (
    PolarisCompiler,
    TaskAtom,
    TaskState,
    TaskType,
    ExecutionToken,
    RoundLock,
    ClosureRecord,
    CompilationResult,
)
from taiji_verify.symptom_map import (
    SymptomMap,
    FailurePattern,
    FailureLevel,
    FailureDetection,
    DetectionResult,
    Detector,
)
from taiji_verify.failure_modes import (
    FailureModeDetector,
    FailureMode,
    FailureSeverity,
)
from taiji_verify.engine import (
    TaijiVerifyEngine,
    VerificationRequest,
    VerificationResponse,
    Verdict,
)
from taiji_verify.plugin import (
    verify,
    verify_async,
    batch_verify,
    TaijiVerify,
    VerifyResult,
)

__all__ = [
    # Delta S (阴阳距)
    "DeltaSCalculator",
    "DeltaSResult",
    "GateZone",
    "AnchorExtension",
    # Kun Guard (坤守)
    "KunGuard",
    "KunGuardResult",
    "HazardLevel",
    "KnowledgeAnchor",
    "ResidualCorrection",
    # Qian Advance (乾进)
    "QianAdvance",
    "QianAdvanceResult",
    "PerturbationResult",
    "StabilityScore",
    # Fu Return (复归)
    "FuReturn",
    "RecoveryResult",
    "RecoveryState",
    "CrashingEvent",
    "CollapseState",
    # Xun Tune (巽调)
    "XunTune",
    "AttentionModulation",
    "TunedOutput",
    # Guan Observe (观变)
    "GuanObserve",
    "StateSnapshot",
    "TrendAnalysis",
    "AnomalyEvent",
    "ChangeType",
    "ObservedState",
    # Polaris Compiler (北辰编译器)
    "PolarisCompiler",
    "TaskAtom",
    "TaskState",
    "TaskType",
    "AtomType",
    "ExecutionToken",
    "RoundLock",
    "ClosureRecord",
    "CompilationResult",
    # Symptom Map (病候图)
    "SymptomMap",
    "FailureSymptom",
    "FailurePattern",
    "FailureLevel",
    "FailureDetection",
    "DetectionResult",
    "Detector",
    "SymptomType",
    # Failure Modes (失败模式)
    "FailureModeDetector",
    "FailureMode",
    "FailureSeverity",
    # Engine (引擎)
    "TaijiVerifyEngine",
    "VerificationRequest",
    "VerificationResponse",
    "Verdict",
    # Plugin SDK (一行验证)
    "verify",
    "verify_async",
    "batch_verify",
    "TaijiVerify",
    "VerifyResult",
]
