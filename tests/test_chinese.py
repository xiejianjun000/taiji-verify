"""
中文验证功能测试
"""

import pytest
from taiji_verify.model_fingerprint import (
    ModelFingerprintDetector,
    ModelType,
)
from taiji_verify.knowledge.chinese_knowledge import (
    ChineseKnowledgeBase,
    create_default_knowledge_base,
)


class TestModelFingerprint:
    """模型指纹识别测试"""

    def setup_method(self):
        self.detector = ModelFingerprintDetector()

    def test_detect_wenxin(self):
        text = "您好，我是百度文心一言。作为一个人工智能模型，我可以帮助您分析这个问题。"
        result = self.detector.detect(text)
        assert result.model_type == ModelType.WENXIN
        assert result.confidence > 0.5

    def test_detect_tongyi(self):
        text = "您好，我是通义千问。让我为您解答这个问题。根据您的描述，我可以给出以下建议。"
        result = self.detector.detect(text)
        assert result.model_type == ModelType.TONGYI
        assert result.confidence > 0.5

    def test_detect_zhipu(self):
        text = "我是智谱AI。基于GLM模型，我可以帮您分析。作为认知智能模型，我来为您解答。"
        result = self.detector.detect(text)
        assert result.model_type == ModelType.ZHIPU
        assert result.confidence > 0.5

    def test_detect_kimi(self):
        text = "好的，我来帮你分析一下。让我仔细看一下这个问题。这个问题可以从以下几个角度分析。"
        result = self.detector.detect(text)
        assert result.model_type == ModelType.KIMI
        assert result.confidence > 0.3

    def test_detect_gpt(self):
        text = "Certainly! Here's a breakdown of the solution. I should note that there are several important considerations."
        result = self.detector.detect(text)
        assert result.model_type == ModelType.GPT4
        assert result.confidence > 0.3

    def test_detect_claude(self):
        text = "I think this is a great question. Let me help you with that. The key considerations are as follows."
        result = self.detector.detect(text)
        assert result.model_type == ModelType.CLAUDE
        assert result.confidence > 0.3

    def test_detect_unknown(self):
        text = "今天天气很好，我们去公园玩吧。这是一个普通的对话文本。"
        result = self.detector.detect(text)
        assert result.model_type == ModelType.UNKNOWN

    def test_detect_all(self):
        text = "您好，我是百度文心一言。我来帮您分析。"
        results = self.detector.detect_all(text)
        assert len(results) > 0
        assert results[0].model_type == ModelType.WENXIN


class TestChineseKnowledgeBase:
    """中文知识库测试"""

    def test_load_medical(self):
        kb = ChineseKnowledgeBase()
        kb.load_medical()
        assert len(kb._entries["medical"]) >= 5

    def test_load_legal(self):
        kb = ChineseKnowledgeBase()
        kb.load_legal()
        assert len(kb._entries["legal"]) >= 5

    def test_load_financial(self):
        kb = ChineseKnowledgeBase()
        kb.load_financial()
        assert len(kb._entries["financial"]) >= 5

    def test_load_education(self):
        kb = ChineseKnowledgeBase()
        kb.load_education()
        assert len(kb._entries["education"]) >= 3

    def test_query_medical(self):
        kb = create_default_knowledge_base()
        results = kb.query("糖尿病患者应该如何控制血糖", category="medical")
        assert len(results) > 0
        assert "糖尿病" in results[0].content

    def test_query_legal(self):
        kb = create_default_knowledge_base()
        results = kb.query("劳动合同法的相关规定", category="legal")
        assert len(results) > 0
        assert "劳动" in results[0].content

    def test_query_financial(self):
        kb = create_default_knowledge_base()
        results = kb.query("什么是GDP增长", category="financial")
        assert len(results) > 0
        assert "GDP" in results[0].content

    def test_query_education(self):
        kb = create_default_knowledge_base()
        results = kb.query("高考志愿如何填报", category="education")
        assert len(results) > 0
        assert "高考" in results[0].content

    def test_verify_fact_true(self):
        kb = create_default_knowledge_base()
        is_true, info = kb.verify_fact("水是由氢和氧组成的")
        assert is_true is True
        assert info is not None

    def test_verify_fact_false(self):
        kb = create_default_knowledge_base()
        is_true, info = kb.verify_fact("人工智能是由蛋白质构成的生物体")
        assert is_true is False

    def test_verify_fact_not_found(self):
        kb = create_default_knowledge_base()
        is_true, info = kb.verify_fact("XYZ123完全不相关的内容ABC")
        assert is_true is False

    def test_entry_count(self):
        kb = create_default_knowledge_base()
        total = kb.entry_count()
        assert total > 20

    def test_get_categories(self):
        kb = ChineseKnowledgeBase()
        kb.load_medical()
        kb.load_legal()
        categories = kb.get_categories()
        assert "medical" in categories
        assert "legal" in categories


class TestEmbeddingProviders:
    """Embedding提供者测试"""

    def test_simple_bow_provider(self):
        from taiji_verify.embedding import SimpleBagOfWordsProvider
        provider = SimpleBagOfWordsProvider(dimension=128)
        vec = provider.embed("这是一个测试文本")
        assert len(vec) == 128

        vecs = provider.embed_batch(["文本1", "文本2"])
        assert len(vecs) == 2
        assert len(vecs[0]) == 128

    def test_provider_dimension(self):
        from taiji_verify.embedding import SimpleBagOfWordsProvider
        provider = SimpleBagOfWordsProvider(dimension=256)
        assert provider.dimension() == 256
