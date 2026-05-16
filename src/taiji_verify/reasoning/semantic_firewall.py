"""
Semantic Firewall - 语义防火墙

输入→ΔS→观变→坤守→巽调→复归→通过/拒绝/修正
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FirewallResult:
    """防火墙结果"""
    decision: str
    delta_s: Optional[float] = None
    step_results: dict = field(default_factory=dict)
    corrections: list[str] = field(default_factory=list)


class SemanticFirewall:
    """
    语义防火墙

    Usage::
        firewall = SemanticFirewall()
        result = firewall.check("正确的环境保护法分析")
        assert result.decision in ["PASS", "MODIFIED"]
    """

    def __init__(
        self,
        delta_s_threshold: float = 0.7,
        block_threshold: float = 0.9,
    ):
        self.delta_s_threshold = delta_s_threshold
        self.block_threshold = block_threshold

    def check(self, text: str) -> FirewallResult:
        """检查文本"""
        delta_s = self._compute_delta_s(text)

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
        """带流水线的检查"""
        delta_s = self._compute_delta_s(text)
        guan_result = self._guan_observe(text)
        kun_result = self._kun_guard(text)
        xun_result = self._xun_tune(text)
        fu_result = self._fu_return(text)

        step_results = {
            "delta_s": delta_s,
            "guan_observe": guan_result,
            "kun_guard": kun_result,
            "xun_tune": xun_result,
            "fu_return": fu_result,
        }

        if delta_s >= self.block_threshold:
            decision = "BLOCK"
        elif delta_s >= self.delta_s_threshold:
            decision = "MODIFIED"
        else:
            decision = "PASS"

        return FirewallResult(
            decision=decision,
            delta_s=delta_s,
            step_results=step_results,
        )

    def _compute_delta_s(self, text: str) -> float:
        """计算ΔS"""
        import re
        suspicious_patterns = [
            r'GB\d{5,}',
            r'\d{4,}年\d{1,2}月',
            r'据.*报道',
            r'研究表明',
        ]
        score = 0.0
        for pattern in suspicious_patterns:
            if re.search(pattern, text):
                score += 0.2
        return min(score, 1.0)

    def _guan_observe(self, text: str) -> dict:
        """观变"""
        return {"observed": True, "stability": 0.8}

    def _kun_guard(self, text: str) -> dict:
        """坤守"""
        return {"guard_active": True, "residual": 0.2}

    def _xun_tune(self, text: str) -> dict:
        """巽调"""
        return {"tuned": True, "factor": 0.9}

    def _fu_return(self, text: str) -> dict:
        """复归"""
        return {"stable": True, "lyapunov": 0.1}
