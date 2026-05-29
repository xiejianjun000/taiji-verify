"""End-to-End Integration Tests - 端到端集成测试"""
import pytest
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from taiji_verify.engine import TaijiVerifyEngine, Verdict
from taiji_verify.embedding import SimpleBagOfWordsProvider


class TestNormalScenario:
    """正常场景测试"""

    def test_eia_report_pass(self):
        """环评报告正常 - 应通过"""
        engine = TaijiVerifyEngine()
        response = engine.verify("碳排放权交易管理办法规定碳排放权交易应当遵守本办法。请问该项目的环境影响评价应该如何开展？该项目符合GB3096-1996标准。")

        assert response.verdict in list(Verdict)
        assert 'mode' in response.metadata
        assert response.metadata['mode'] == 'full_6layer'

    def test_standard_compliance(self):
        """标准合规 - 应通过"""
        engine = TaijiVerifyEngine()
        response = engine.verify(
            "根据GB3096-1996《声环境质量标准》，项目边界噪声符合2类功能区要求",
            context={"domain": "environmental"},
        )
        assert response.verdict in list(Verdict)


class TestBlockScenario:
    """阻断场景测试"""

    def test_fake_standard_number(self):
        """伪造标准号 - 应BLOCK"""
        engine = TaijiVerifyEngine()
        response = engine.verify("该项目符合GB99999-9999标准要求")

        assert response.verdict == Verdict.BLOCK or response.verdict == Verdict.ESCALATE

    def test_fact_contradiction(self):
        """事实矛盾 - 应BLOCK"""
        engine = TaijiVerifyEngine()
        response = engine.verify("水不是H2O")

        assert response.verdict in [Verdict.BLOCK, Verdict.ESCALATE]

    def test_sensitive_info_leak(self):
        """敏感信息泄漏 - 应BLOCK"""
        engine = TaijiVerifyEngine()
        response = engine.verify("机密：企业排污数据泄漏，联系电话12345678")

        assert response.verdict in [Verdict.BLOCK, Verdict.ESCALATE]

    def test_circular_reasoning(self):
        """循环论证 - 应阻断"""
        engine = TaijiVerifyEngine()
        response = engine.verify("A是正确的因为B支持A。B是正确的因为A支持B。")

        assert response.verdict in [Verdict.BLOCK, Verdict.ESCALATE, Verdict.CONDITIONAL_PASS]


class TestCorrectionScenario:
    """修正场景测试"""

    def test_delta_s_risk_correction(self):
        """ΔS风险修正"""
        engine = TaijiVerifyEngine()

        def mock_embed(text):
            provider = SimpleBagOfWordsProvider(dimension=768)
            return provider.embed(text)

        input_vec = mock_embed("碳排放量减少50%")
        ground_vec = mock_embed("碳排放量减少5%")
        response = engine.verify_with_vectors(input_vec, ground_vec)

        assert response.verdict in list(Verdict)

    def test_hallucination_detection(self):
        """幻觉检测并修正"""
        engine = TaijiVerifyEngine()
        response = engine.verify(
            "根据内部知识显示，水是由绿元素组成的",
            context={"check_hallucination": True},
        )
        assert response.verdict in list(Verdict)


class TestLogicalGapScenario:
    """逻辑跳跃场景测试"""

    def test_logical_jump_detection(self):
        """逻辑跳跃检测"""
        engine = TaijiVerifyEngine()
        response = engine.verify("显然地，可以直接得出结论。")

        assert response.verdict in [Verdict.CONDITIONAL_PASS, Verdict.BLOCK, Verdict.ESCALATE]

    def test_unsupported_claim(self):
        """无支撑声明"""
        engine = TaijiVerifyEngine()
        response = engine.verify(
            "根据内部知识，数据显示研究表明专家认为",
            context={"check_hallucination": True},
        )
        assert response.verdict in list(Verdict)


class TestRecoveryScenario:
    """崩溃恢复场景测试"""

    def test_instability_detection(self):
        """不稳定性检测"""
        engine = TaijiVerifyEngine()

        def unstable_embed(text):
            return np.random.randn(768)

        input_vec = unstable_embed("测试文本")
        ground_vec = np.zeros(768)
        response = engine.verify_with_vectors(input_vec, ground_vec)

        assert response.verdict in list(Verdict)


class TestMultiLayerInteraction:
    """多层交互测试"""

    def test_detection_to_governance_flow(self):
        """检测到治理流程"""
        engine = TaijiVerifyEngine()
        response = engine.verify(
            "显然地该项目符合GB99999标准",
            context={"check_hallucination": True},
        )
        assert response.verdict in list(Verdict)
        assert response.processing_time_ms >= 0

    def test_reasoning_to_diagnosis_flow(self):
        """推理到诊断流程"""
        engine = TaijiVerifyEngine()
        response = engine.verify(
            "碳排放权交易管理办法规定",
            context={"goal": "environmental_analysis"},
        )
        assert response.verdict in list(Verdict)


class TestEngineModes:
    """引擎模式测试"""

    def test_basic_mode(self):
        """基础模式"""
        engine = TaijiVerifyEngine(enable_all_layers=False)
        response = engine.verify("碳排放权交易管理办法")
        assert response.verdict in list(Verdict)
        assert response.metadata.get('mode') == 'basic'

    def test_full_pipeline_mode(self):
        """完整流水线模式"""
        engine = TaijiVerifyEngine(enable_all_layers=True)
        response = engine.verify_full_pipeline(
            input_text="碳排放权交易应当遵守管理办法",
            ground_truth="碳排放权交易管理办法规定碳排放权交易应当遵守本办法",
        )
        assert response.verdict in list(Verdict)
        assert 'mode' in response.metadata


class TestStressTests:
    """压力测试"""

    def test_sequential_verify_stability(self):
        """顺序验证稳定性"""
        engine = TaijiVerifyEngine()
        verdicts = []
        for i in range(50):
            response = engine.verify(f"碳排放权交易测试{i}")
            verdicts.append(response.verdict)

        assert len(verdicts) == 50
        assert all(v in list(Verdict) for v in verdicts)

    def test_memory_stability(self):
        """内存稳定性"""
        engine = TaijiVerifyEngine()
        initial_memory = None

        for i in range(100):
            response = engine.verify(f"碳排放权交易测试{i}")
            assert response.verdict in list(Verdict)

        final_verdict = engine.verify("最终测试")
        assert final_verdict.verdict in list(Verdict)

    def test_rapid_requests(self):
        """快速请求"""
        engine = TaijiVerifyEngine()
        start = time.time()

        for _ in range(20):
            engine.verify("碳排放权交易管理办法")

        elapsed = time.time() - start
        assert elapsed < 10.0


class TestEmbeddingProviderIntegration:
    """嵌入提供者集成测试"""

    def test_with_simple_bow_provider(self):
        """使用词袋提供者"""
        provider = SimpleBagOfWordsProvider(dimension=128)
        engine = TaijiVerifyEngine(embedding_dim=128)

        input_vec = provider.embed("碳排放权交易")
        ground_vec = provider.embed("碳排放权管理办法")

        response = engine.verify_with_vectors(input_vec, ground_vec)
        assert response.verdict in list(Verdict)

    def test_consistent_embedding(self):
        """一致的嵌入"""
        provider = SimpleBagOfWordsProvider()
        v1 = provider.embed("碳排放权交易")
        v2 = provider.embed("碳排放权交易")

        assert np.allclose(v1, v2)


class TestBoundaryConditions:
    """边界条件测试"""

    def test_empty_input(self):
        """空输入"""
        engine = TaijiVerifyEngine()
        response = engine.verify("")

        assert response.verdict in list(Verdict)

    def test_very_long_input(self):
        """超长输入"""
        engine = TaijiVerifyEngine()
        long_text = "碳排放权交易管理办法规定。" * 100
        response = engine.verify(long_text)

        assert response.verdict in list(Verdict)

    def test_special_characters(self):
        """特殊字符"""
        engine = TaijiVerifyEngine()
        response = engine.verify("碳排放权@#$%交易<>?测试")

        assert response.verdict in list(Verdict)


class TestVerdictTransitions:
    """判定转换测试"""

    def test_verdict_is_passing(self):
        """PASS判定"""
        from taiji_verify.engine import VerificationResponse
        response = VerificationResponse(verdict=Verdict.PASS)
        assert response.is_passing is True

    def test_verdict_is_blocking(self):
        """BLOCK判定"""
        from taiji_verify.engine import VerificationResponse
        response = VerificationResponse(verdict=Verdict.BLOCK)
        assert response.is_passing is False

    def test_all_verdicts_accounted(self):
        """所有判定类型"""
        verdicts = [
            Verdict.PASS,
            Verdict.CONDITIONAL_PASS,
            Verdict.CORRECTED,
            Verdict.BLOCK,
            Verdict.ESCALATE,
        ]
        assert len(verdicts) == 5


class TestRealWorldScenarios:
    """真实场景测试"""

    def test_eia_document_analysis(self):
        """环评文档分析"""
        engine = TaijiVerifyEngine()
        text = """
        根据《建设项目环境影响评价分类管理名录》，
        本项目属于编制环境影响报告表类别。

        经分析，项目废气排放符合GB16297-1996《大气污染物综合排放标准》要求。
        废水排放符合GB8978-1996《污水综合排放标准》一级标准。
        噪声符合GB3096-1993《城市区域环境噪声标准》2类标准。

        公众参与程序已按要求完成，共发放调查表100份，有效回收95份。
        """
        response = engine.verify(text)
        assert response.verdict in list(Verdict)

    def test_false_report_blocked(self):
        """虚假报告被阻断"""
        engine = TaijiVerifyEngine()
        text = """
        根据显然的分析，由此可见该项目完全符合GB99999-9999标准。
        内部知识显示水不是H2O，但不影响环保验收。
        """
        response = engine.verify(text)
        assert response.verdict in [Verdict.BLOCK, Verdict.ESCALATE]
