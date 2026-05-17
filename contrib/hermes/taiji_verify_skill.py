"""
Taiji Verify Skill for Hermes Agent

将太极验证集成到Hermes Agent的Skill系统中

使用方法:
    1. 将此文件放到 skills/ 目录
    2. Hermes会自动发现并注册此Skill
    3. 使用 /taiji-verify <文本> 调用

或通过对话:
    "请用太极验证检查这个回答"
"""

from typing import Optional
from hermes_agent import skill, tool, ToolContext

try:
    from taiji_verify import verify, TaijiVerify, VerifyResult
    TAIJI_AVAILABLE = True
except ImportError:
    TAIJI_AVAILABLE = False
    print("警告: taiji-verify未安装。运行: pip install taiji-verify")


@skill(
    name="taiji-verify",
    description="太极验证 - 检查AI输出是否可信，无幻觉、无逻辑跳跃、无事实冲突",
    aliases=["verify", "验证", "tverify"],
    examples=[
        "/taiji-verify 碳排放量减少了20%",
        "请验证这个回答是否正确",
        "检查输出是否有幻觉",
    ],
)
def taiji_verify_skill(text: str, context: Optional[ToolContext] = None) -> dict:
    """
    使用太极验证引擎检查文本

    Args:
        text: 要验证的文本
        context: Hermes工具上下文

    Returns:
        验证结果字典
    """
    if not TAIJI_AVAILABLE:
        return {
            "error": "taiji-verify未安装",
            "hint": "运行: pip install taiji-verify",
        }

    result = verify(text)

    return {
        "verdict": result.verdict,
        "is_passing": result.is_passing,
        "delta_s": result.delta_s,
        "risk_level": result.risk_level,
        "failures": [
            {
                "mode": getattr(f, 'mode_name', str(f)),
                "details": getattr(f, 'details', ''),
            }
            for f in result.failures
        ],
        "processing_time_ms": result.processing_time_ms,
    }


@tool(
    name="taiji_verify",
    description="验证AI输出是否可信，返回置信度评估",
)
def taiji_verify_tool(text: str, ground_truth: Optional[str] = None) -> dict:
    """
    工具函数：验证文本

    Args:
        text: 待验证文本
        ground_truth: 标准答案（可选）

    Returns:
        验证结果
    """
    if not TAIJI_AVAILABLE:
        return {"error": "taiji-verify未安装"}

    verifier = TaijiVerify()
    result = verifier.verify(text, ground_truth)

    return {
        "verdict": result.verdict,
        "is_passing": result.is_passing,
        "confidence": result.delta_s,
        "summary": f"判定: {result.verdict}, ΔS: {result.delta_s:.3f}" if result.delta_s else f"判定: {result.verdict}",
    }


@tool(
    name="taiji_verify_batch",
    description="批量验证多个文本",
)
def taiji_verify_batch_tool(texts: list[str]) -> dict:
    """
    工具函数：批量验证

    Args:
        texts: 文本列表

    Returns:
        批量验证结果
    """
    if not TAIJI_AVAILABLE:
        return {"error": "taiji-verify未安装"}

    from taiji_verify import batch_verify
    results = batch_verify(texts)

    passed = sum(1 for r in results if r.is_passing)

    return {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": passed / len(results) if results else 0,
        "results": [
            {
                "verdict": r.verdict,
                "is_passing": r.is_passing,
            }
            for r in results
        ],
    }


if __name__ == "__main__":
    if TAIJI_AVAILABLE:
        print("Taiji Verify Skill已加载")
        print("使用方式:")
        print("  /taiji-verify <文本>")
        print("  '请验证这个回答'")
    else:
        print("警告: taiji-verify未安装")
        print("运行: pip install taiji-verify")
