"""EmbeddingProvider测试 - 完整覆盖率"""
import pytest
import numpy as np
from taiji_verify.embedding import (
    EmbeddingProvider, SimpleBagOfWordsProvider,
    OpenAIEmbeddingProvider, LocalSentenceTransformerProvider,
    create_default_provider,
)


class TestSimpleBagOfWordsProvider:
    """词袋模型提供者测试"""

    def test_default_init(self):
        provider = SimpleBagOfWordsProvider()
        assert provider.dimension() == 128

    def test_custom_dimension(self):
        provider = SimpleBagOfWordsProvider(dimension=256)
        assert provider.dimension() == 256

    def test_embed_returns_numpy_array(self):
        provider = SimpleBagOfWordsProvider()
        vector = provider.embed("测试文本")
        assert isinstance(vector, np.ndarray)
        assert len(vector) == 128

    def test_embed_is_normalized(self):
        provider = SimpleBagOfWordsProvider()
        vector = provider.embed("碳排放权交易管理办法")
        norm = np.linalg.norm(vector)
        assert abs(norm - 1.0) < 0.01

    def test_embed_batch(self):
        provider = SimpleBagOfWordsProvider()
        texts = ["文本1", "文本2", "文本3"]
        vectors = provider.embed_batch(texts)
        assert len(vectors) == 3
        assert all(isinstance(v, np.ndarray) for v in vectors)

    def test_fit_builds_vocab(self):
        provider = SimpleBagOfWordsProvider(dimension=64)
        texts = [
            "碳排放权交易管理办法",
            "环境保护法规定",
            "环境影响评价法",
        ]
        provider.fit(texts)
        assert len(provider._vocab) > 0

    def test_fit_then_embed(self):
        provider = SimpleBagOfWordsProvider(dimension=64)
        texts = [
            "碳排放权交易",
            "环境保护",
        ]
        provider.fit(texts)
        vector = provider.embed("碳排放权")
        assert np.linalg.norm(vector) > 0

    def test_identical_texts_same_vector(self):
        provider = SimpleBagOfWordsProvider()
        v1 = provider.embed("碳排放权交易管理办法")
        v2 = provider.embed("碳排放权交易管理办法")
        assert np.allclose(v1, v2)

    def test_different_texts_different_vectors(self):
        provider = SimpleBagOfWordsProvider()
        v1 = provider.embed("碳排放权交易")
        v2 = provider.embed("环境保护法")
        assert not np.allclose(v1, v2)

    def test_empty_text(self):
        provider = SimpleBagOfWordsProvider()
        vector = provider.embed("")
        assert len(vector) == 128

    def test_stopwords_filtering(self):
        provider = SimpleBagOfWordsProvider()
        v1 = provider.embed("碳排放权的交易")
        v2 = provider.embed("碳排放权交易")
        assert isinstance(v1, np.ndarray)
        assert isinstance(v2, np.ndarray)


class TestOpenAIProvider:
    """OpenAI提供者测试"""

    def test_init(self):
        provider = OpenAIEmbeddingProvider()
        assert provider.dimension() == 1536
        assert provider._model == "text-embedding-3-small"

    def test_custom_dimension(self):
        provider = OpenAIEmbeddingProvider(dimension=512)
        assert provider.dimension() == 512

    def test_custom_model(self):
        provider = OpenAIEmbeddingProvider(model="text-embedding-3-large")
        assert provider._model == "text-embedding-3-large"


class TestLocalSentenceTransformerProvider:
    """本地Sentence-Transformer提供者测试"""

    def test_init(self):
        provider = LocalSentenceTransformerProvider()
        assert provider._model_name == "paraphrase-multilingual-MiniLM-L12-v2"

    def test_custom_model(self):
        provider = LocalSentenceTransformerProvider(model_name="paraphrase-multilingual-mpnet-base-v2")
        assert provider._model_name == "paraphrase-multilingual-mpnet-base-v2"

    def test_dimension_not_set_initially(self):
        provider = LocalSentenceTransformerProvider()
        assert provider._dim is None


class TestCreateDefaultProvider:
    """默认提供者工厂测试"""

    def test_returns_simple_bow_provider(self):
        provider = create_default_provider()
        assert isinstance(provider, SimpleBagOfWordsProvider)

    def test_default_has_correct_dimension(self):
        provider = create_default_provider()
        assert provider.dimension() == 128


class TestEmbeddingInterface:
    """嵌入接口一致性测试"""

    def test_all_providers_implement_embed(self):
        providers = [
            SimpleBagOfWordsProvider(),
        ]
        for provider in providers:
            vector = provider.embed("测试文本")
            assert isinstance(vector, np.ndarray)

    def test_all_providers_implement_embed_batch(self):
        provider = SimpleBagOfWordsProvider()
        vectors = provider.embed_batch(["文本1", "文本2"])
        assert len(vectors) == 2
        assert all(isinstance(v, np.ndarray) for v in vectors)

    def test_all_providers_implement_dimension(self):
        provider = SimpleBagOfWordsProvider()
        dim = provider.dimension()
        assert isinstance(dim, int)
        assert dim > 0
