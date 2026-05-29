"""Engine Tests - 主引擎测试 - 完整覆盖率"""
import pytest
import numpy as np
from taiji_verify.engine import (
    TaijiVerifyEngine, Verdict, VerificationRequest, VerificationResponse,
)


class TestTaijiVerifyEngineInit:
    """引擎初始化测试"""

    def test_default_init(self):
        engine = TaijiVerifyEngine()
        assert engine.embedding_dim == 768
        assert engine.delta_s_calculator is not None
        assert engine.failure_detector is not None
        assert engine.compiler is not None

    def test_custom_init(self):
        engine = TaijiVerifyEngine(
            embedding_dim=512,
            delta_s_safe_threshold=0.5,
            enable_all_layers=True,
            enable_governance=True,
        )
        assert engine.embedding_dim == 512

    def test_basic_mode_init(self):
        engine = TaijiVerifyEngine(enable_all_layers=False)
        assert hasattr(engine, 'delta_s_calculator')
        assert hasattr(engine, 'failure_detector')


class TestVerdictEnum:
    """判定枚举测试"""

    def test_verdict_values(self):
        assert Verdict.PASS.value == "pass"
        assert Verdict.CONDITIONAL_PASS.value == "conditional_pass"
        assert Verdict.CORRECTED.value == "corrected"
        assert Verdict.BLOCK.value == "block"
        assert Verdict.ESCALATE.value == "escalate"

    def test_verdict_is_string(self):
        assert isinstance(Verdict.PASS, str)
        assert Verdict.PASS == "pass"


class TestVerificationRequest:
    """验证请求测试"""

    def test_request_creation(self):
        request = VerificationRequest(
            input_text="测试文本",
            ground_truth="标准答案",
            context={"key": "value"},
        )
        assert request.input_text == "测试文本"
        assert request.ground_truth == "标准答案"
        assert request.context["key"] == "value"

    def test_request_defaults(self):
        request = VerificationRequest(input_text="测试")
        assert request.ground_truth is None
        assert request.context is None
        assert request.embed_fn is None


class TestVerificationResponse:
    """验证响应测试"""

    def test_response_creation(self):
        response = VerificationResponse(verdict=Verdict.PASS)
        assert response.verdict == Verdict.PASS

    def test_is_passing(self):
        assert VerificationResponse(verdict=Verdict.PASS).is_passing is True
        assert VerificationResponse(verdict=Verdict.CONDITIONAL_PASS).is_passing is True
        assert VerificationResponse(verdict=Verdict.CORRECTED).is_passing is True
        assert VerificationResponse(verdict=Verdict.BLOCK).is_passing is False
        assert VerificationResponse(verdict=Verdict.ESCALATE).is_passing is False


class TestVerifyMethods:
    """验证方法测试"""

    def test_verify_text_only(self):
        engine = TaijiVerifyEngine()
        response = engine.verify_text_only("碳排放权交易管理办法规定")
        assert isinstance(response.verdict, Verdict)
        assert response.processing_time_ms >= 0

    def test_verify_basic_mode(self):
        engine = TaijiVerifyEngine(enable_all_layers=False)
        response = engine.verify("碳排放权交易管理办法规定")
        assert response.verdict in list(Verdict)
        assert 'mode' in response.metadata
        assert response.metadata['mode'] == 'basic'

    def test_verify_full_pipeline(self):
        engine = TaijiVerifyEngine()
        response = engine.verify_full_pipeline(
            input_text="碳排放权交易平台应当建立",
            ground_truth="碳排放权交易平台应当建立完善的监管机制",
        )
        assert response.verdict in list(Verdict)
        assert 'mode' in response.metadata

    def test_verify_with_context(self):
        engine = TaijiVerifyEngine()
        response = engine.verify(
            "测试文本",
            context={"source": "test", "timestamp": "2024-01-01"},
        )
        assert response.verdict in list(Verdict)


class TestSystemHealth:
    """系统健康测试"""

    def test_system_health_full_layers(self):
        engine = TaijiVerifyEngine(enable_all_layers=True)
        health = engine.system_health
        assert health['engine_version'].startswith('v2.2')
        assert 'layers_enabled' in health
        assert health['layers_enabled']['detection'] is True
        assert health['layers_enabled']['reasoning'] is True
        assert health['layers_enabled']['governance'] is True

    def test_system_health_basic_mode(self):
        engine = TaijiVerifyEngine(enable_all_layers=False)
        health = engine.system_health
        assert 'layers_enabled' in health


class TestDetectionLayer:
    """检测层测试"""

    def test_run_detection_layer(self):
        engine = TaijiVerifyEngine()
        result = engine._run_detection_layer("碳排放权交易管理办法规定碳排放权交易应当遵守")
        assert 'rule_result' in result
        assert 'consistency_result' in result
        assert 'hallucination_result' in result


class TestReasoningLayer:
    """推理层测试"""

    def test_run_reasoning_layer(self):
        engine = TaijiVerifyEngine()
        result = engine._run_reasoning_layer(
            "碳排放权交易管理办法",
            "碳排放权交易管理办法规定",
        )
        assert 'chain_result' in result
        assert 'firewall_result' in result

    def test_run_reasoning_layer_no_goal(self):
        engine = TaijiVerifyEngine()
        result = engine._run_reasoning_layer("碳排放权交易", None)
        assert 'chain_result' in result


class TestGovernanceLayer:
    """治理层测试"""

    def test_run_governance_layer(self):
        engine = TaijiVerifyEngine()
        result = engine._run_governance_layer("碳排放权交易管理办法规定")
        assert 'gate_results' in result
        assert 'twin_atlas_result' in result
        assert 'stopped' in result
        assert 'coarse' in result

    def test_run_governance_layer_stopped(self):
        engine = TaijiVerifyEngine()
        result = engine._run_governance_layer("机密信息泄漏")
        assert 'stopped' in result
        assert 'coarse' in result


class TestDiagnosisLayer:
    """诊断层测试"""

    def test_run_diagnosis_layer(self):
        engine = TaijiVerifyEngine()
        detection_result = {
            'rule_result': {'violations': []},
            'hallucination_result': None,
        }
        result = engine._run_diagnosis_layer("测试文本", detection_result)
        assert 'diagnosis' in result
        assert 'recommended_fixes' in result


class TestDeltaS:
    """阴阳距计算测试"""

    def test_run_delta_s(self):
        engine = TaijiVerifyEngine()

        def mock_embed(text):
            return np.random.randn(768)

        result = engine._run_delta_s(
            mock_embed,
            "碳排放权交易管理办法",
            "碳排放权交易管理办法规定",
        )
        assert result is not None
        assert hasattr(result, 'delta_s')


class TestVerdictComputation:
    """判定计算测试"""

    def test_compute_verdict_no_vectors_blocked(self):
        engine = TaijiVerifyEngine()
        detection_result = {'hallucination_result': None}
        reasoning_result = {'firewall_result': None}
        governance_result = {'stopped': True, 'coarse': False}
        verdict = engine._compute_verdict_no_vectors(
            detection_result, reasoning_result, governance_result
        )
        assert verdict == Verdict.BLOCK

    def test_compute_verdict_no_vectors_coarse(self):
        engine = TaijiVerifyEngine()
        verdict = engine._compute_verdict_no_vectors(
            {'hallucination_result': None},
            {'firewall_result': None},
            {'stopped': False, 'coarse': True},
        )
        assert verdict == Verdict.CONDITIONAL_PASS

    def test_compute_verdict_no_vectors_pass(self):
        engine = TaijiVerifyEngine()
        verdict = engine._compute_verdict_no_vectors(
            {'hallucination_result': None},
            {'firewall_result': None},
            {'stopped': False, 'coarse': False},
        )
        assert verdict == Verdict.PASS

    def test_compute_verdict_from_delta_s_safe(self):
        engine = TaijiVerifyEngine()
        from taiji_verify.delta_s import DeltaSResult, GateZone
        ds_result = DeltaSResult(
            delta_s=0.1,
            zone=GateZone.SAFE,
            cosine_similarity=0.95,
        )
        verdict = engine._compute_verdict_from_delta_s(ds_result)
        assert verdict == Verdict.PASS

    def test_compute_verdict_from_delta_s_danger(self):
        engine = TaijiVerifyEngine()
        from taiji_verify.delta_s import DeltaSResult, GateZone
        ds_result = DeltaSResult(
            delta_s=0.9,
            zone=GateZone.DANGER,
            cosine_similarity=0.1,
        )
        verdict = engine._compute_verdict_from_delta_s(ds_result)
        assert verdict == Verdict.BLOCK

    def test_compute_verdict_from_delta_s_risk(self):
        engine = TaijiVerifyEngine()
        from taiji_verify.delta_s import DeltaSResult, GateZone
        ds_result = DeltaSResult(
            delta_s=0.5,
            zone=GateZone.RISK,
            cosine_similarity=0.5,
        )
        verdict = engine._compute_verdict_from_delta_s(ds_result)
        assert verdict == Verdict.CONDITIONAL_PASS

    def test_compute_verdict_from_delta_s_transit(self):
        engine = TaijiVerifyEngine()
        from taiji_verify.delta_s import DeltaSResult, GateZone
        ds_result = DeltaSResult(
            delta_s=0.35,
            zone=GateZone.TRANSIT,
            cosine_similarity=0.65,
        )
        verdict = engine._compute_verdict_from_delta_s(ds_result)
        assert verdict == Verdict.CONDITIONAL_PASS


class TestAddMethods:
    """添加方法测试"""

    def test_add_rule(self):
        engine = TaijiVerifyEngine()
        from taiji_verify.detection.rule_engine import Rule

        class MockRule:
            id = "mock_rule_001"
            pattern = "test_pattern"
            severity = "LOW"
            fix_suggestion = "fix_test"

        engine.add_rule(MockRule())

    def test_add_knowledge_entry(self):
        engine = TaijiVerifyEngine()
        engine.add_knowledge_entry(
            "entry_001",
            "碳排放权交易管理办法",
            ["碳排放", "交易"],
        )


class TestVerifyWithVectors:
    """向量验证测试"""

    def test_verify_with_vectors(self):
        engine = TaijiVerifyEngine()
        input_vec = np.random.randn(768)
        ground_vec = np.random.randn(768)
        response = engine.verify_with_vectors(input_vec, ground_vec)
        assert response.verdict in list(Verdict)
        assert response.delta_s_result is not None


class TestLayerInitialization:
    """层初始化测试"""

    def test_init_detection_layer(self):
        engine = TaijiVerifyEngine()
        engine._init_detection_layer()
        assert hasattr(engine, 'rule_engine')
        assert hasattr(engine, 'consistency_checker')
        assert hasattr(engine, 'hallucination_detector')

    def test_init_reasoning_layer(self):
        engine = TaijiVerifyEngine()
        engine._init_reasoning_layer()
        assert hasattr(engine, 'seven_step_chain')
        assert hasattr(engine, 'coupler')
        assert hasattr(engine, 'semantic_firewall')

    def test_init_diagnosis_layer(self):
        engine = TaijiVerifyEngine()
        engine._init_diagnosis_layer()
        assert hasattr(engine, 'fix_map')
        assert hasattr(engine, 'troubleshooting_atlas')

    def test_init_governance_layer(self):
        engine = TaijiVerifyEngine()
        engine._init_governance_layer()
        assert hasattr(engine, 'twin_atlas')

    def test_init_execution_layer(self):
        engine = TaijiVerifyEngine()
        engine._init_execution_layer()
        assert hasattr(engine, 'goal_compiler')
        assert hasattr(engine, 'leak_auditor')
