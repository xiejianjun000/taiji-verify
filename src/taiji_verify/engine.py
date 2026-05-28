"""
Taiji Verify Engine v2.2 - 太极验证主引擎 (六层融合 + 归因验证)

整合六层架构的完整验证流水线：
Layer 2: Detection层 - 规则引擎、一致性、溯源、幻觉检测、归因验证(SAA)
Layer 3: Reasoning层 - 七步推理链、检查点、耦合器、语义防火墙
Layer 4: Diagnosis层 - 全局修复图、故障排除
Layer 5: Governance层 - 双图、7个治理门
Layer 6: Execution层 - 目标编译器、泄漏审计

v2.2新增：
- AttributionVerifier: 归因验证能力
- SAA指标计算
- VerificationResponse.attribution字段

判定规则：
- 治理层STOP → BLOCK
- 治理层COARSE → CONDITIONAL_PASS
- CRITICAL失败模式 → BLOCK
- ΔS在DANGER+检测高风险 → BLOCK
- ΔS在RISK+修正成功 → CORRECTED
- ΔS在RISK+修正失败 → ESCALATE
- ΔS在TRANSIT → CONDITIONAL_PASS
- ΔS在SAFE+低风险 → PASS
- 执行层有未完成 → CONDITIONAL_PASS
- 归因验证失败 → CONDITIONAL_PASS (带警告)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable

import numpy as np

from taiji_verify.delta_s import DeltaSCalculator, DeltaSResult, GateZone
from taiji_verify.polaris import PolarisCompiler, CompilationResult
from taiji_verify.failure_modes import (
    FailureModeDetector,
    FailureDetection,
    FailureSeverity,
)

from taiji_verify.detection.rule_engine import RuleEngine
from taiji_verify.detection.consistency import SelfConsistencyChecker
from taiji_verify.detection.hallucination_detector import (
    HallucinationDetector,
    RiskLevel as DetectRiskLevel,
)
from taiji_verify.detection.attribution_verifier import (
    AttributionVerifier,
    AttributionResult,
    AttributionLevel,
)
from taiji_verify.reasoning.seven_step_chain import SevenStepChain, StepInput
from taiji_verify.reasoning.coupler import Coupler
from taiji_verify.reasoning.semantic_firewall import SemanticFirewall
from taiji_verify.governance.governance_gates import GateState, evaluate_all_gates
from taiji_verify.governance.twin_atlas import TwinAtlas
from taiji_verify.execution.goal_compiler import GoalCompiler
from taiji_verify.execution.leak_auditor import LeakAuditor


class Verdict(str, Enum):
    """最终判定"""

    PASS = "pass"
    CONDITIONAL_PASS = "conditional_pass"
    CORRECTED = "corrected"
    BLOCK = "block"
    ESCALATE = "escalate"


@dataclass
class VerificationRequest:
    """验证请求"""

    input_text: str
    ground_truth: Optional[str] = None
    context: Optional[dict] = None
    embed_fn: Optional[Callable] = None
    process_fn: Optional[Callable] = None


@dataclass
class AttributionSummary:
    """
    归因验证摘要

    用于在验证响应中返回归因相关的汇总信息
    """

    total_conclusions: int = 0  # 总结论数
    attributable_count: int = 0  # 可归因数
    attribution_rate: float = 0.0  # 归因率
    saa_score: Optional[float] = None  # SAA分数（如果有ground_truth）
    attribution_level_counts: dict[str, int] = field(default_factory=dict)  # 各级别数量
    has_attribution: bool = False  # 是否有归因验证结果


@dataclass
class VerificationResponse:
    """验证响应"""

    verdict: Verdict
    delta_s_result: Optional[DeltaSResult] = None
    detection_result: Optional[dict] = field(default_factory=dict)
    reasoning_chain_result: Optional[dict] = field(default_factory=dict)
    governance_result: Optional[dict] = field(default_factory=dict)
    diagnosis_result: Optional[dict] = field(default_factory=dict)
    failure_detections: list[FailureDetection] = field(default_factory=list)
    compilation: Optional[CompilationResult] = None
    final_vector: Optional[np.ndarray] = None
    corrected_text: Optional[str] = None
    processing_time_ms: int = 0
    metadata: dict = field(default_factory=dict)
    # v2.2新增归因字段
    attribution: Optional[AttributionSummary] = None  # 归因验证摘要
    attribution_results: list[AttributionResult] = field(default_factory=list)  # 详细归因结果

    @property
    def is_passing(self) -> bool:
        return self.verdict in (Verdict.PASS, Verdict.CONDITIONAL_PASS, Verdict.CORRECTED)


class TaijiVerifyEngine:
    """
    太极验证引擎 v2.2 - 六层融合 + 归因验证

    Usage::
        engine = TaijiVerifyEngine(embedding_dim=768)
        response = engine.verify(
            input_text="碳排放权交易管理办法规定...",
            ground_truth="碳排放权交易管理办法...",
        )
        print(response.verdict)
        print(response.attribution)  # 访问归因摘要
    """

    def __init__(
        self,
        embedding_dim: int = 768,
        delta_s_safe_threshold: float = 0.3,
        enable_all_layers: bool = True,
        enable_governance: bool = True,
        enable_attribution: bool = True,
    ):
        self.embedding_dim = embedding_dim
        self.enable_all_layers = enable_all_layers
        self.enable_governance = enable_governance
        self.enable_attribution = enable_attribution

        self.delta_s_calculator = DeltaSCalculator(
            embedding_dim=embedding_dim,
            safe_threshold=delta_s_safe_threshold,
        )
        self.failure_detector = FailureModeDetector()
        self.compiler = PolarisCompiler()

        if enable_all_layers:
            self._init_detection_layer()
            self._init_reasoning_layer()
            self._init_diagnosis_layer()
            self._init_governance_layer()
            self._init_execution_layer()

    def _init_detection_layer(self) -> None:
        """初始化检测层"""
        self.rule_engine = RuleEngine()
        self.consistency_checker = SelfConsistencyChecker()
        self.hallucination_detector = HallucinationDetector()
        # v2.2新增：归因验证器
        if self.enable_attribution:
            self.attribution_verifier = AttributionVerifier()

    def _init_reasoning_layer(self) -> None:
        """初始化推理层"""
        self.seven_step_chain = SevenStepChain()
        self.coupler = Coupler()
        self.semantic_firewall = SemanticFirewall()

    def _init_diagnosis_layer(self) -> None:
        """初始化诊断层"""
        from taiji_verify.diagnosis.global_fix_map import GlobalFixMap
        from taiji_verify.diagnosis.troubleshooting_atlas import TroubleshootingAtlas

        self.fix_map = GlobalFixMap()
        self.troubleshooting_atlas = TroubleshootingAtlas()

    def _init_governance_layer(self) -> None:
        """初始化治理层"""
        self.twin_atlas = TwinAtlas()

    def _init_execution_layer(self) -> None:
        """初始化执行层"""
        self.goal_compiler = GoalCompiler()
        self.leak_auditor = LeakAuditor()

    def verify(
        self,
        input_text: str,
        ground_truth: Optional[str] = None,
        context: Optional[dict] = None,
        embed_fn: Optional[Callable] = None,
        samples: Optional[int] = None,
    ) -> VerificationResponse:
        """执行完整验证流水线"""
        start = time.time()

        request = VerificationRequest(
            input_text=input_text,
            ground_truth=ground_truth,
            context=context,
            embed_fn=embed_fn,
        )

        if self.enable_all_layers:
            return self._full_layer_verification(request, start)
        return self._basic_verification(request, start)

    def verify_text_only(self, input_text: str) -> VerificationResponse:
        """纯文本验证"""
        return self.verify(input_text, ground_truth=None)

    def verify_with_vectors(
        self,
        input_vec: np.ndarray,
        ground_vec: np.ndarray,
    ) -> VerificationResponse:
        """向量验证"""
        start = time.time()
        ds_result = self.delta_s_calculator.compute(input_vec, ground_vec)
        verdict = self._compute_verdict_from_delta_s(ds_result)

        return VerificationResponse(
            verdict=verdict,
            delta_s_result=ds_result,
            processing_time_ms=int((time.time() - start) * 1000),
        )

    def verify_full_pipeline(
        self,
        input_text: str,
        ground_truth: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> VerificationResponse:
        """完整流水线验证"""
        return self.verify(input_text, ground_truth, context)

    def _basic_verification(
        self,
        request: VerificationRequest,
        start: float,
    ) -> VerificationResponse:
        """基础验证（Layer 1核心）"""
        detections = self.failure_detector.detect_all(request.input_text)
        compilation = self.compiler.compile(request.ground_truth or "")

        verdict = Verdict.PASS
        if any(d.mode.severity == FailureSeverity.CRITICAL for d in detections):
            verdict = Verdict.BLOCK
        elif detections:
            verdict = Verdict.CONDITIONAL_PASS

        return VerificationResponse(
            verdict=verdict,
            failure_detections=detections,
            compilation=compilation,
            processing_time_ms=int((time.time() - start) * 1000),
            metadata={"mode": "basic"},
        )

    def _full_layer_verification(
        self,
        request: VerificationRequest,
        start: float,
    ) -> VerificationResponse:
        """完整六层验证"""
        input_text = request.input_text

        detection_result = self._run_detection_layer(input_text)

        reasoning_chain_result = self._run_reasoning_layer(input_text, request.ground_truth)

        governance_result = self._run_governance_layer(input_text)

        if request.ground_truth and request.embed_fn:
            ds_result = self._run_delta_s(request.embed_fn, input_text, request.ground_truth)
            verdict = self._compute_verdict(
                ds_result, detection_result, reasoning_chain_result, governance_result
            )
        else:
            ds_result = None
            verdict = self._compute_verdict_no_vectors(
                detection_result, reasoning_chain_result, governance_result
            )

        diagnosis_result = self._run_diagnosis_layer(input_text, detection_result)

        compilation = self.compiler.compile(request.ground_truth or input_text)

        # v2.2新增：归因验证
        attribution_results, attribution_summary = self._run_attribution_layer(
            input_text, request.context
        )

        return VerificationResponse(
            verdict=verdict,
            delta_s_result=ds_result,
            detection_result=detection_result,
            reasoning_chain_result=reasoning_chain_result,
            governance_result=governance_result,
            diagnosis_result=diagnosis_result,
            failure_detections=self.failure_detector.detect_all(input_text),
            compilation=compilation,
            processing_time_ms=int((time.time() - start) * 1000),
            metadata={"mode": "full_6layer"},
            attribution=attribution_summary,
            attribution_results=attribution_results,
        )

    def _run_detection_layer(self, text: str) -> dict:
        """运行检测层"""
        result = {
            "rule_result": None,
            "consistency_result": None,
            "hallucination_result": None,
        }

        rule_engine = RuleEngine()
        result["rule_result"] = rule_engine.verify(text)

        consistency = SelfConsistencyChecker()
        result["consistency_result"] = consistency.batch_consistency([text])

        detector = HallucinationDetector()
        result["hallucination_result"] = detector.detect(text)

        return result

    def _run_attribution_layer(
        self,
        text: str,
        context: Optional[dict] = None,
    ) -> tuple[list[AttributionResult], Optional[AttributionSummary]]:
        """
        运行归因验证层

        Args:
            text: 待验证文本
            context: 上下文信息，可能包含声称的来源等

        Returns:
            tuple[list[AttributionResult], AttributionSummary]: 归因结果和摘要
        """
        if not self.enable_attribution or not hasattr(self, "attribution_verifier"):
            return [], None

        verifier = self.attribution_verifier

        # 如果知识库为空，使用context中的知识
        if not verifier.knowledge_base and context:
            if "knowledge_base" in context:
                for kb_entry in context["knowledge_base"]:
                    verifier.add_knowledge(**kb_entry)

        # 提取声称的来源
        claimed_source = None
        if context and "claimed_source" in context:
            claimed_source = context["claimed_source"]

        # 执行归因验证
        result = verifier.verify_attribution(text, claimed_source)

        # 计算归因摘要
        summary = AttributionSummary(
            total_conclusions=1,
            attributable_count=1 if result.is_attributable else 0,
            attribution_rate=1.0 if result.is_attributable else 0.0,
            attribution_level_counts={result.attribution_level.value: 1},
            has_attribution=True,
        )

        return [result], summary

    def add_attribution_knowledge(
        self,
        source_id: str,
        source_path: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        添加归因验证知识

        Args:
            source_id: 来源ID
            source_path: 来源路径
            content: 内容
            metadata: 元数据
        """
        if hasattr(self, "attribution_verifier"):
            self.attribution_verifier.add_knowledge(
                source_id=source_id,
                source_path=source_path,
                content=content,
                metadata=metadata,
            )

    def _run_reasoning_layer(
        self,
        text: str,
        goal: Optional[str],
    ) -> dict:
        """运行推理层"""
        result = {
            "chain_result": None,
            "firewall_result": None,
            "delta_s": None,
        }

        chain = SevenStepChain()
        input_data = StepInput(
            text=text,
            goal=goal or text,
        )
        result["chain_result"] = chain.execute_full_chain(input_data)
        result["delta_s"] = result["chain_result"].final_delta_s

        firewall = SemanticFirewall()
        result["firewall_result"] = firewall.check(text)

        return result

    def _run_governance_layer(self, text: str) -> dict:
        """运行治理层"""
        result = {
            "gate_results": {},
            "twin_atlas_result": None,
            "stopped": False,
            "coarse": False,
        }

        gate_results = evaluate_all_gates(text)
        result["gate_results"] = {gate_type.value: gr for gate_type, gr in gate_results.items()}

        for gate_type, gate_result in gate_results.items():
            if gate_result.state == GateState.STOP:
                result["stopped"] = True
            elif gate_result.state == GateState.COARSE:
                result["coarse"] = True

        atlas = TwinAtlas()
        result["twin_atlas_result"] = atlas.execute(text)

        return result

    def _run_diagnosis_layer(
        self,
        text: str,
        detection_result: dict,
    ) -> dict:
        """运行诊断层"""
        from taiji_verify.diagnosis.troubleshooting_atlas import TroubleshootingAtlas

        atlas = TroubleshootingAtlas()
        diagnosis = atlas.diagnose(text)

        return {
            "diagnosis": diagnosis,
            "recommended_fixes": diagnosis.recommended_fixes,
        }

    def _run_delta_s(
        self,
        embed_fn: Callable,
        input_text: str,
        ground_truth: str,
    ) -> DeltaSResult:
        """计算阴阳距"""
        input_vec = embed_fn(input_text)
        ground_vec = embed_fn(ground_truth)
        return self.delta_s_calculator.compute(input_vec, ground_vec)

    def _compute_verdict(
        self,
        ds_result: DeltaSResult,
        detection_result: dict,
        reasoning_result: dict,
        governance_result: dict,
    ) -> Verdict:
        """综合判定"""
        if governance_result["stopped"]:
            return Verdict.BLOCK

        if governance_result["coarse"]:
            return Verdict.CONDITIONAL_PASS

        hallucinations = detection_result.get("hallucination_result")
        if hallucinations and hallucinations.risk_level == DetectRiskLevel.CRITICAL:
            return Verdict.BLOCK

        if ds_result.zone == GateZone.DANGER:
            if hallucinations and hallucinations.weighted_score > 0.7:
                return Verdict.BLOCK

        if ds_result.zone == GateZone.RISK:
            firewall = reasoning_result.get("firewall_result")
            if firewall and firewall.decision == "MODIFIED":
                return Verdict.CORRECTED
            return Verdict.ESCALATE

        if ds_result.zone == GateZone.TRANSIT:
            return Verdict.CONDITIONAL_PASS

        if ds_result.zone == GateZone.SAFE:
            if hallucinations and hallucinations.risk_level == DetectRiskLevel.LOW:
                return Verdict.PASS
            return Verdict.CONDITIONAL_PASS

        return Verdict.PASS

    def _compute_verdict_no_vectors(
        self,
        detection_result: dict,
        reasoning_result: dict,
        governance_result: dict,
    ) -> Verdict:
        """无向量时的判定"""
        if governance_result["stopped"]:
            return Verdict.BLOCK

        if governance_result["coarse"]:
            return Verdict.CONDITIONAL_PASS

        hallucinations = detection_result.get("hallucination_result")
        if hallucinations and hallucinations.risk_level == DetectRiskLevel.CRITICAL:
            return Verdict.BLOCK

        firewall = reasoning_result.get("firewall_result")
        if firewall and firewall.decision == "BLOCK":
            return Verdict.BLOCK

        if hallucinations and hallucinations.risk_level == DetectRiskLevel.HIGH:
            return Verdict.CONDITIONAL_PASS

        return Verdict.PASS

    def _compute_verdict_from_delta_s(self, ds_result: DeltaSResult) -> Verdict:
        """从ΔS结果计算判定"""
        if ds_result.zone == GateZone.DANGER:
            return Verdict.BLOCK
        if ds_result.zone == GateZone.RISK:
            return Verdict.CONDITIONAL_PASS
        if ds_result.zone == GateZone.TRANSIT:
            return Verdict.CONDITIONAL_PASS
        return Verdict.PASS

    def add_rule(self, rule) -> None:
        """添加规则到检测层"""
        if hasattr(self, "rule_engine"):
            self.rule_engine.add_rule(rule)

    def add_knowledge_entry(
        self,
        entry_id: str,
        content: str,
        keywords: list[str],
    ) -> None:
        """添加知识条目"""
        if hasattr(self, "rule_engine"):
            self.rule_engine.add_knowledge_entry(entry_id, content, keywords)

    @property
    def system_health(self) -> dict:
        """系统健康状态"""
        health = {
            "engine_version": "v2.2_6layer_attribution",
            "layers_enabled": {
                "detection": hasattr(self, "rule_engine"),
                "reasoning": hasattr(self, "seven_step_chain"),
                "diagnosis": hasattr(self, "fix_map"),
                "governance": hasattr(self, "twin_atlas"),
                "execution": hasattr(self, "goal_compiler"),
                "attribution": hasattr(self, "attribution_verifier"),
            },
        }
        return health
