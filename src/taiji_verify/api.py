"""
Taiji Verify HTTP API Server

FastAPI服务，提供REST接口供其他语言/项目调用

启动方式:
    uvicorn taiji_verify.api:app --host 0.0.0.0 --port 8080

API端点:
    POST /verify          - 单文本验证
    POST /verify/batch    - 批量验证
    GET  /health          - 健康检查
    GET  /stats           - 统计信息
"""

from __future__ import annotations

import time
import asyncio
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dataclasses import dataclass, field

from taiji_verify.plugin import verify, batch_verify, VerifyResult


@dataclass
class Stats:
    """统计信息"""
    requests_total: int = 0
    requests_passed: int = 0
    requests_blocked: int = 0
    avg_latency_ms: float = 0.0
    total_latency_ms: float = 0.0

    def record(self, latency_ms: float, passed: bool):
        self.requests_total += 1
        self.total_latency_ms += latency_ms
        self.avg_latency_ms = self.total_latency_ms / self.requests_total
        if passed:
            self.requests_passed += 1
        else:
            self.requests_blocked += 1


stats = Stats()


class VerifyRequest(BaseModel):
    """验证请求"""
    text: str = Field(..., description="待验证的文本")
    ground_truth: Optional[str] = Field(None, description="标准答案/真值")
    context: Optional[dict] = Field(None, description="额外上下文")


class VerifyResponse(BaseModel):
    """验证响应"""
    verdict: str = Field(..., description="pass/conditional_pass/corrected/block/escalate")
    is_passing: bool = Field(..., description="是否通过")
    delta_s: Optional[float] = Field(None, description="阴阳距/相似度")
    risk_level: Optional[str] = Field(None, description="风险等级")
    failures: list = Field(default_factory=list, description="检测到的失败")
    processing_time_ms: int = Field(..., description="处理耗时")
    details: Optional[dict] = Field(None, description="完整详情")


class BatchVerifyRequest(BaseModel):
    """批量验证请求"""
    texts: list[str] = Field(..., description="待验证的文本列表")
    ground_truths: Optional[list[str]] = Field(None, description="标准答案列表")
    max_workers: int = Field(4, description="最大并发数")


class BatchVerifyResponse(BaseModel):
    """批量验证响应"""
    results: list[VerifyResponse] = Field(..., description="验证结果列表")
    total: int = Field(..., description="总数")
    passed: int = Field(..., description="通过数")
    processing_time_ms: int = Field(..., description="总处理耗时")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="版本号")


class StatsResponse(BaseModel):
    """统计信息响应"""
    requests_total: int = Field(..., description="总请求数")
    requests_passed: int = Field(..., description="通过数")
    requests_blocked: int = Field(..., description="拒绝数")
    pass_rate: float = Field(..., description="通过率")
    avg_latency_ms: float = Field(..., description="平均延迟")


def _get_failure_info(f) -> dict:
    mode = getattr(f, 'mode', None)
    return {
        "mode_id": mode.id if mode else str(f),
        "mode_name": mode.name if mode else str(f),
        "severity": getattr(f, 'severity', '') or (mode.severity if mode else ''),
        "details": getattr(f, 'details', ''),
        "location": getattr(f, 'location', ''),
    }


def result_to_response(result: VerifyResult) -> VerifyResponse:
    """将VerifyResult转换为API响应"""
    return VerifyResponse(
        verdict=result.verdict,
        is_passing=result.is_passing,
        delta_s=result.delta_s,
        risk_level=result.risk_level,
        failures=[_get_failure_info(f) for f in result.failures],
        processing_time_ms=result.processing_time_ms,
        details=result.details,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    print("🚀 Taiji Verify API 启动中...")
    yield
    print("👋 Taiji Verify API 关闭")


app = FastAPI(
    title="Taiji Verify API",
    description="太极验证引擎 - AI输出语义验证REST API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["系统"])
async def health_check():
    """健康检查"""
    return HealthResponse(status="healthy", version="2.0.0")


@app.get("/stats", response_model=StatsResponse, tags=["系统"])
async def get_stats():
    """获取统计信息"""
    pass_rate = 0.0
    if stats.requests_total > 0:
        pass_rate = stats.requests_passed / stats.requests_total

    return StatsResponse(
        requests_total=stats.requests_total,
        requests_passed=stats.requests_passed,
        requests_blocked=stats.requests_blocked,
        pass_rate=pass_rate,
        avg_latency_ms=stats.avg_latency_ms,
    )


@app.post("/verify", response_model=VerifyResponse, tags=["验证"])
async def verify_text(request: VerifyRequest):
    """
    验证单个文本

    支持两种模式：
    1. **仅文本验证** - 只传入text，检测幻觉/规则违规
    2. **相似度验证** - 同时传入text和ground_truth，计算ΔS
    """
    start_time = time.time()

    try:
        result = verify(
            text=request.text,
            ground_truth=request.ground_truth,
            context=request.context,
        )

        latency_ms = int((time.time() - start_time) * 1000)
        stats.record(latency_ms, result.is_passing)

        return result_to_response(result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")


@app.post("/verify/batch", response_model=BatchVerifyResponse, tags=["验证"])
async def verify_batch(request: BatchVerifyRequest):
    """
    批量验证多个文本

    适用于：
    - 批量质量检查
    - CI/CD流水线
    - 数据预处理
    """
    start_time = time.time()

    if len(request.texts) > 1000:
        raise HTTPException(status_code=400, detail="单次批量最多1000条")

    try:
        results = batch_verify(
            texts=request.texts,
            ground_truths=request.ground_truths,
            max_workers=request.max_workers,
        )

        responses = [result_to_response(r) for r in results]
        passed = sum(1 for r in results if r.is_passing)
        latency_ms = int((time.time() - start_time) * 1000)

        stats.requests_total += len(results)
        for r in results:
            if r.is_passing:
                stats.requests_passed += 1
            else:
                stats.requests_blocked += 1

        return BatchVerifyResponse(
            results=responses,
            total=len(results),
            passed=passed,
            processing_time_ms=latency_ms,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量验证失败: {str(e)}")


@app.post("/verify/sync", response_model=VerifyResponse, tags=["验证"])
async def verify_text_sync(request: VerifyRequest):
    """
    同步验证（等同于/verify）

    为兼容某些客户端设计
    """
    return await verify_text(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
