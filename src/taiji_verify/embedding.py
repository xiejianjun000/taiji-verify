"""
EmbeddingProvider - 嵌入向量提供者抽象层

提供可插拔的文本嵌入接口：
- SimpleBagOfWordsProvider: 词袋模型（默认，零依赖）
- OpenAIEmbeddingProvider: OpenAI text-embedding-3-small
- LocalSentenceTransformerProvider: 本地sentence-transformers模型
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from typing import Optional
import hashlib
import math

import numpy as np


class EmbeddingProvider(ABC):
    """嵌入向量提供者抽象基类"""

    @abstractmethod
    def embed(self, text: str) -> np.ndarray:
        """将文本转换为嵌入向量"""
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        """批量将文本转换为嵌入向量"""
        pass

    @abstractmethod
    def dimension(self) -> int:
        """返回嵌入向量维度"""
        pass


class SimpleBagOfWordsProvider(EmbeddingProvider):
    """
    词袋模型嵌入提供者（零依赖）

    使用词频和IDF权重计算文本向量，适合无外部依赖的环境。

    Usage::
        provider = SimpleBagOfWordsProvider(dimension=128)
        vector = provider.embed("碳排放权交易管理办法")
        vectors = provider.embed_batch(["文本1", "文本2"])
    """

    def __init__(
        self,
        dimension: int = 128,
        stopwords: Optional[set[str]] = None,
        use_idf: bool = True,
    ):
        self._dim = dimension
        self._use_idf = use_idf
        self._vocab: dict[str, int] = {}
        self._idf: dict[str, float] = {}
        self._doc_count = 0

        self._default_stopwords = stopwords or {
            "的",
            "了",
            "在",
            "是",
            "我",
            "有",
            "和",
            "就",
            "不",
            "人",
            "都",
            "一",
            "一个",
            "上",
            "也",
            "很",
            "到",
            "说",
            "要",
            "去",
            "你",
            "会",
            "着",
            "没有",
            "看",
            "好",
            "自己",
            "这",
            "那",
            "它",
            "他",
            "她",
        }

    def _tokenize(self, text: str) -> list[str]:
        """简单分词"""
        chars = list(text.lower())
        tokens = []
        i = 0
        while i < len(chars):
            if i + 1 < len(chars):
                tokens.append(chars[i] + chars[i + 1])
            i += 2
        return tokens

    def _compute_idf(self, texts: list[str]) -> dict[str, float]:
        """计算IDF"""
        df = Counter()
        for text in texts:
            tokens = set(self._tokenize(text))
            for token in tokens:
                df[token] += 1

        idf = {}
        for token, freq in df.items():
            idf[token] = math.log((len(texts) + 1) / (freq + 1)) + 1
        return idf

    def fit(self, texts: list[str]) -> SimpleBagOfWordsProvider:
        """从语料库学习词汇表和IDF"""
        all_tokens = []
        for text in texts:
            tokens = self._tokenize(text)
            tokens = [t for t in tokens if t not in self._default_stopwords]
            all_tokens.extend(tokens)

        token_freq = Counter(all_tokens)
        most_common = token_freq.most_common(self._dim)
        self._vocab = {token: idx for idx, (token, _) in enumerate(most_common)}
        self._idf = self._compute_idf(texts)
        self._doc_count = len(texts)
        return self

    def embed(self, text: str) -> np.ndarray:
        """将文本转换为向量"""
        if not self._vocab:
            return self._random_embed(text)

        tokens = self._tokenize(text)
        tokens = [t for t in tokens if t not in self._default_stopwords]

        vector = np.zeros(self._dim)
        if self._use_idf:
            for token in tokens:
                if token in self._vocab:
                    idx = self._vocab[token]
                    idf = self._idf.get(token, 1.0)
                    vector[idx] = idf
        else:
            for token in tokens:
                if token in self._vocab:
                    idx = self._vocab[token]
                    vector[idx] += 1

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector

    def _random_embed(self, text: str) -> np.ndarray:
        """无词汇表时的伪嵌入"""
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16)
        rng = np.random.RandomState(seed % (2**32))
        vector = rng.randn(self._dim)
        vector = vector / np.linalg.norm(vector)
        return vector

    def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        """批量嵌入"""
        return [self.embed(text) for text in texts]

    def dimension(self) -> int:
        """返回向量维度"""
        return self._dim


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI嵌入提供者

    需要openai包和API密钥。
    使用text-embedding-3-small模型。
    """

    def __init__(
        self,
        dimension: int = 1536,
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
    ):
        self._dim = dimension
        self._model = model
        self._api_key = api_key
        self._client = None

    def _get_client(self):
        """延迟初始化客户端"""
        if self._client is None:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=self._api_key)
            except ImportError:
                raise ImportError("OpenAI package required. Install: pip install openai")
        return self._client

    def embed(self, text: str) -> np.ndarray:
        """调用OpenAI API获取嵌入"""
        client = self._get_client()
        response = client.embeddings.create(
            model=self._model,
            input=text,
            dimensions=self._dim,
        )
        embedding = response.data[0].embedding
        return np.array(embedding)

    def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        """批量调用OpenAI API"""
        client = self._get_client()
        response = client.embeddings.create(
            model=self._model,
            input=texts,
            dimensions=self._dim,
        )
        return [np.array(item.embedding) for item in response.data]

    def dimension(self) -> int:
        """返回向量维度"""
        return self._dim


class LocalSentenceTransformerProvider(EmbeddingProvider):
    """
    本地Sentence-Transformers提供者

    使用本地部署的sentence-transformers模型。
    """

    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        dimension: Optional[int] = None,
    ):
        self._model_name = model_name
        self._dim = dimension
        self._model = None

    def _get_model(self):
        """延迟加载模型"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self._model_name)
                if self._dim is None:
                    self._dim = self._model.get_sentence_embedding_dimension()
            except ImportError:
                raise ImportError(
                    "sentence-transformers required. Install: pip install sentence-transformers"
                )
        return self._model

    def embed(self, text: str) -> np.ndarray:
        """使用本地模型嵌入"""
        model = self._get_model()
        embedding = model.encode(text)
        return embedding

    def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        """批量嵌入"""
        model = self._get_model()
        embeddings = model.encode(texts)
        return [emb for emb in embeddings]

    def dimension(self) -> int:
        """返回向量维度"""
        if self._dim is None:
            self._get_model()
        return self._dim


def create_default_provider() -> EmbeddingProvider:
    """创建默认的嵌入提供者（零依赖）"""
    return SimpleBagOfWordsProvider(dimension=128)
