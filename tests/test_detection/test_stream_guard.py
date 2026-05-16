"""
Stream Guard Tests
"""

import pytest
from taiji_verify.detection.stream_guard import StreamGuard, GuardConfig, GuardResult


class TestStreamGuard:
    """流式守卫测试"""

    def test_stream_guard_initialization(self):
        """测试流式守卫初始化"""
        guard = StreamGuard(token_threshold=100, check_interval=50)
        assert guard.token_threshold == 100
        assert guard.current_tokens == 0

    def test_add_tokens_and_check(self):
        """测试添加token和检查"""
        guard = StreamGuard(token_threshold=10, check_interval=5)
        tokens = guard.add_tokens("今天天气")
        assert tokens > 0
        guard.add_tokens("很好")
        if guard.current_tokens >= guard.token_threshold:
            result = guard.check_batch()
            assert result is not None

    def test_stream_guard_context(self):
        """测试上下文设置"""
        guard = StreamGuard(token_threshold=20)
        guard.set_context("碳排放权交易")
        assert "碳排放权交易" in guard.context

    def test_flush(self):
        """测试清空缓冲区"""
        guard = StreamGuard(token_threshold=100)
        guard.add_tokens("测试内容")
        guard.flush()
        assert guard.current_tokens == 0

    def test_guard_result(self):
        """测试守卫结果"""
        guard = StreamGuard(token_threshold=1)
        guard.add_tokens("测试")
        result = guard.check_batch()
        assert isinstance(result, GuardResult)
