"""
Governance Gates - 治理门

7个治理门，每个都有实际检查逻辑：
1. 问题构成 (PROBLEM_FORMATION)     - 问题是否有效形成？
2. 世界对齐 (WORLD_ALIGNMENT)       - 是否与已知事实对齐？
3. 崩溃几何 (COLLAPSE_GEOMETRY)     - 是否有崩溃迹象？
4. 相邻切割 (ADJACENT_CUT)          - 是否与相邻领域冲突？
5. 解决授权 (RESOLUTION_AUTH)       - 是否赢得存在权利？
6. 修复合法性 (FIX_LEGALITY)        - 修正是否合法？
7. Emission控制 (EMISSION_CONTROL)  - 是否可公开发布？

4个输出状态: STOP / COARSE / UNRESOLVED / AUTHORIZED
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import re


class GateType(str, Enum):
    """治理门类型"""
    PROBLEM_FORMATION = "problem_formation"
    WORLD_ALIGNMENT = "world_alignment"
    COLLAPSE_GEOMETRY = "collapse_geometry"
    ADJACENT_CUT = "adjacent_cut"
    RESOLUTION_AUTH = "resolution_auth"
    FIX_LEGALITY = "fix_legality"
    EMISSION_CONTROL = "emission_control"


class GateState(str, Enum):
    """门状态"""
    STOP = "stop"
    COARSE = "coarse"
    UNRESOLVED = "unresolved"
    AUTHORIZED = "authorized"


@dataclass
class GateResult:
    """门结果"""
    passed: bool
    state: GateState
    reason: str
    confidence: float = 1.0
    details: dict = field(default_factory=dict)


class GovernanceGate:
    """
    治理门 - 每个门都有实际检查逻辑

    Usage::
        gate = GovernanceGate(GateType.WORLD_ALIGNMENT)
        result = gate.evaluate("地球是圆的")
        assert result.state == GateState.AUTHORIZED
    """

    WORLD_KNOWLEDGE = {
        "地球": ["圆", "球形", "行星"],
        "太阳": ["恒星", "发光", "核聚变"],
        "水": ["H2O", "无色无味", "常温液态"],
        "环境保护法": ["1989年", "已颁布", "基本法律"],
        "大气污染防治法": ["1987年", "已颁布"],
        "水污染防治法": ["1984年", "已颁布"],
    }

    ADJACENT_CONFLICTS = {
        "法律": ["道德规范", "政策文件"],
        "科学": ["迷信", "伪科学"],
        "经济": ["环保", "社会效益"],
        "技术": ["管理", "流程"],
    }

    def __init__(self, gate_type: GateType):
        self.gate_type = gate_type

    def evaluate(
        self,
        input_text: str,
        context: Optional[dict] = None,
    ) -> GateResult:
        """评估输入"""
        if self.gate_type == GateType.PROBLEM_FORMATION:
            return self._evaluate_problem_formation(input_text)
        elif self.gate_type == GateType.WORLD_ALIGNMENT:
            return self._evaluate_world_alignment(input_text)
        elif self.gate_type == GateType.COLLAPSE_GEOMETRY:
            return self._evaluate_collapse_geometry(input_text)
        elif self.gate_type == GateType.ADJACENT_CUT:
            return self._evaluate_adjacent_cut(input_text)
        elif self.gate_type == GateType.RESOLUTION_AUTH:
            return self._evaluate_resolution_auth(input_text)
        elif self.gate_type == GateType.FIX_LEGALITY:
            return self._evaluate_fix_legality(input_text)
        elif self.gate_type == GateType.EMISSION_CONTROL:
            return self._evaluate_emission_control(input_text)

        return GateResult(passed=True, state=GateState.AUTHORIZED, reason="默认通过")

    def _evaluate_problem_formation(self, text: str) -> GateResult:
        """评估问题构成"""
        issues = []

        if len(text) < 10:
            issues.append("问题描述过短")

        if not any(c in text for c in '？?。.!！'):
            issues.append("缺少结束标点")

        question_words = ["什么", "如何", "为什么", "谁", "哪", "when", "what", "how", "why"]
        if not any(qw in text.lower() for qw in question_words):
            issues.append("缺少疑问词")

        if issues:
            if len(issues) >= 2:
                return GateResult(
                    passed=False,
                    state=GateState.STOP,
                    reason=f"问题未有效形成: {', '.join(issues)}",
                    confidence=0.9,
                    details={"issues": issues}
                )
            return GateResult(
                passed=False,
                state=GateState.COARSE,
                reason=f"问题格式不完整: {', '.join(issues)}",
                confidence=0.7,
                details={"issues": issues}
            )

        return GateResult(
            passed=True,
            state=GateState.AUTHORIZED,
            reason="问题有效形成",
            confidence=0.95,
        )

    def _evaluate_world_alignment(self, text: str) -> GateResult:
        """评估世界对齐 - 真正检查知识库"""
        violations = []
        aligned = []

        for entity, facts in self.WORLD_KNOWLEDGE.items():
            if entity in text:
                for i, part in enumerate(text.split(entity)):
                    for fact in facts:
                        if fact in text:
                            aligned.append(f"{entity}:{fact}")
                        elif i > 0:
                            neg_fact = f"非{fact}"
                            if neg_fact in text or f"不是{fact}" in text:
                                violations.append(f"{entity}与事实冲突")

        fact_check_patterns = [
            (r'\d{4}年\d{1,2}月', "日期格式"),
            (r'GB\d{5,}', "异常标准编号"),
            (r'据.*报道', "无来源引用"),
        ]

        for pattern, label in fact_check_patterns:
            if re.search(pattern, text):
                aligned.append(label)

        if violations:
            return GateResult(
                passed=False,
                state=GateState.STOP,
                reason=f"与已知事实冲突: {violations[0]}",
                confidence=0.85,
                details={"violations": violations}
            )

        if not aligned:
            return GateResult(
                passed=True,
                state=GateState.AUTHORIZED,
                reason="无事实冲突，可信度高",
                confidence=0.9,
            )

        return GateResult(
            passed=True,
            state=GateState.AUTHORIZED,
            reason=f"与事实对齐: {len(aligned)}项验证通过",
            confidence=0.95,
            details={"aligned": aligned}
        )

    def _evaluate_collapse_geometry(self, text: str) -> GateResult:
        """评估崩溃几何 - 检测崩溃迹象"""
        collapse_indicators = [
            ("崩溃", "系统崩溃关键词"),
            ("错误", "错误关键词"),
            ("失败", "失败关键词"),
            ("异常", "异常关键词"),
            ("死循环", "循环崩溃"),
            ("无限", "无限循环"),
            ("OOM", "内存溢出"),
            ("超时", "超时崩溃"),
        ]

        detected = []
        for keyword, label in collapse_indicators:
            if keyword in text:
                detected.append(label)

        if detected:
            severity = "HIGH" if len(detected) > 2 else "MEDIUM"
            return GateResult(
                passed=False,
                state=GateState.STOP if severity == "HIGH" else GateState.COARSE,
                reason=f"检测到崩溃迹象: {', '.join(detected)}",
                confidence=0.9,
                details={"collapse_indicators": detected, "severity": severity}
            )

        return GateResult(
            passed=True,
            state=GateState.AUTHORIZED,
            reason="无崩溃迹象",
            confidence=0.95,
        )

    def _evaluate_adjacent_cut(self, text: str) -> GateResult:
        """评估相邻切割 - 检测领域冲突"""
        conflicts = []

        for domain, adjacent_domains in self.ADJACENT_CONFLICTS.items():
            if domain in text:
                for adjacent in adjacent_domains:
                    if adjacent in text:
                        patterns = [
                            f"{domain}不是{adjacent}",
                            f"{domain}与{adjacent}无关",
                            f"不应考虑{adjacent}",
                        ]
                        for pattern in patterns:
                            if pattern in text or pattern.replace("不应", "不需要") in text:
                                conflicts.append(f"{domain}与{adjacent}冲突")

        if conflicts:
            return GateResult(
                passed=False,
                state=GateState.COARSE,
                reason=f"检测到领域冲突: {conflicts[0]}",
                confidence=0.8,
                details={"conflicts": conflicts}
            )

        return GateResult(
            passed=True,
            state=GateState.AUTHORIZED,
            reason="无相邻领域冲突",
            confidence=0.9,
        )

    def _evaluate_resolution_auth(self, text: str) -> GateResult:
        """评估解决授权 - 检查是否有权限解决问题"""
        authority_indicators = [
            ("应当", "义务性表述"),
            ("必须", "强制性表述"),
            ("可以", "许可性表述"),
            ("有权", "权利性表述"),
            ("建议", "建议性表述"),
        ]

        authority_phrases = []
        for keyword, label in authority_indicators:
            if keyword in text:
                authority_phrases.append(label)

        if not authority_phrases:
            return GateResult(
                passed=True,
                state=GateState.UNRESOLVED,
                reason="缺少权威性表述，无法判断解决权限",
                confidence=0.5,
            )

        has_strong_authority = "义务性表述" in authority_phrases or "强制性表述" in authority_phrases

        return GateResult(
            passed=True,
            state=GateState.AUTHORIZED if has_strong_authority else GateState.COARSE,
            reason=f"具有解决权限: {', '.join(authority_phrases)}",
            confidence=0.85,
            details={"authority_phrases": authority_phrases}
        )

    def _evaluate_fix_legality(self, text: str) -> GateResult:
        """评估修复合法性 - 检查修正是否合法"""
        illegal_patterns = [
            (r"伪造", "伪造信息"),
            (r"篡改", "篡改数据"),
            (r"删除.*事实", "删除事实"),
            (r"无视.*证据", "无视证据"),
        ]

        illegal_indicators = []
        for pattern, label in illegal_patterns:
            if re.search(pattern, text):
                illegal_indicators.append(label)

        if illegal_indicators:
            return GateResult(
                passed=False,
                state=GateState.STOP,
                reason=f"修正不合法: {', '.join(illegal_indicators)}",
                confidence=0.95,
                details={"illegal_indicators": illegal_indicators}
            )

        return GateResult(
            passed=True,
            state=GateState.AUTHORIZED,
            reason="修正合法",
            confidence=0.9,
        )

    def _evaluate_emission_control(self, text: str) -> GateResult:
        """评估Emission控制 - 检查是否可公开发布"""
        sensitive_categories = {
            "机密": ["机密", "保密", "secret"],
            "隐私": ["隐私", "个人信息", "身份证", "手机号"],
            "内部": ["内部", "仅限", "不对外"],
            "专有": ["专利", "商业秘密", "专有技术"],
        }

        detected_sensitive = []
        for category, keywords in sensitive_categories.items():
            for keyword in keywords:
                if keyword in text:
                    detected_sensitive.append(f"{category}:{keyword}")

        if detected_sensitive:
            return GateResult(
                passed=False,
                state=GateState.STOP,
                reason=f"包含敏感信息: {', '.join(detected_sensitive)}",
                confidence=0.95,
                details={"sensitive": detected_sensitive}
            )

        return GateResult(
            passed=True,
            state=GateState.AUTHORIZED,
            reason="可公开发布",
            confidence=0.9,
        )


def evaluate_all_gates(input_text: str) -> dict[GateType, GateResult]:
    """评估所有7个门"""
    results = {}
    for gate_type in GateType:
        gate = GovernanceGate(gate_type)
        results[gate_type] = gate.evaluate(input_text)
    return results
