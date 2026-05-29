"""
Neural Symbolic Dual-Track Verifier - 神经符号双轨验证器

核心概念：
- 神经轨道（Neural Track）：基于LLM的软验证，概率性输出
- 符号轨道（Symbolic Track）：基于规则引擎的硬验证，确定性输出
- 双轨融合：加权组合两条轨道的结果

功能：
- 神经轨道：调用CrossModelVerifier进行多模型交叉验证
- 符号轨道：调用RuleEngine+ConsistencyChecker进行规则验证
- 融合策略：weighted/conservative/optimistic
- 轨道矛盾检测与处理

v2.2 Phase 1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from taiji_verify.detection.cross_model_verifier import (
    CrossModelVerifier,
    CrossModelResult,
)
from taiji_verify.detection.rule_engine import RuleEngine, Rule
from taiji_verify.detection.consistency import SelfConsistencyChecker


class TrackType(str, Enum):
    """
    轨道类型枚举

    - NEURAL: 神经轨道（LLM软验证）
    - SYMBOLIC: 符号轨道（规则硬验证）
    - FUSED: 融合结果
    """

    NEURAL = "neural"
    SYMBOLIC = "symbolic"
    FUSED = "fused"


class TrackResult:
    """
    单轨道结果

    存储单个验证轨道的结果，包括分数、判定、证据和置信度。

    Attributes:
        track_type: 轨道类型
        score: 验证分数（0-1）
        verdict: 判定结果（pass/fail/uncertain）
        evidence: 证据链列表
        confidence: 轨道置信度（0-1）
    """

    def __init__(
        self,
        track_type: TrackType,
        score: float = 0.0,
        verdict: str = "uncertain",
        evidence: Optional[list[str]] = None,
        confidence: float = 0.5,
    ):
        self.track_type = track_type
        self.score = score
        self.verdict = verdict
        self.evidence = evidence or []
        self.confidence = confidence

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "track_type": self.track_type.value,
            "score": self.score,
            "verdict": self.verdict,
            "evidence": self.evidence,
            "confidence": self.confidence,
        }


@dataclass
class DualTrackResult:
    """
    双轨融合结果

    存储神经符号双轨验证的完整结果，包括两条轨道的结果和融合结果。

    Attributes:
        neural_result: 神经轨道结果
        symbolic_result: 符号轨道结果
        fused_result: 融合结果
        fusion_strategy: 融合策略名称
        disagreement: 两轨道是否矛盾
    """

    neural_result: TrackResult
    symbolic_result: TrackResult
    fused_result: TrackResult
    fusion_strategy: str = "weighted"
    disagreement: bool = False

    @property
    def has_disagreement(self) -> bool:
        """两轨道是否存在矛盾"""
        return self.disagreement

    def get_highest_risk_track(self) -> TrackType:
        """获取风险更高的轨道"""
        if self.neural_result.score < self.symbolic_result.score:
            return TrackType.NEURAL
        return TrackType.SYMBOLIC

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "neural": self.neural_result.to_dict(),
            "symbolic": self.symbolic_result.to_dict(),
            "fused": self.fused_result.to_dict(),
            "fusion_strategy": self.fusion_strategy,
            "disagreement": self.disagreement,
        }


class NeuralSymbolicVerifier:
    """
    神经符号双轨验证器

    结合神经网络的概率性验证和符号系统的确定性验证，
    通过加权融合提供更可靠的验证结果。

    设计原则：
    - 符号轨道权重更高（默认0.6），确定性更强
    - 三种融合策略：weighted/conservative/optimistic
    - 轨道矛盾时自动切换保守策略并标记

    Usage:
        # 默认配置
        verifier = NeuralSymbolicVerifier()
        result = verifier.verify("碳排放权交易管理办法规定...")

        # 自定义配置
        verifier = NeuralSymbolicVerifier(
            fusion_strategy="conservative",
            neural_weight=0.3,
            symbolic_weight=0.7,
        )
        result = verifier.verify(text, context)
    """

    SUPPORTED_STRATEGIES = ["weighted", "conservative", "optimistic"]

    def __init__(
        self,
        neural_verifier: Optional[CrossModelVerifier] = None,
        symbolic_rules: Optional[list[Rule]] = None,
        fusion_strategy: str = "weighted",
        neural_weight: float = 0.4,
        symbolic_weight: float = 0.6,
        enable_neural: bool = True,
        enable_symbolic: bool = True,
    ):
        """
        初始化双轨验证器

        Args:
            neural_verifier: 神经轨道验证器，默认使用CrossModelVerifier
            symbolic_rules: 符号轨道规则列表
            fusion_strategy: 融合策略（weighted/conservative/optimistic）
            neural_weight: 神经轨道权重
            symbolic_weight: 符号轨道权重
            enable_neural: 是否启用神经轨道
            enable_symbolic: 是否启用符号轨道
        """
        # 验证权重
        if abs(neural_weight + symbolic_weight - 1.0) > 0.01:
            raise ValueError(
                f"权重和必须为1.0，当前 neural={neural_weight}, symbolic={symbolic_weight}"
            )

        if fusion_strategy not in self.SUPPORTED_STRATEGIES:
            raise ValueError(
                f"不支持的融合策略: {fusion_strategy}，支持: {self.SUPPORTED_STRATEGIES}"
            )

        # 初始化神经轨道
        self._enable_neural = enable_neural
        if enable_neural:
            self._neural_verifier = neural_verifier or CrossModelVerifier()
        else:
            self._neural_verifier = None

        # 初始化符号轨道
        self._enable_symbolic = enable_symbolic
        if enable_symbolic:
            self._rule_engine = RuleEngine()
            self._consistency_checker = SelfConsistencyChecker()
            if symbolic_rules:
                for rule in symbolic_rules:
                    self._rule_engine.add_rule(rule)
        else:
            self._rule_engine = None
            self._consistency_checker = None

        # 融合配置
        self._fusion_strategy = fusion_strategy
        self._neural_weight = neural_weight
        self._symbolic_weight = symbolic_weight

    def verify(
        self,
        text: str,
        context: Optional[dict] = None,
        claim: Optional[str] = None,
    ) -> DualTrackResult:
        """
        双轨并行验证

        同时运行神经轨道和符号轨道，然后融合结果。

        Args:
            text: 待验证文本
            context: 上下文信息（可选）
            claim: 声称的来源或结论（可选）

        Returns:
            DualTrackResult: 双轨融合结果
        """
        # 运行两条轨道
        neural_result = self._run_neural_track(text, context)
        symbolic_result = self._run_symbolic_track(text, context, claim)

        # 检测轨道矛盾
        disagreement = self._check_disagreement(neural_result, symbolic_result)

        # 融合
        fusion_strategy = self._fusion_strategy
        if disagreement:
            # 轨道矛盾时自动切换保守策略
            fusion_strategy = "conservative"

        fused_result = self._fuse(neural_result, symbolic_result, fusion_strategy)

        return DualTrackResult(
            neural_result=neural_result,
            symbolic_result=symbolic_result,
            fused_result=fused_result,
            fusion_strategy=fusion_strategy,
            disagreement=disagreement,
        )

    def _run_neural_track(
        self,
        text: str,
        context: Optional[dict],
    ) -> TrackResult:
        """
        神经轨道：调用CrossModelVerifier

        使用多个LLM模型交叉验证文本。

        Args:
            text: 待验证文本
            context: 上下文信息

        Returns:
            TrackResult: 神经轨道结果
        """
        if not self._enable_neural or self._neural_verifier is None:
            return TrackResult(
                track_type=TrackType.NEURAL,
                score=0.5,
                verdict="uncertain",
                evidence=["神经轨道未启用"],
                confidence=0.0,
            )

        try:
            # 准备结论文本
            conclusion = text
            context_str = context.get("context") if context else None

            # 调用交叉验证器
            result = self._neural_verifier.verify(conclusion, context_str)

            # 转换结果
            evidence = []
            if result.model_responses:
                for model_id, response in result.model_responses.items():
                    evidence.append(f"{model_id}: {response[:50]}...")

            # 根据判定确定verdict
            from taiji_verify.detection.cross_model_verifier import CrossModelVerdict

            if result.verdict == CrossModelVerdict.AGREE:
                verdict = "pass"
            elif result.verdict == CrossModelVerdict.DISAGREE:
                verdict = "fail"
            else:
                verdict = "uncertain"

            return TrackResult(
                track_type=TrackType.NEURAL,
                score=result.confidence,
                verdict=verdict,
                evidence=evidence,
                confidence=result.confidence,
            )

        except Exception as e:
            return TrackResult(
                track_type=TrackType.NEURAL,
                score=0.0,
                verdict="fail",
                evidence=[f"神经轨道错误: {str(e)}"],
                confidence=0.0,
            )

    def _run_symbolic_track(
        self,
        text: str,
        context: Optional[dict],
        claim: Optional[str],
    ) -> TrackResult:
        """
        符号轨道：调用RuleEngine+ConsistencyChecker

        使用规则引擎进行确定性验证。

        Args:
            text: 待验证文本
            context: 上下文信息
            claim: 声称的来源或结论

        Returns:
            TrackResult: 符号轨道结果
        """
        if not self._enable_symbolic:
            return TrackResult(
                track_type=TrackType.SYMBOLIC,
                score=0.5,
                verdict="uncertain",
                evidence=["符号轨道未启用"],
                confidence=0.0,
            )

        evidence = []
        total_score = 0.0
        rule_count = 0

        try:
            # 1. 规则引擎验证
            rule_result = self._rule_engine.verify(text)
            if rule_result:
                rule_count += 1
                total_score += rule_result.confidence
                evidence.append(f"规则引擎: score={rule_result.confidence:.2f}")
                if rule_result.corrected_text:
                    evidence.append(f"修正文本: {rule_result.corrected_text[:50]}...")

            # 2. 自一致性检查
            if self._consistency_checker:
                consistency_result = self._consistency_checker.batch_consistency([text])
                if consistency_result:
                    consistency_score = (
                        consistency_result[0].similarity_score
                        if hasattr(consistency_result[0], "similarity_score")
                        else 0.5
                    )
                    total_score += consistency_score
                    rule_count += 1
                    evidence.append(f"自一致性: score={consistency_score:.2f}")

            # 3. 上下文知识验证
            if context and self._rule_engine.knowledge_base:
                kb_matches = self._rule_engine.verify(text)
                if kb_matches and kb_matches.knowledge_matches:
                    match = kb_matches.knowledge_matches[0]
                    evidence.append(f"知识库匹配: {match.entry_id} (相似度={match.similarity:.2f})")

            # 计算最终分数
            if rule_count > 0:
                final_score = total_score / rule_count
            else:
                final_score = 0.5

            # 确定verdict
            if final_score >= 0.7:
                verdict = "pass"
            elif final_score < 0.3:
                verdict = "fail"
            else:
                verdict = "uncertain"

            return TrackResult(
                track_type=TrackType.SYMBOLIC,
                score=final_score,
                verdict=verdict,
                evidence=evidence,
                confidence=0.9,  # 符号轨道确定性高
            )

        except Exception as e:
            return TrackResult(
                track_type=TrackType.SYMBOLIC,
                score=0.0,
                verdict="fail",
                evidence=[f"符号轨道错误: {str(e)}"],
                confidence=0.0,
            )

    def _fuse(
        self,
        neural: TrackResult,
        symbolic: TrackResult,
        strategy: str,
    ) -> TrackResult:
        """
        双轨融合

        根据融合策略组合两条轨道的结果。

        Args:
            neural: 神经轨道结果
            symbolic: 符号轨道结果
            strategy: 融合策略

        Returns:
            TrackResult: 融合后的结果
        """
        evidence = [
            f"神经轨道: score={neural.score:.2f}, verdict={neural.verdict}",
            f"符号轨道: score={symbolic.score:.2f}, verdict={symbolic.verdict}",
            f"融合策略: {strategy}",
        ]

        if strategy == "weighted":
            # 加权平均
            fused_score = (
                neural.score * self._neural_weight + symbolic.score * self._symbolic_weight
            )
            fused_confidence = (
                neural.confidence * self._neural_weight
                + symbolic.confidence * self._symbolic_weight
            )

        elif strategy == "conservative":
            # 取更保守的结果（更低的分数）
            if neural.score < symbolic.score:
                fused_score = neural.score * 0.6 + symbolic.score * 0.4
            else:
                fused_score = neural.score * 0.4 + symbolic.score * 0.6
            fused_score = min(neural.score, symbolic.score) * 0.8 + fused_score * 0.2
            fused_confidence = min(neural.confidence, symbolic.confidence) * 0.9

        elif strategy == "optimistic":
            # 取更乐观的结果
            fused_score = max(neural.score, symbolic.score) * 0.9
            fused_confidence = max(neural.confidence, symbolic.confidence) * 0.9

        else:
            fused_score = 0.5
            fused_confidence = 0.5

        # 确定verdict
        if fused_score >= 0.7:
            fused_verdict = "pass"
        elif fused_score < 0.3:
            fused_verdict = "fail"
        else:
            fused_verdict = "uncertain"

        return TrackResult(
            track_type=TrackType.FUSED,
            score=fused_score,
            verdict=fused_verdict,
            evidence=evidence,
            confidence=fused_confidence,
        )

    def _check_disagreement(self, neural: TrackResult, symbolic: TrackResult) -> bool:
        """
        检测轨道矛盾

        当两条轨道一个pass一个fail时视为矛盾。

        Args:
            neural: 神经轨道结果
            symbolic: 符号轨道结果

        Returns:
            bool: 是否存在矛盾
        """
        # 只有当两个都是明确判定时才检查矛盾
        clear_results = {"pass", "fail"}
        if neural.verdict in clear_results and symbolic.verdict in clear_results:
            return neural.verdict != symbolic.verdict
        return False

    def add_symbolic_rule(self, rule: Rule) -> None:
        """
        添加符号轨道规则

        Args:
            rule: 验证规则
        """
        if self._rule_engine:
            self._rule_engine.add_rule(rule)

    def add_knowledge(
        self,
        entry_id: str,
        content: str,
        keywords: list[str],
        source: str = "",
        metadata: Optional[dict] = None,
    ) -> None:
        """
        添加知识库条目

        Args:
            entry_id: 条目ID
            content: 内容
            keywords: 关键词
            source: 来源
            metadata: 元数据
        """
        if self._rule_engine:
            self._rule_engine.add_knowledge_entry(entry_id, content, keywords, source, metadata)

    def set_fusion_strategy(self, strategy: str) -> None:
        """
        设置融合策略

        Args:
            strategy: 策略名称
        """
        if strategy not in self.SUPPORTED_STRATEGIES:
            raise ValueError(f"不支持的融合策略: {strategy}，支持: {self.SUPPORTED_STRATEGIES}")
        self._fusion_strategy = strategy

    @property
    def fusion_strategy(self) -> str:
        """获取当前融合策略"""
        return self._fusion_strategy

    @property
    def weights(self) -> tuple[float, float]:
        """获取神经/符号权重"""
        return (self._neural_weight, self._symbolic_weight)

    @property
    def is_neural_enabled(self) -> bool:
        """神经轨道是否启用"""
        return self._enable_neural

    @property
    def is_symbolic_enabled(self) -> bool:
        """符号轨道是否启用"""
        return self._enable_symbolic
