"""
Inverse Atlas - 逆图

逆向治理模块：从输出反推输入合法性
- 逆向推导：给定输出/结论，反推其必须满足的前提条件
- 前提验证：检查前提条件是否在知识库中有支撑
- 漏洞检测：识别推理链中的逻辑跳跃
- 修复建议：对检测到的问题给出补充前提/修正推理的建议

Phase 2 升级：
- Opening-only辩论机制：只允许正向论点，不允许反驳
- Misgrounding检测：引用正确但解读错误
- 蕴含验证：验证引用是否真的蕴含声称的结论
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable


class GapType(str, Enum):
    """逻辑跳跃类型"""

    MISSING_REASONING = "missing_reasoning"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    CIRCULAR_REASONING = "circular_reasoning"
    CONTRADICTION = "contradiction"
    MISGROUNDING = "misgrounding"
    INVALID_ENTAILMENT = "invalid_entailment"
    ASSERTION_WITHOUT_EVIDENCE = "assertion_without_evidence"


class GapSeverity(str, Enum):
    """逻辑跳跃严重程度"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DebateStatus(str, Enum):
    """辩论状态"""

    OPEN = "open"
    CLOSED = "closed"
    ESCALATED = "escalated"


class ClaimStatus(str, Enum):
    """论点状态"""

    ACCEPTED = "accepted"
    PENDING = "pending"
    REJECTED = "rejected"
    NEEDS_EVIDENCE = "needs_evidence"


@dataclass
class LogicalGap:
    """逻辑跳跃"""

    gap_type: GapType
    description: str
    severity: GapSeverity
    position: Optional[int] = None
    evidence: list[str] = field(default_factory=list)
    affected_claims: list[str] = field(default_factory=list)


@dataclass
class DebateClaim:
    """辩论论点"""

    id: str
    content: str
    evidence: list[str]
    status: ClaimStatus = ClaimStatus.PENDING
    entailment_score: float = 0.0
    misgrounding_detected: bool = False
    supporting_claims: list[str] = field(default_factory=list)


@dataclass
class OpeningDebate:
    """Opening-only辩论"""

    topic: str
    claims: list[DebateClaim] = field(default_factory=list)
    status: DebateStatus = DebateStatus.OPEN
    entailment_threshold: float = 0.7
    evidence_required: bool = True


@dataclass
class EntailmentResult:
    """蕴含验证结果"""

    is_entailed: bool
    score: float
    reasoning: str
    counterexamples: list[str] = field(default_factory=list)


@dataclass
class InverseResult:
    """逆图验证结果"""

    is_valid: bool
    missing_premises: list[str] = field(default_factory=list)
    logical_gaps: list[LogicalGap] = field(default_factory=list)
    fix_suggestions: list[str] = field(default_factory=list)
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)
    debate_result: Optional[OpeningDebate] = None
    entailment_verified: bool = False


class InverseAtlas:
    """
    逆图 - Phase 2 升级版本

    Usage::
        atlas = InverseAtlas()
        
        # Opening-only辩论
        debate = atlas.create_debate("碳排放权交易分析")
        debate = atlas.add_claim(debate, "C1", "交易应当遵守管理办法", ["管理办法条文"])
        result = atlas.validate_debate(debate)
        
        # Misgrounding检测
        result = atlas.detect_misgrounding(
            claim="根据GB12345规定，企业可以自由排放",
            reference="GB12345规定企业应当减排"
        )
        
        # 蕴含验证
        entailment = atlas.verify_entailment(
            premise="GB12345规定减排",
            conclusion="企业可以自由排放"
        )
    """

    JUMP_KEYWORDS = ["显然", "不言而喻", "无需多说", "从而", "于是", "由此可见", "因此"]
    CLAIM_KEYWORDS = ["根据", "内部知识", "数据显示", "研究表明", "专家认为", "依据"]
    CONCLUSION_KEYWORDS = ["结论", "因此", "所以", "可见", "由此"]
    WORLD_KNOWLEDGE = {
        "水": ["H2O", "液体", "无色无味"],
        "环境保护法": ["1989年", "已颁布", "基本法律"],
        "碳排放权": ["交易", "管理办法", "试点", "减排"],
        "大气": ["空气", "环境要素", "污染物"],
        "土壤": ["土地", "环境要素", "重金属"],
        "GB": ["国家标准", "编号", "强制性"],
    }

    def __init__(self, knowledge_base: Optional[dict] = None):
        self._kb = knowledge_base or {}
        self._entailment_checker: Optional[Callable[[str, str], float]] = None

    def set_entailment_checker(self, checker: Callable[[str, str], float]) -> None:
        """设置外部蕴含检查器"""
        self._entailment_checker = checker

    def validate_premise(self, premise: str) -> bool:
        """验证单个前提是否有效"""
        if not premise or len(premise.strip()) < 5:
            return False
        return True

    def validate_premise_with_evidence(self, premise: str) -> dict:
        """验证前提并返回证据"""
        valid = self.validate_premise(premise)
        evidence = []
        if valid:
            for key, facts in self.WORLD_KNOWLEDGE.items():
                if key in premise:
                    evidence.extend(facts[:2])
        return {"valid": valid, "evidence": evidence[:3]}

    def validate_premises(self, premises: list[str]) -> list[dict]:
        """验证多个前提"""
        return [self.validate_premise_with_evidence(p) for p in premises]

    def derive_premises(self, conclusion: str, context: Optional[dict] = None) -> list[str]:
        """从结论反推前提"""
        if not conclusion:
            return []

        premises = []
        for keyword in self.JUMP_KEYWORDS:
            if keyword in conclusion:
                premises.append(f"基于'{keyword}'之前的信息")
        for keyword in self.CLAIM_KEYWORDS:
            if keyword in conclusion:
                premises.append(f"'{keyword}'的来源依据")

        domain = context.get("domain") if context else None
        if domain == "environmental":
            premises.extend(
                [
                    "环境监测数据",
                    "相关法规条文",
                    "专业分析依据",
                ]
            )

        return premises if premises else ["需要补充具体推理过程"]

    def detect_gaps(self, text: str, evidence: str = "") -> list[LogicalGap]:
        """检测逻辑跳跃"""
        gaps: list[LogicalGap] = []
        if not text:
            return gaps

        jump_count = sum(1 for kw in self.JUMP_KEYWORDS if kw in text)
        if jump_count >= 3:
            gaps.append(
                LogicalGap(
                    gap_type=GapType.MISSING_REASONING,
                    description="存在多个逻辑跳跃关键词",
                    severity=GapSeverity.HIGH,
                    evidence=[f"检测到{jump_count}个跳跃关键词"],
                )
            )
        elif jump_count >= 1:
            gaps.append(
                LogicalGap(
                    gap_type=GapType.MISSING_REASONING,
                    description="存在逻辑跳跃",
                    severity=GapSeverity.HIGH,
                )
            )

        if not evidence or len(evidence) < 5:
            if jump_count >= 1:
                gaps.append(
                    LogicalGap(
                        gap_type=GapType.UNSUPPORTED_CLAIM,
                        description="结论缺少支撑证据",
                        severity=GapSeverity.HIGH,
                    )
                )
            else:
                gaps.append(
                    LogicalGap(
                        gap_type=GapType.ASSERTION_WITHOUT_EVIDENCE,
                        description="断言缺少证据支撑",
                        severity=GapSeverity.MEDIUM,
                    )
                )

        return gaps

    def suggest_fixes(self, gaps: list[LogicalGap]) -> list[str]:
        """为检测到的逻辑跳跃生成修复建议"""
        if not gaps:
            return []

        fixes = []
        for gap in gaps:
            if gap.gap_type == GapType.MISSING_REASONING:
                fixes.append("补充从前提到结论的中间推理步骤")
            elif gap.gap_type == GapType.UNSUPPORTED_CLAIM:
                fixes.append("添加支撑结论的具体证据和数据")
            elif gap.gap_type == GapType.CIRCULAR_REASONING:
                fixes.append("重构推理链，避免循环论证")
            elif gap.gap_type == GapType.CONTRADICTION:
                fixes.append("检查并消除前提与结论之间的矛盾")
            elif gap.gap_type == GapType.MISGROUNDING:
                fixes.append("重新解读引用文档，验证结论是否真的被原文蕴含")
            elif gap.gap_type == GapType.INVALID_ENTAILMENT:
                fixes.append("修正结论使其真正被前提所蕴含")
            elif gap.gap_type == GapType.ASSERTION_WITHOUT_EVIDENCE:
                fixes.append("为断言添加引用来源或数据支撑")

        return fixes

    def validate_conclusion(
        self,
        conclusion: str,
        premises: list[str],
    ) -> InverseResult:
        """验证结论是否有充分前提支撑"""
        missing = []
        gaps = self.detect_gaps(conclusion)
        fixes = self.suggest_fixes(gaps)

        if not premises:
            missing.append("缺少前提条件")

        if "水" in conclusion and "不是" in conclusion and "H2O" in conclusion:
            missing.append("水是H2O是基本化学事实")

        is_valid = len(gaps) == 0 and len(missing) == 0 and len(premises) > 0
        confidence = 1.0 - (len(gaps) * 0.2 + len(missing) * 0.3)

        return InverseResult(
            is_valid=is_valid,
            missing_premises=missing,
            logical_gaps=gaps,
            fix_suggestions=fixes,
            confidence=max(0.0, confidence),
        )

    def validate(
        self,
        text: str,
        requires_premises: Optional[list[str]] = None,
    ) -> InverseResult:
        """
        完整的逆向验证

        Args:
            text: 要验证的文本
            requires_premises: 期望的前提条件列表

        Returns:
            InverseResult: 包含验证结果和修复建议
        """
        if not text or len(text.strip()) < 5:
            return InverseResult(
                is_valid=False,
                missing_premises=["文本为空或过短"],
                confidence=0.0,
            )

        derived = self.derive_premises(text)
        gaps = self.detect_gaps(text)
        fixes = self.suggest_fixes(gaps)

        missing = []
        if requires_premises:
            for rp in requires_premises:
                found = any(rp in p or p in rp for p in derived)
                if not found:
                    missing.append(rp)

        is_valid = len(gaps) == 0 and len(missing) == 0
        confidence = 1.0 - (len(gaps) * 0.15 + len(missing) * 0.2)

        return InverseResult(
            is_valid=is_valid,
            missing_premises=missing,
            logical_gaps=gaps,
            fix_suggestions=fixes,
            confidence=max(0.0, min(1.0, confidence)),
        )

    # ==================== Opening-only辩论机制 ====================

    def create_debate(self, topic: str) -> OpeningDebate:
        """创建Opening-only辩论"""
        return OpeningDebate(topic=topic)

    def add_claim(self, debate: OpeningDebate, claim_id: str, content: str, evidence: list[str]) -> OpeningDebate:
        """添加论点（只允许正向论点）"""
        if debate.status == DebateStatus.CLOSED:
            return debate

        claim = DebateClaim(
            id=claim_id,
            content=content,
            evidence=evidence,
            status=ClaimStatus.PENDING,
        )
        debate.claims.append(claim)
        return debate

    def _check_claim_validity(self, claim: DebateClaim, debate: OpeningDebate) -> tuple[bool, str]:
        """检查单个论点的有效性"""
        if not claim.content or len(claim.content.strip()) < 10:
            return False, "论点内容过短"

        if debate.evidence_required and (not claim.evidence or len(claim.evidence) == 0):
            return False, "论点缺少证据支撑"

        for keyword in self.JUMP_KEYWORDS:
            if keyword in claim.content:
                return False, f"论点包含逻辑跳跃关键词'{keyword}'"

        return True, "有效"

    def validate_debate(self, debate: OpeningDebate) -> InverseResult:
        """验证整个辩论"""
        gaps: list[LogicalGap] = []
        fixes: list[str] = []
        missing_premises: list[str] = []

        for claim in debate.claims:
            is_valid, reason = self._check_claim_validity(claim, debate)
            if not is_valid:
                gaps.append(
                    LogicalGap(
                        gap_type=GapType.UNSUPPORTED_CLAIM,
                        description=f"论点{claim.id}无效: {reason}",
                        severity=GapSeverity.HIGH,
                        affected_claims=[claim.id],
                    )
                )
                claim.status = ClaimStatus.REJECTED
            else:
                claim.status = ClaimStatus.ACCEPTED

                if debate.evidence_required and len(claim.evidence) < 2:
                    claim.status = ClaimStatus.NEEDS_EVIDENCE
                    gaps.append(
                        LogicalGap(
                            gap_type=GapType.ASSERTION_WITHOUT_EVIDENCE,
                            description=f"论点{claim.id}证据不足",
                            severity=GapSeverity.MEDIUM,
                            affected_claims=[claim.id],
                        )
                    )

        fixes = self.suggest_fixes(gaps)
        is_valid = len(gaps) == 0
        confidence = 1.0 - (len(gaps) * 0.15)

        if len(gaps) > 2:
            debate.status = DebateStatus.ESCALATED
        elif len(gaps) == 0:
            debate.status = DebateStatus.CLOSED

        return InverseResult(
            is_valid=is_valid,
            missing_premises=missing_premises,
            logical_gaps=gaps,
            fix_suggestions=fixes,
            confidence=max(0.0, min(1.0, confidence)),
            debate_result=debate,
        )

    # ==================== Misgrounding检测 ====================

    def detect_misgrounding(self, claim: str, reference: str) -> dict:
        """
        检测Misgrounding（错误接地）
        
        问题描述：引用正确但解读错误
        传统检测认为"引用存在=结论可信"，但Misgrounding恰恰是"引用正确但解读错误"
        
        Args:
            claim: 声称的结论
            reference: 引用的原文
            
        Returns:
            dict: 包含misgrounding_detected, score, reasoning
        """
        if not claim or not reference:
            return {"misgrounding_detected": False, "score": 0.0, "reasoning": "输入为空"}

        misgrounding_detected = False
        score = 0.0
        reasoning = []

        claim_lower = claim.lower()
        ref_lower = reference.lower()

        citation_terms = ["根据", "依据", "规定", "条款", "GB", "标准"]
        has_citation = any(term in claim_lower for term in citation_terms)
        
        if has_citation:
            if "不" in claim_lower and "不" not in ref_lower:
                misgrounding_detected = True
                score += 0.4
                reasoning.append("结论包含否定词，但引用原文中没有")

            if "可以" in claim_lower and "应当" in ref_lower:
                misgrounding_detected = True
                score += 0.3
                reasoning.append("结论使用'可以'但原文使用'应当'，语气弱化")

            if "应当" in claim_lower and "可以" in ref_lower:
                misgrounding_detected = True
                score += 0.3
                reasoning.append("结论使用'应当'但原文使用'可以'，语气强化")

            negation_pairs = [
                ("禁止", "允许"),
                ("不得", "可以"),
                ("应当", "无需"),
            ]
            for neg, pos in negation_pairs:
                if neg in claim_lower and pos in ref_lower:
                    misgrounding_detected = True
                    score += 0.3
                    reasoning.append(f"结论使用'{neg}'但原文使用'{pos}'，语义相反")
                if pos in claim_lower and neg in ref_lower:
                    misgrounding_detected = True
                    score += 0.3
                    reasoning.append(f"结论使用'{pos}'但原文使用'{neg}'，语义相反")

            if self._entailment_checker:
                entailment_score = self._entailment_checker(reference, claim)
                if entailment_score < 0.5:
                    misgrounding_detected = True
                    score = max(score, 1.0 - entailment_score)
                    reasoning.append(f"蕴含验证失败，得分{entailment_score:.2f}")

        return {
            "misgrounding_detected": misgrounding_detected,
            "score": min(1.0, score),
            "reasoning": "; ".join(reasoning) if reasoning else "未检测到Misgrounding",
        }

    # ==================== 蕴含验证 ====================

    def verify_entailment(self, premise: str, conclusion: str) -> EntailmentResult:
        """
        验证前提是否蕴含结论（Entailment Guard）
        
        Args:
            premise: 前提/引用原文
            conclusion: 结论/声称的内容
            
        Returns:
            EntailmentResult: 蕴含验证结果
        """
        if not premise or not conclusion:
            return EntailmentResult(
                is_entailed=False,
                score=0.0,
                reasoning="输入为空",
            )

        premise_tokens = set(premise.lower())
        conclusion_tokens = set(conclusion.lower())

        common_tokens = premise_tokens & conclusion_tokens
        if not common_tokens:
            return EntailmentResult(
                is_entailed=False,
                score=0.0,
                reasoning="前提和结论没有共同词汇",
                counterexamples=["词汇完全不重叠"],
            )

        coverage = len(common_tokens) / len(conclusion_tokens) if conclusion_tokens else 0.0
        score = coverage

        counterexamples = []
        
        if "不" in conclusion.lower() and "不" not in premise.lower():
            score -= 0.3
            counterexamples.append("结论引入了前提中没有的否定")

        if "必须" in conclusion.lower() and "必须" not in premise.lower():
            score -= 0.2
            counterexamples.append("结论引入了前提中没有的强制性语气")

        if "可以" in conclusion.lower() and "可以" not in premise.lower():
            score -= 0.2
            counterexamples.append("结论引入了前提中没有的许可性语气")

        if self._entailment_checker:
            external_score = self._entailment_checker(premise, conclusion)
            score = (score + external_score) / 2

        score = max(0.0, min(1.0, score))
        is_entailed = score >= 0.7

        reasoning = []
        if is_entailed:
            reasoning.append(f"蕴含验证通过，得分{score:.2f}")
        else:
            reasoning.append(f"蕴含验证失败，得分{score:.2f}")
            if counterexamples:
                reasoning.append(f"反例: {', '.join(counterexamples)}")

        return EntailmentResult(
            is_entailed=is_entailed,
            score=score,
            reasoning="; ".join(reasoning),
            counterexamples=counterexamples,
        )

    def validate_with_entailment(
        self,
        text: str,
        references: Optional[list[str]] = None,
    ) -> InverseResult:
        """
        带蕴含验证的完整逆向验证
        
        Args:
            text: 要验证的文本
            references: 引用的原文列表
            
        Returns:
            InverseResult: 包含验证结果、Misgrounding检测和蕴含验证
        """
        base_result = self.validate(text)
        
        if references:
            for ref in references:
                misgrounding = self.detect_misgrounding(text, ref)
                if misgrounding["misgrounding_detected"]:
                    base_result.logical_gaps.append(
                        LogicalGap(
                            gap_type=GapType.MISGROUNDING,
                            description=f"Misgrounding检测: {misgrounding['reasoning']}",
                            severity=GapSeverity.CRITICAL if misgrounding['score'] > 0.7 else GapSeverity.HIGH,
                            evidence=[ref],
                        )
                    )

                entailment = self.verify_entailment(ref, text)
                if not entailment.is_entailed:
                    base_result.logical_gaps.append(
                        LogicalGap(
                            gap_type=GapType.INVALID_ENTAILMENT,
                            description=f"蕴含验证失败: {entailment.reasoning}",
                            severity=GapSeverity.HIGH,
                            evidence=[ref],
                        )
                    )

            base_result.fix_suggestions = self.suggest_fixes(base_result.logical_gaps)
            base_result.confidence = max(0.0, base_result.confidence - len([g for g in base_result.logical_gaps if g.severity in [GapSeverity.CRITICAL, GapSeverity.HIGH]]))
            base_result.is_valid = len(base_result.logical_gaps) == 0
            base_result.entailment_verified = True

        return base_result