"""
Taiji Verify SDK - 简化插件接口

一行代码集成AI输出验证

使用方式:
    from taiji_verify import verify

    result = verify("AI输出文本", ground_truth="标准答案")
    if result.is_passing:
        print("验证通过")
"""

from __future__ import annotations

import os
import asyncio
from typing import Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from taiji_verify.engine import (
    TaijiVerifyEngine,
    VerificationResponse,
    Verdict,
)

_executor: Optional[ThreadPoolExecutor] = None
_engine: Optional[TaijiVerifyEngine] = None


def _get_engine() -> TaijiVerifyEngine:
    global _engine
    if _engine is None:
        embedding_dim = int(os.environ.get("TAIJI_EMBEDDING_DIM", "768"))
        delta_threshold = float(os.environ.get("TAIJI_DELTA_THRESHOLD", "0.6"))
        _engine = TaijiVerifyEngine(
            embedding_dim=embedding_dim,
            delta_s_safe_threshold=delta_threshold,
        )
    return _engine


@dataclass
class VerifyResult:
    """验证结果（简化版）"""

    verdict: str
    is_passing: bool
    delta_s: Optional[float] = None
    risk_level: Optional[str] = None
    failures: list = None
    processing_time_ms: int = 0
    _response: Optional[VerificationResponse] = None

    def __post_init__(self):
        if self.failures is None:
            self.failures = []

    def _get_failure_info(self, f) -> dict:
        mode = getattr(f, 'mode', None)
        return {
            "mode_id": mode.id if mode else str(f),
            "mode_name": mode.name if mode else str(f),
            "severity": getattr(f, 'severity', '') or (mode.severity if mode else ''),
            "details": getattr(f, 'details', ''),
            "location": getattr(f, 'location', ''),
        }

    @property
    def details(self) -> dict:
        """返回完整详情"""
        if self._response:
            return {
                "verdict": self.verdict,
                "is_passing": self.is_passing,
                "delta_s": self.delta_s,
                "risk_level": self.risk_level,
                "failures": [self._get_failure_info(f) for f in self._response.failure_detections],
                "processing_time_ms": self.processing_time_ms,
                "detection_result": self._response.detection_result,
                "governance_result": self._response.governance_result,
            }
        return {}

    def __str__(self) -> str:
        status = "✅ 通过" if self.is_passing else "❌ 拒绝"
        return f"Taiji Verify: {status} | ΔS={self.delta_s:.3f} | {self.processing_time_ms}ms"


def verify(
    text: str,
    ground_truth: Optional[str] = None,
    context: Optional[dict] = None,
    embed_fn: Optional[callable] = None,
) -> VerifyResult:
    """
    一行验证AI输出

    Args:
        text: 待验证的AI输出文本
        ground_truth: 标准答案/真值（可选，用于ΔS计算）
        context: 额外上下文信息
        embed_fn: 自定义嵌入函数（可选）

    Returns:
        VerifyResult: 验证结果

    Example:
        from taiji_verify import verify

        result = verify(
            "碳排放权交易管理办法规定...",
            ground_truth="碳排放权交易管理办法规定...",
        )
        if result.is_passing:
            print("验证通过")
    """
    engine = _get_engine()

    response = engine.verify(
        input_text=text,
        ground_truth=ground_truth,
        context=context,
        embed_fn=embed_fn,
    )

    delta_s = None
    risk_level = None
    if response.delta_s_result:
        delta_s = response.delta_s_result.cosine_similarity
        risk_level = str(response.delta_s_result.gate_zone.value) if hasattr(response.delta_s_result.gate_zone, "value") else str(response.delta_s_result.gate_zone)

    return VerifyResult(
        verdict=response.verdict.value,
        is_passing=response.is_passing,
        delta_s=delta_s,
        risk_level=risk_level,
        failures=response.failure_detections,
        processing_time_ms=response.processing_time_ms,
        _response=response,
    )


async def verify_async(
    text: str,
    ground_truth: Optional[str] = None,
    context: Optional[dict] = None,
) -> VerifyResult:
    """
    异步验证AI输出（用于Web/API服务）

    Args:
        text: 待验证的AI输出文本
        ground_truth: 标准答案/真值（可选）
        context: 额外上下文信息

    Returns:
        VerifyResult: 验证结果

    Example:
        import asyncio
        from taiji_verify import verify_async

        async def main():
            result = await verify_async("AI输出", "标准答案")
            print(result)
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        verify,
        text,
        ground_truth,
        context,
    )


def batch_verify(
    texts: list[str],
    ground_truths: Optional[list[str]] = None,
    max_workers: int = 4,
) -> list[VerifyResult]:
    """
    批量验证多个文本

    Args:
        texts: 待验证的文本列表
        ground_truths: 标准答案列表（与texts一一对应）
        max_workers: 最大并发数

    Returns:
        list[VerifyResult]: 验证结果列表

    Example:
        from taiji_verify import batch_verify

        results = batch_verify(
            ["文本1", "文本2", "文本3"],
            ["答案1", "答案2", "答案3"],
        )
        for r in results:
            print(r)
    """
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=max_workers)

    ground_truths = ground_truths or [None] * len(texts)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(verify, text, gt)
            for text, gt in zip(texts, ground_truths)
        ]
        return [f.result() for f in futures]


def reset_engine():
    """重置引擎（用于配置变更后）"""
    global _engine
    _engine = None


class TaijiVerify:
    """
    面向对象的SDK接口

    Example:
        from taiji_verify import TaijiVerify

        verifier = TaijiVerify()
        result = verifier.verify("AI输出", "标准答案")

        # 自定义配置
        verifier2 = TaijiVerify(
            embedding_dim=512,
            delta_threshold=0.5,
        )
    """

    def __init__(
        self,
        embedding_dim: int = 768,
        delta_threshold: float = 0.6,
        enable_all_layers: bool = True,
        enable_governance: bool = True,
    ):
        self._engine = TaijiVerifyEngine(
            embedding_dim=embedding_dim,
            delta_s_safe_threshold=delta_threshold,
            enable_all_layers=enable_all_layers,
            enable_governance=enable_governance,
        )

    def verify(
        self,
        text: str,
        ground_truth: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> VerifyResult:
        """验证单个文本"""
        response = self._engine.verify(
            input_text=text,
            ground_truth=ground_truth,
            context=context,
        )
        return self._to_result(response)

    async def verify_async(
        self,
        text: str,
        ground_truth: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> VerifyResult:
        """异步验证"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.verify,
            text,
            ground_truth,
            context,
        )

    def _to_result(self, response: VerificationResponse) -> VerifyResult:
        delta_s = None
        risk_level = None
        if response.delta_s_result:
            delta_s = response.delta_s_result.cosine_similarity
            risk_level = str(response.delta_s_result.gate_zone.value) if hasattr(response.delta_s_result.gate_zone, "value") else str(response.delta_s_result.gate_zone)

        return VerifyResult(
            verdict=response.verdict.value,
            is_passing=response.is_passing,
            delta_s=delta_s,
            risk_level=risk_level,
            failures=response.failure_detections,
            processing_time_ms=response.processing_time_ms,
            _response=response,
        )
