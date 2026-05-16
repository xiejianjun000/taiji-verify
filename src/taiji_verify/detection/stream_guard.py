"""
Stream Guard - 流式守卫

对应 ZeroTokenGuard 的 Python 实现

功能:
- 缓冲区累积token，达阈值批量检测
- 支持流式实时场景
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GuardConfig:
    """守卫配置"""
    token_threshold: int = 100
    check_interval: int = 50


@dataclass
class GuardResult:
    """守卫结果"""
    detected: bool
    risk_level: str = "low"
    details: dict = field(default_factory=dict)


class StreamGuard:
    """
    流式守卫

    Usage::
        guard = StreamGuard(token_threshold=100)
        guard.add_tokens("今天天气")
        guard.add_tokens("很好")
        if guard.current_tokens >= guard.token_threshold:
            result = guard.check_batch()
    """

    def __init__(
        self,
        token_threshold: int = 100,
        check_interval: int = 50,
    ):
        self.token_threshold = token_threshold
        self.check_interval = check_interval
        self._buffer: list[str] = []
        self._context: str = ""
        self._total_tokens: int = 0

    @property
    def current_tokens(self) -> int:
        """当前token数"""
        return self._total_tokens

    @property
    def context(self) -> str:
        """上下文"""
        return self._context

    def add_tokens(self, text: str) -> int:
        """添加token"""
        self._buffer.append(text)
        tokens = self._estimate_tokens(text)
        self._total_tokens += tokens
        return tokens

    def set_context(self, context: str) -> None:
        """设置上下文"""
        self._context = context

    def check_batch(self) -> GuardResult:
        """批量检查"""
        if not self._buffer:
            return GuardResult(detected=False)

        combined_text = "".join(self._buffer)
        risk = self._assess_risk(combined_text)

        return GuardResult(
            detected=risk > 0.5,
            risk_level="high" if risk > 0.5 else "low",
            details={
                'token_count': self._total_tokens,
                'buffer_size': len(self._buffer),
                'risk_score': risk,
            },
        )

    def flush(self) -> None:
        """清空缓冲区"""
        self._buffer.clear()
        self._total_tokens = 0

    def _estimate_tokens(self, text: str) -> int:
        """估算token数（简单实现）"""
        import re
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        return chinese_chars + english_words

    def _assess_risk(self, text: str) -> float:
        """评估风险"""
        suspicious_count = 0
        import re
        if re.search(r'GB\d{5,}', text):
            suspicious_count += 1
        if re.search(r'据.*报道', text):
            suspicious_count += 1
        return min(suspicious_count * 0.3, 1.0)
