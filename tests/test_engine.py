"""
Engine Tests - 主引擎测试
"""

import pytest
from taiji_verify.engine import TaijiVerifyEngine, Verdict


class TestTaijiVerifyEngine:
    """主引擎测试"""

    def test_engine_initialization(self):
        """测试引擎初始化"""
        engine = TaijiVerifyEngine()
        assert engine.embedding_dim == 768

    def test_verify_text_only(self):
        """测试纯文本验证"""
        engine = TaijiVerifyEngine()
        response = engine.verify_text_only("碳排放权交易管理办法规定")
        assert isinstance(response.verdict, Verdict)
        assert response.verdict in [Verdict.PASS, Verdict.BLOCK, Verdict.CONDITIONAL_PASS]

    def test_verify_basic(self):
        """测试基础验证"""
        engine = TaijiVerifyEngine(enable_all_layers=False)
        response = engine.verify("碳排放权交易管理办法规定")
        assert isinstance(response.verdict, Verdict)

    def test_verify_full_pipeline(self):
        """测试完整流水线"""
        engine = TaijiVerifyEngine()
        response = engine.verify_full_pipeline(
            input_text="碳排放权交易平台应当建立",
            ground_truth="碳排放权交易平台应当建立完善的监管机制"
        )
        assert response.verdict in [Verdict.PASS, Verdict.BLOCK, Verdict.CONDITIONAL_PASS, Verdict.CORRECTED]

    def test_system_health(self):
        """测试系统健康状态"""
        engine = TaijiVerifyEngine()
        health = engine.system_health
        assert 'engine_version' in health
        assert 'layers_enabled' in health

    def test_verdict_enum(self):
        """测试判定枚举"""
        assert Verdict.PASS.value == "pass"
        assert Verdict.BLOCK.value == "block"
        assert Verdict.ESCALATE.value == "escalate"
