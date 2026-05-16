"""TaijiVerifyEngine 太极验证引擎测试"""
import numpy as np
import pytest
from numpy.linalg import norm

class TestEngine:
    def test_engine_initialization(self):
        from taiji_verify.engine import TaijiVerifyEngine
        engine = TaijiVerifyEngine()
        assert engine is not None

    def test_verify_safe_input(self):
        from taiji_verify.engine import TaijiVerifyEngine, VerificationRequest
        engine = TaijiVerifyEngine()
        request = VerificationRequest(
            input_text="这是一个正常的测试输入",
            ground_truth="这是预期的正确输出",
            context={'task': 'test'}
        )
        result = engine.verify(request)
        assert result.verdict is not None

    def test_engine_has_all_components(self):
        from taiji_verify.engine import TaijiVerifyEngine
        engine = TaijiVerifyEngine()
        assert hasattr(engine, 'delta_s_calculator')
        assert hasattr(engine, 'kun_guard')
        assert hasattr(engine, 'qian_advance')
        assert hasattr(engine, 'fu_return')
        assert hasattr(engine, 'xun_tune')
        assert hasattr(engine, 'compiler')

    def test_verdict_enum(self):
        from taiji_verify.engine import Verdict
        assert Verdict.PASS is not None
        assert Verdict.BLOCK is not None
        assert Verdict.CORRECTED is not None

    def test_verification_request(self):
        from taiji_verify.engine import VerificationRequest
        req = VerificationRequest(
            input_text="test",
            ground_truth="expected",
            context={"key": "value"}
        )
        assert req.input_text == "test"
        assert req.ground_truth == "expected"
        assert req.context["key"] == "value"
