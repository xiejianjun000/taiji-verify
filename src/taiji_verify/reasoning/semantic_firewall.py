"""
Semantic Firewall - 语义防火墙

使用文本相似度计算ΔS，而非假embedding
输入→ΔS→观变→坤守→巽调→复归→通过/拒绝/修正
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from taiji_verify.kun_guard import KunGuard
    from taiji_verify.xun_tune import XunTune
    from taiji_verify.fu_return import FuReturn


@dataclass
class FirewallResult:
    """防火墙结果"""

    decision: str
    delta_s: Optional[float] = None
    step_results: dict = field(default_factory=dict)
    corrections: list = field(default_factory=list)


class SemanticFirewall:
    """
    语义防火墙 - 使用文本相似度计算ΔS

    Usage::
        firewall = SemanticFirewall()
        result = firewall.check("正确的环境保护法分析")
        assert result.decision in ["PASS", "MODIFIED"]
    """

    REFERENCE_TERMS = [
        "正确",
        "标准",
        "合法",
        "有效",
        "符合",
        "规范",
        "事实",
        "法律",
        "规定",
        "政策",
        "真实",
        "准确",
        "可靠",
    ]

    def __init__(
        self,
        delta_s_threshold: float = 0.7,
        block_threshold: float = 0.9,
    ):
        self.delta_s_threshold = delta_s_threshold
        self.block_threshold = block_threshold

        self._kun_guard: Optional["KunGuard"] = None
        self._xun_tune: Optional["XunTune"] = None
        self._fu_return: Optional["FuReturn"] = None

    def _init_modules(self) -> None:
        """延迟初始化模块"""
        if self._kun_guard is None:
            from taiji_verify.kun_guard import KunGuard

            self._kun_guard = KunGuard()
        if self._xun_tune is None:
            from taiji_verify.xun_tune import XunTune

            self._xun_tune = XunTune()
        if self._fu_return is None:
            from taiji_verify.fu_return import FuReturn

            self._fu_return = FuReturn()

    def check(self, text: str) -> FirewallResult:
        """检查文本"""
        self._init_modules()

        delta_s = self._compute_delta_s_from_text(text)

        if delta_s >= self.block_threshold:
            return FirewallResult(
                decision="BLOCK",
                delta_s=delta_s,
                step_results={"delta_s": delta_s},
            )

        if delta_s >= self.delta_s_threshold:
            return FirewallResult(
                decision="MODIFIED",
                delta_s=delta_s,
                step_results={"delta_s": delta_s},
                corrections=["建议修正语义偏差"],
            )

        return FirewallResult(
            decision="PASS",
            delta_s=delta_s,
            step_results={"delta_s": delta_s},
        )

    def check_with_pipeline(self, text: str) -> FirewallResult:
        """带完整流水线的检查"""
        self._init_modules()

        delta_s = self._compute_delta_s_from_text(text)

        guan_result = self._guan_observe(text, delta_s)
        kun_result = self._kun_guard_check(text, delta_s)
        fu_result = self._fu_return_check(delta_s)

        step_results = {
            "delta_s": delta_s,
            "guan_observe": guan_result,
            "kun_guard": kun_result,
            "fu_return": fu_result,
        }

        corrections = []
        if kun_result.get("correction_needed"):
            corrections.append("坤守修正")

        if delta_s >= self.block_threshold or fu_result.get("crash_detected"):
            decision = "BLOCK"
        elif delta_s >= self.delta_s_threshold or corrections:
            decision = "MODIFIED"
        else:
            decision = "PASS"

        return FirewallResult(
            decision=decision,
            delta_s=delta_s,
            step_results=step_results,
            corrections=corrections,
        )

    def _compute_delta_s_from_text(self, text: str) -> float:
        """
        使用文本相似度计算ΔS

        基于以下因素计算：
        1. 正面术语匹配度
        2. 负面模式检测
        3. 可疑模式检测
        """
        positive_score = 0.0
        negative_score = 0.0

        for term in self.REFERENCE_TERMS:
            if term in text:
                positive_score += 0.1

        suspicious_patterns = [
            (r"GB\d{5,}", 0.3, "可疑标准编号"),
            (r"\d{4,}年\d{1,2}月", 0.2, "可疑日期格式"),
            (r"据.*报道", 0.2, "无来源引用"),
            (r"研究表明", 0.15, "未验证声明"),
            (r"据说", 0.25, "未经证实"),
            (r"可能.*是", 0.1, "不确定性过高"),
        ]

        import re

        for pattern, score, label in suspicious_patterns:
            if re.search(pattern, text):
                negative_score += score

        contradiction_indicators = [
            ("是", "不是"),
            ("有", "没有"),
            ("可以", "不可以"),
            ("必须", "不必"),
            ("正确", "错误"),
        ]
        for pos, neg in contradiction_indicators:
            if pos in text and neg in text:
                negative_score += 0.25
                break

        positive_score = min(positive_score, 0.6)
        negative_score = min(negative_score, 0.8)

        delta_s = 0.3 + negative_score - positive_score * 0.5

        return max(0.0, min(1.0, delta_s))

    def _guan_observe(self, text: str, delta_s: float) -> dict:
        """观变"""
        lambda_observe = 1.0 - delta_s
        stability = lambda_observe * 0.9

        return {
            "observed": True,
            "stability": stability,
            "lambda_observe": lambda_observe,
        }

    def _kun_guard_check(self, text: str, delta_s: float) -> dict:
        """坤守"""
        if self._kun_guard is None:
            self._init_modules()

        hazard, needs_block = self._kun_guard.check_hazard(delta_s)

        return {
            "hazard_level": hazard.value if hasattr(hazard, "value") else "LOW",
            "correction_needed": delta_s > 0.6,
            "hazard_score": hazard.value if hasattr(hazard, "value") else "LOW",
        }

    def _fu_return_check(self, delta_s: float) -> dict:
        """复归"""
        if self._fu_return is None:
            self._init_modules()

        import numpy as np

        state_history = [np.array([delta_s])]
        lyapunov = self._fu_return.compute_lyapunov_exponent(
            state_history=state_history, delta_t=0.1
        )
        recovery_state = self._fu_return.detect_crash(lyapunov=lyapunov, residual=delta_s)

        return {
            "stable": recovery_state.value in ["normal", "recovered"],
            "crash_detected": delta_s > 0.9,
            "recovery_state": recovery_state.value,
        }
