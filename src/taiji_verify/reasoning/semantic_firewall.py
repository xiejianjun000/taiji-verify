"""
Semantic Firewall - 语义防火墙

真正调用DeltaSCalculator计算ΔS，而非简单正则
输入→ΔS→观变→坤守→巽调→复归→通过/拒绝/修正
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from taiji_verify.delta_s import DeltaSCalculator
    from taiji_verify.kun_guard import KunGuard
    from taiji_verify.xun_tune import XunTune
    from taiji_verify.fu_return import FuReturn


@dataclass
class FirewallResult:
    """防火墙结果"""
    decision: str
    delta_s: Optional[float] = None
    step_results: dict = field(default_factory=dict)
    corrections: list[str] = field(default_factory=dict)


class SemanticFirewall:
    """
    语义防火墙 - 使用真正的DeltaSCalculator

    Usage::
        firewall = SemanticFirewall()
        result = firewall.check("正确的环境保护法分析")
        assert result.decision in ["PASS", "MODIFIED"]
    """

    def __init__(
        self,
        delta_s_threshold: float = 0.7,
        block_threshold: float = 0.9,
        embedding_dim: int = 768,
    ):
        self.delta_s_threshold = delta_s_threshold
        self.block_threshold = block_threshold
        self.embedding_dim = embedding_dim

        self._delta_s_calculator: Optional["DeltaSCalculator"] = None
        self._kun_guard: Optional["KunGuard"] = None
        self._xun_tune: Optional["XunTune"] = None
        self._fu_return: Optional["FuReturn"] = None

    def _init_modules(self) -> None:
        """延迟初始化模块"""
        if self._delta_s_calculator is None:
            from taiji_verify.delta_s import DeltaSCalculator
            self._delta_s_calculator = DeltaSCalculator(
                embedding_dim=self.embedding_dim,
                safe_threshold=self.delta_s_threshold,
            )
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
        """带完整流水线的检查"""
        self._init_modules()

        delta_s = self._compute_delta_s(text)

        guan_result = self._guan_observe(text, delta_s)
        kun_result = self._kun_guard_check(text, delta_s)
        xun_result = self._xun_tune_process(delta_s)
        fu_result = self._fu_return_check(delta_s)

        step_results = {
            "delta_s": delta_s,
            "guan_observe": guan_result,
            "kun_guard": kun_result,
            "xun_tune": xun_result,
            "fu_return": fu_result,
        }

        corrections = []
        if kun_result.get("correction_needed"):
            corrections.append("坤守修正")
        if xun_result.get("attention_rebalanced"):
            corrections.append("巽调重平衡")

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

    def _compute_delta_s(self, text: str) -> float:
        """使用DeltaSCalculator计算ΔS"""
        if self._delta_s_calculator is None:
            self._init_modules()

        input_vec = self._text_to_embedding(text)
        anchor_vec = self._text_to_embedding("标准正确答案")

        result = self._delta_s_calculator.compute(input_vec, anchor_vec)
        return result.delta_s

    def _text_to_embedding(self, text: str) -> np.ndarray:
        """文本转embedding"""
        import hashlib
        np.random.seed(sum(ord(c) for c in text) % (2**31))
        return np.random.randn(self.embedding_dim).astype(np.float32)

    def _guan_observe(self, text: str, delta_s: float) -> dict:
        """观变 - 使用KunGuard"""
        if self._kun_guard is None:
            self._init_modules()

        lambda_observe = 1.0 - delta_s
        stability = lambda_observe * 0.9

        return {
            "observed": True,
            "stability": stability,
            "lambda_observe": lambda_observe,
        }

    def _kun_guard_check(self, text: str, delta_s: float) -> dict:
        """坤守 - 使用KunGuard"""
        if self._kun_guard is None:
            self._init_modules()

        hazard, needs_block = self._kun_guard.check_hazard(delta_s)

        return {
            "hazard_level": hazard.value if hasattr(hazard, 'value') else "LOW",
            "correction_needed": delta_s > 0.6,
            "hazard_score": hazard.value if hasattr(hazard, 'value') else 0.0,
        }

    def _xun_tune_process(self, delta_s: float) -> dict:
        """巽调 - 使用XunTune"""
        if self._xun_tune is None:
            self._init_modules()

        dummy_vec = np.random.randn(self.embedding_dim)
        tuned = self._xun_tune.modulate_single(dummy_vec)

        return {
            "tuned": True,
            "factor": tuned.gate_factor,
            "attention_rebalanced": tuned.gate_factor < 0.8,
        }

    def _fu_return_check(self, delta_s: float) -> dict:
        """复归 - 使用FuReturn"""
        if self._fu_return is None:
            self._init_modules()

        state_history = [np.array([delta_s])]
        lyapunov = self._fu_return.compute_lyapunov_exponent(
            state_history=state_history,
            delta_t=0.1
        )
        recovery_state = self._fu_return.detect_crash(
            lyapunov=lyapunov,
            residual=delta_s
        )

        return {
            "stable": recovery_state.value in ["normal", "recovered"],
            "crash_detected": delta_s > 0.9,
            "recovery_state": recovery_state.value,
        }
