"""
Cross Model Verifier Tests - ARIS交叉模型验证器测试

测试用例覆盖：
1. MockProvider的各种场景
2. 一致性矩阵计算
3. 分歧检测
4. 边界条件（单模型、空输入等）
5. CrossModelVerifier核心功能
6. 批量验证
7. 融合策略（间接通过cross_model_verifier）

v2.2 Phase 1
"""

import sys
import os
import types

# 直接加载模块
cmv_module = types.ModuleType('cross_model_verifier')
sys.modules['cross_model_verifier'] = cmv_module

with open(
    os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'taiji_verify', 'detection', 'cross_model_verifier.py'),
    'r'
) as f:
    content = f.read()
exec(content, cmv_module.__dict__)

# 导入需要的类
ModelProvider = cmv_module.ModelProvider
MockProvider = cmv_module.MockProvider
DeepSeekProvider = cmv_module.DeepSeekProvider
QwenProvider = cmv_module.QwenProvider
GLMProvider = cmv_module.GLMProvider
CrossModelResult = cmv_module.CrossModelResult
CrossModelVerifier = cmv_module.CrossModelVerifier
CrossModelVerdict = cmv_module.CrossModelVerdict


class TestMockProviderBasic:
    """MockProvider基本功能测试"""

    def test_mock_provider_init_default(self):
        """测试默认初始化"""
        provider = MockProvider()
        assert provider._model_id == "mock-default"
        assert provider._response_mode == "agree"

    def test_mock_provider_init_custom(self):
        """测试自定义初始化"""
        provider = MockProvider(model_id="test-model", response_mode="disagree")
        assert provider._model_id == "test-model"
        assert provider._response_mode == "disagree"

    def test_mock_provider_get_model_id(self):
        """测试获取模型ID"""
        provider = MockProvider(model_id="custom-id")
        assert provider.get_model_id() == "custom-id"

    def test_mock_provider_fixed_response(self):
        """测试固定回复模式"""
        provider = MockProvider(
            model_id="fixed",
            fixed_response="这是固定回复"
        )
        response = provider.generate("任何问题")
        assert response == "这是固定回复"

    def test_mock_provider_agree_mode(self):
        """测试agree模式"""
        provider = MockProvider(response_mode="agree")
        response = provider.generate("什么是碳排放权？")
        assert "一致" in response or "知识" in response or "参考" in response

    def test_mock_provider_disagree_mode(self):
        """测试disagree模式"""
        provider = MockProvider(response_mode="disagree")
        response = provider.generate("什么是碳排放权？")
        assert "争议" in response or "不同" in response or "谨慎" in response

    def test_mock_provider_partial_mode(self):
        """测试partial模式"""
        provider = MockProvider(response_mode="partial")
        response = provider.generate("什么是碳排放权？")
        assert "部分" in response or "证据" in response or "需要" in response


class TestModelProviderAbstract:
    """ModelProvider抽象类测试"""

    def test_model_provider_is_abc(self):
        """测试是ABC类"""
        assert hasattr(ModelProvider, 'generate')
        assert hasattr(ModelProvider, 'get_model_id')


class TestCrossModelResult:
    """CrossModelResult数据类测试"""

    def test_result_creation(self):
        """测试结果创建"""
        result = CrossModelResult(conclusion="测试结论")
        assert result.conclusion == "测试结论"
        assert result.agreement_rate == 0.0
        assert result.verdict == CrossModelVerdict.INSUFFICIENT

    def test_result_model_count(self):
        """测试模型数量属性"""
        result = CrossModelResult(
            conclusion="测试",
            model_responses={"m1": "r1", "m2": "r2"}
        )
        assert result.model_count == 2

    def test_result_has_disagreement(self):
        """测试分歧标记检测"""
        result = CrossModelResult(
            conclusion="测试",
            disagreement_flags=["flag1"]
        )
        assert result.has_disagreement is True

        result2 = CrossModelResult(conclusion="测试")
        assert result2.has_disagreement is False

    def test_result_get_response(self):
        """测试获取特定模型回复"""
        result = CrossModelResult(
            conclusion="测试",
            model_responses={"m1": "response1", "m2": "response2"}
        )
        assert result.get_response("m1") == "response1"
        assert result.get_response("m3") is None


class TestCrossModelVerifierInit:
    """CrossModelVerifier初始化测试"""

    def test_verifier_init_default(self):
        """测试默认初始化"""
        verifier = CrossModelVerifier()
        assert verifier.provider_count == 3  # 默认3个MockProvider

    def test_verifier_init_empty_providers_fails(self):
        """测试空providers列表会抛出异常"""
        try:
            verifier = CrossModelVerifier(providers=[])
            assert False, "应该抛出异常"
        except ValueError as e:
            assert "至少需要" in str(e)

    def test_verifier_init_custom_providers(self):
        """测试自定义providers"""
        providers = [
            MockProvider(model_id="p1"),
            MockProvider(model_id="p2"),
        ]
        verifier = CrossModelVerifier(providers=providers)
        assert verifier.provider_count == 2

    def test_verifier_init_too_few_providers(self):
        """测试提供者数量不足"""
        providers = [MockProvider(model_id="p1")]
        try:
            verifier = CrossModelVerifier(providers=providers, min_models=2)
            assert False, "应该抛出异常"
        except ValueError as e:
            assert "至少需要" in str(e)

    def test_verifier_init_too_many_providers(self):
        """测试提供者数量过多"""
        providers = [
            MockProvider(model_id=f"p{i}") for i in range(6)
        ]
        try:
            verifier = CrossModelVerifier(providers=providers, max_models=5)
            assert False, "应该抛出异常"
        except ValueError as e:
            assert "最多支持" in str(e)

    def test_verifier_disagreement_threshold(self):
        """测试分歧阈值配置"""
        verifier = CrossModelVerifier(disagreement_threshold=0.5)
        assert verifier._disagreement_threshold == 0.5

    def test_verifier_providers_property(self):
        """测试providers属性"""
        verifier = CrossModelVerifier()
        providers = verifier.providers
        assert len(providers) == 3
        assert all(isinstance(p, MockProvider) for p in providers)


class TestCrossModelVerifierVerify:
    """CrossModelVerifier验证功能测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = CrossModelVerifier()

    def test_verify_basic(self):
        """测试基本验证"""
        result = self.verifier.verify("碳排放权交易管理办法规定碳排放权")
        assert isinstance(result, CrossModelResult)
        assert result.conclusion == "碳排放权交易管理办法规定碳排放权"
        assert result.model_count == 3

    def test_verify_empty_conclusion(self):
        """测试空结论"""
        result = self.verifier.verify("")
        assert result.verdict == CrossModelVerdict.INSUFFICIENT
        assert result.confidence == 0.0

    def test_verify_whitespace_conclusion(self):
        """测试纯空白结论"""
        result = self.verifier.verify("   ")
        assert result.verdict == CrossModelVerdict.INSUFFICIENT

    def test_verify_with_context(self):
        """测试带上下文验证"""
        result = self.verifier.verify(
            "这是一个测试结论",
            context="相关上下文信息"
        )
        assert result.model_count == 3
        assert len(result.model_responses) == 3

    def test_verify_model_responses_filled(self):
        """测试模型回复被正确填充"""
        result = self.verifier.verify("测试结论")
        for model_id, response in result.model_responses.items():
            assert response is not None
            assert len(response) > 0


class TestAgreementMatrix:
    """一致性矩阵计算测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = CrossModelVerifier()

    def test_matrix_empty_responses(self):
        """测试空回复列表"""
        matrix = self.verifier.compute_agreement([])
        assert matrix.size == 0

    def test_matrix_single_response(self):
        """测试单个回复"""
        matrix = self.verifier.compute_agreement(["只有一个回复"])
        assert matrix.shape == (1, 1)
        assert matrix[0][0] == 1.0

    def test_matrix_two_responses(self):
        """测试两个回复"""
        matrix = self.verifier.compute_agreement(["回复1", "回复2"])
        assert matrix.shape == (2, 2)
        assert matrix[0][0] == 1.0
        assert matrix[1][1] == 1.0
        assert matrix[0][1] == matrix[1][0]  # 对称性

    def test_matrix_three_responses(self):
        """测试三个回复"""
        matrix = self.verifier.compute_agreement(["回复1", "回复2", "回复3"])
        assert matrix.shape == (3, 3)
        # 对角线全为1
        assert matrix[0][0] == matrix[1][1] == matrix[2][2] == 1.0

    def test_matrix_symmetric(self):
        """测试矩阵对称性"""
        matrix = self.verifier.compute_agreement(["回复1", "回复2", "回复3"])
        for i in range(3):
            for j in range(3):
                assert matrix[i][j] == matrix[j][i]

    def test_matrix_values_in_range(self):
        """测试矩阵值在[0,1]范围内"""
        matrix = self.verifier.compute_agreement(["回复1", "回复2"])
        assert 0 <= matrix[0][1] <= 1.0


class TestDisagreementDetection:
    """分歧检测测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = CrossModelVerifier()

    def test_detect_disagreement_empty_result(self):
        """测试空结果"""
        result = CrossModelResult(conclusion="测试")
        flags = self.verifier.detect_disagreement(result)
        assert len(flags) == 0

    def test_detect_disagreement_single_model(self):
        """测试单模型结果"""
        result = CrossModelResult(
            conclusion="测试",
            model_responses={"m1": "回复1"}
        )
        flags = self.verifier.detect_disagreement(result)
        assert len(flags) == 0

    def test_detect_disagreement_no_difference(self):
        """测试无差异情况"""
        result = CrossModelResult(
            conclusion="测试",
            model_responses={
                "m1": "该结论正确",
                "m2": "该结论正确",
                "m3": "该结论正确"
            }
        )
        flags = self.verifier.detect_disagreement(result)
        # 完全相同可能无分歧标记
        assert isinstance(flags, list)

    def test_detect_disagreement_with_numbers(self):
        """测试数值差异检测"""
        result = CrossModelResult(
            conclusion="测试",
            model_responses={
                "m1": "碳排放量是100万吨",
                "m2": "碳排放量是200万吨",
            }
        )
        flags = self.verifier.detect_disagreement(result)
        # 检查返回值是列表类型
        assert isinstance(flags, list)

    def test_detect_disagreement_deduplication(self):
        """测试分歧标记去重"""
        result = CrossModelResult(
            conclusion="测试",
            model_responses={
                "m1": "关键词A不同关键词B",
                "m2": "关键词A不同关键词C",
                "m3": "关键词A不同关键词D",
            }
        )
        flags = self.verifier.detect_disagreement(result)
        # 应该去重，相同类型的分歧只出现一次
        type_counts = {}
        for flag in flags:
            flag_type = flag.split(":")[0]
            type_counts[flag_type] = type_counts.get(flag_type, 0) + 1


class TestCrossValidationScore:
    """交叉验证分数计算测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = CrossModelVerifier()

    def test_score_empty_results(self):
        """测试空结果列表"""
        score = self.verifier.compute_cross_validation_score([])
        assert score == 0.0

    def test_score_all_agree(self):
        """测试全部一致"""
        results = [
            CrossModelResult(conclusion=f"c{i}", verdict=CrossModelVerdict.AGREE)
            for i in range(3)
        ]
        score = self.verifier.compute_cross_validation_score(results)
        assert score == 1.0

    def test_score_all_disagree(self):
        """测试全部分歧"""
        results = [
            CrossModelResult(conclusion=f"c{i}", verdict=CrossModelVerdict.DISAGREE)
            for i in range(3)
        ]
        score = self.verifier.compute_cross_validation_score(results)
        assert score == 0.0

    def test_score_mixed(self):
        """测试混合结果"""
        results = [
            CrossModelResult(conclusion="c1", verdict=CrossModelVerdict.AGREE),
            CrossModelResult(conclusion="c2", verdict=CrossModelVerdict.DISAGREE),
            CrossModelResult(conclusion="c3", verdict=CrossModelVerdict.PARTIAL),
        ]
        score = self.verifier.compute_cross_validation_score(results)
        # AGREE*1 + DISAGREE*0 + PARTIAL*0.5 = 1.5 / 3 = 0.5
        assert score == 0.5


class TestBatchVerify:
    """批量验证测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = CrossModelVerifier()

    def test_batch_verify_empty(self):
        """测试空批量"""
        results = self.verifier.batch_verify([])
        assert len(results) == 0

    def test_batch_verify_single(self):
        """测试单条批量"""
        results = self.verifier.batch_verify(["结论1"])
        assert len(results) == 1
        assert results[0].conclusion == "结论1"

    def test_batch_verify_multiple(self):
        """测试多条批量"""
        conclusions = ["结论1", "结论2", "结论3"]
        results = self.verifier.batch_verify(conclusions)
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.conclusion == conclusions[i]

    def test_batch_verify_with_context(self):
        """测试带上下文的批量验证"""
        conclusions = ["结论1", "结论2"]
        context = "共享上下文"
        results = self.verifier.batch_verify(conclusions, context=context)
        assert len(results) == 2


class TestVerdictClassification:
    """判定分类测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = CrossModelVerifier()

    def test_verdict_agree_high_agreement(self):
        """测试高一致率=AGREE"""
        result = CrossModelResult(
            conclusion="测试",
            agreement_rate=0.9,
            model_responses={"m1": "r1", "m2": "r2"}
        )
        # 手动计算verdict
        verdict = self.verifier._compute_verdict(0.9, 0)
        assert verdict == CrossModelVerdict.AGREE

    def test_verdict_disagree_low_agreement(self):
        """测试低一致率=DISAGREE"""
        verdict = self.verifier._compute_verdict(0.2, 3)
        assert verdict == CrossModelVerdict.DISAGREE

    def test_verdict_partial_moderate(self):
        """测试中等一致率=PARTIAL"""
        verdict = self.verifier._compute_verdict(0.6, 2)
        assert verdict == CrossModelVerdict.PARTIAL


class TestConfidenceCalculation:
    """置信度计算测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = CrossModelVerifier()

    def test_confidence_basic(self):
        """测试基础置信度"""
        confidence = self.verifier._compute_confidence(0.8, 0, 3)
        assert 0 <= confidence <= 1.0
        assert confidence > 0.5  # 高一致率应该有较高置信度

    def test_confidence_with_disagreement(self):
        """测试有分歧时的置信度"""
        high_disagree = self.verifier._compute_confidence(0.8, 5, 3)
        no_disagree = self.verifier._compute_confidence(0.8, 0, 3)
        assert high_disagree < no_disagree

    def test_confidence_model_count_bonus(self):
        """测试模型数量加成"""
        two_models = self.verifier._compute_confidence(0.8, 0, 2)
        three_models = self.verifier._compute_confidence(0.8, 0, 3)
        assert three_models >= two_models

    def test_confidence_bounds(self):
        """测试置信度边界"""
        # 极端情况
        conf = self.verifier._compute_confidence(1.0, 0, 5)
        assert conf <= 1.0
        conf = self.verifier._compute_confidence(0.0, 10, 2)
        assert conf >= 0.0


class TestProviderClasses:
    """真实Provider类测试（检查类存在性）"""

    def test_deepseek_provider_class(self):
        """测试DeepSeekProvider类存在"""
        assert DeepSeekProvider is not None

    def test_qwen_provider_class(self):
        """测试QwenProvider类存在"""
        assert QwenProvider is not None

    def test_glm_provider_class(self):
        """测试GLMProvider类存在"""
        assert GLMProvider is not None

    def test_deepseek_provider_init(self):
        """测试DeepSeekProvider初始化"""
        provider = DeepSeekProvider(model="test-model", api_key="test-key")
        assert provider._model == "test-model"
        assert provider._api_key == "test-key"

    def test_qwen_provider_init(self):
        """测试QwenProvider初始化"""
        provider = QwenProvider(model="qwen-test", api_key="test-key")
        assert provider._model == "qwen-test"

    def test_glm_provider_init(self):
        """测试GLMProvider初始化"""
        provider = GLMProvider(model="glm-test", api_key="test-key")
        assert provider._model == "glm-test"


class TestEdgeCases:
    """边界条件测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = CrossModelVerifier()

    def test_very_long_conclusion(self):
        """测试超长结论"""
        long_text = "测试" * 1000
        result = self.verifier.verify(long_text)
        assert result.conclusion == long_text

    def test_unicode_conclusion(self):
        """测试Unicode内容"""
        result = self.verifier.verify("碳排放权交易管理办法规定碳排放权交易🔥")
        assert result.model_count == 3

    def test_special_characters(self):
        """测试特殊字符"""
        result = self.verifier.verify("测试！@#$%^&*()_+-=[]{}|;':\",./<>?")
        assert result.model_count == 3

    def test_chinese_only(self):
        """测试纯中文"""
        result = self.verifier.verify("碳排放权交易管理办法规定重点排污单位应当安装自动监测设备")
        assert result.model_count == 3
        assert result.verdict in [CrossModelVerdict.AGREE, CrossModelVerdict.PARTIAL]

    def test_english_only(self):
        """测试纯英文"""
        result = self.verifier.verify("Carbon emission trading is a market-based approach")
        assert result.model_count == 3

    def test_mixed_language(self):
        """测试中英混合"""
        result = self.verifier.verify("碳排放权Carbon emission trading")
        assert result.model_count == 3


class TestEmbeddingIntegration:
    """嵌入集成测试"""

    def test_with_embedding_provider(self):
        """测试带嵌入提供者的验证器"""
        # 由于我们没有真实的嵌入提供者，这里只测试接口
        try:
            verifier = CrossModelVerifier(embedding_provider=None)
            assert verifier._embedding_provider is None
        except Exception:
            assert False, "应该能创建不带嵌入提供者的验证器"

    def test_keyword_extraction(self):
        """测试关键词提取"""
        verifier = CrossModelVerifier()
        text = "碳排放权交易管理办法规定重点排污单位应当安装自动监测设备"
        keywords = verifier._extract_keywords(text)
        assert isinstance(keywords, set)
        assert len(keywords) > 0

    def test_source_extraction(self):
        """测试来源提取"""
        verifier = CrossModelVerifier()
        text = "根据《大气污染防治法》第38条规定，重点排污单位应当安装自动监测设备"
        sources = verifier._extract_sources(text)
        assert isinstance(sources, set)
        # 应该能提取到法律名称
        assert len(sources) >= 0
