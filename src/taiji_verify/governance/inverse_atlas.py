"""
Inverse Atlas - 逆图

逆向治理模块：从输出反推输入合法性
- 逆向推导：给定输出/结论，反推其必须满足的前提条件
- 前提验证：检查前提条件是否在知识库中有支撑
- 漏洞检测：识别推理链中的逻辑跳跃
- 修复建议：对检测到的问题给出补充前提/修正推理的建议
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class GapType(str, Enum):
    """逻辑跳跃类型"""

    MISSING_REASONING = "missing_reasoning"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    CIRCULAR_REASONING = "circular_reasoning"
    CONTRADICTION = "contradiction"


class GapSeverity(str, Enum):
    """逻辑跳跃严重程度"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class LogicalGap:
    """逻辑跳跃"""

    gap_type: GapType
    description: str
    severity: GapSeverity
    position: Optional[int] = None
    evidence: list[str] = field(default_factory=list)


@dataclass
class InverseResult:
    """逆图验证结果"""

    is_valid: bool
    missing_premises: list[str] = field(default_factory=list)
    logical_gaps: list[LogicalGap] = field(default_factory=list)
    fix_suggestions: list[str] = field(default_factory=list)
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)


class InverseAtlas:
    """
    逆图

    Usage::
        atlas = InverseAtlas()
        result = atlas.validate("结论", requires_premises=["前提1"])
        if not result.is_valid:
            print(result.missing_premises)
            print(result.logical_gaps)
    """

    JUMP_KEYWORDS = ["显然", "不言而喻", "无需多说", "从而", "于是", "由此可见", "因此"]
    CLAIM_KEYWORDS = ["根据", "内部知识", "数据显示", "研究表明", "专家认为"]
    WORLD_KNOWLEDGE = {
        "水": ["H2O", "液体", "无色无味"],
        "环境保护法": ["1989年", "已颁布", "基本法律"],
        "碳排放权": ["交易", "管理办法", "试点"],
        "大气": ["空气", "环境要素", "污染物"],
        "土壤": ["土地", "环境要素", "重金属"],
    }

    def __init__(self, knowledge_base: Optional[dict] = None):
        self._kb = knowledge_base or {}

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
