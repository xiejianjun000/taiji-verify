"""
中文AI验证器

整合中文Embedding、领域知识库、模型指纹识别的一站式验证方案。

Usage:
    from taiji_verify.chinese import ChineseVerifier

    verifier = ChineseVerifier(embedding="zhipu", api_key="xxx")
    result = verifier.verify("AI输出文本", expected="标准答案")

    # 识别模型来源
    result = verifier.verify_with_model_detection("AI输出文本")
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from taiji_verify.engine import TaijiVerifyEngine
from taiji_verify.embedding import (
    EmbeddingProvider,
    SimpleBagOfWordsProvider,
    ZhipuEmbeddingProvider,
    WenxinEmbeddingProvider,
    TongyiEmbeddingProvider,
    DoubaoEmbeddingProvider,
    HunyuanEmbeddingProvider,
)
from taiji_verify.knowledge.chinese_knowledge import ChineseKnowledgeBase
from taiji_verify.model_fingerprint import (
    ModelFingerprintDetector,
    ModelFingerprint,
    ModelType,
)


class ChineseVerifier:
    """
    中文AI输出验证器

    整合:
    - 中文Embedding模型
    - 中文领域知识库
    - 模型指纹识别

    Usage:
        verifier = ChineseVerifier(embedding="zhipu", api_key="xxx")
        result = verifier.verify("AI输出", expected="标准答案")
    """

    def __init__(
        self,
        embedding: str = "local",
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        knowledge_base: bool = True,
        model_detection: bool = True,
        embedding_dim: int = 768,
    ):
        """
        初始化中文验证器

        Args:
            embedding: Embedding类型
                - "local": 本地词袋模型（默认，无需API）
                - "zhipu": 智谱GLM
                - "wenxin": 百度文心
                - "tongyi": 阿里通义
                - "doubao": 字节豆包
                - "hunyuan": 腾讯混元
            api_key: API密钥（部分embedding需要）
            secret_key: 密钥（百度文心需要）
            knowledge_base: 是否加载中文知识库
            model_detection: 是否启用模型指纹识别
            embedding_dim: 向量维度
        """
        self._embedding = self._create_embedding(embedding, api_key, secret_key, embedding_dim)
        self._engine = TaijiVerifyEngine(
            embedding_dim=embedding_dim,
            enable_all_layers=True,
        )
        self._knowledge_base = ChineseKnowledgeBase() if knowledge_base else None
        self._model_detector = ModelFingerprintDetector() if model_detection else None

        if knowledge_base:
            self._knowledge_base.load_medical()
            self._knowledge_base.load_legal()
            self._knowledge_base.load_financial()
            self._knowledge_base.load_education()

    def _create_embedding(
        self,
        embedding: str,
        api_key: Optional[str],
        secret_key: Optional[str],
        dimension: int,
    ) -> EmbeddingProvider:
        """创建Embedding提供者"""
        providers = {
            "local": lambda: SimpleBagOfWordsProvider(dimension=dimension),
            "zhipu": lambda: ZhipuEmbeddingProvider(
                api_key=api_key or "",
                dimension=dimension,
            ) if api_key else SimpleBagOfWordsProvider(dimension=dimension),
            "wenxin": lambda: WenxinEmbeddingProvider(
                api_key=api_key or "",
                secret_key=secret_key or "",
                dimension=dimension,
            ) if api_key and secret_key else SimpleBagOfWordsProvider(dimension=dimension),
            "tongyi": lambda: TongyiEmbeddingProvider(
                api_key=api_key or "",
                dimension=dimension,
            ) if api_key else SimpleBagOfWordsProvider(dimension=dimension),
            "doubao": lambda: DoubaoEmbeddingProvider(
                api_key=api_key or "",
                dimension=dimension,
            ) if api_key else SimpleBagOfWordsProvider(dimension=dimension),
            "hunyuan": lambda: HunyuanEmbeddingProvider(
                secret_id=api_key or "",
                secret_key=secret_key or "",
                dimension=dimension,
            ) if api_key and secret_key else SimpleBagOfWordsProvider(dimension=dimension),
        }

        return providers.get(embedding, providers["local"])()

    def verify(
        self,
        text: str,
        expected: Optional[str] = None,
    ) -> ChineseVerifyResult:
        """
        验证AI输出

        Args:
            text: AI输出文本
            expected: 期望/标准答案

        Returns:
            ChineseVerifyResult: 验证结果
        """
        response = self._engine.verify(
            input_text=text,
            ground_truth=expected,
        )

        knowledge_issues = []
        if self._knowledge_base:
            for cat in self._knowledge_base.get_categories():
                results = self._knowledge_base.query(text, category=cat)
                if results:
                    knowledge_issues.extend([
                        {
                            "category": cat,
                            "entry": r.content[:100],
                            "source": r.source,
                        }
                        for r in results[:2]
                    ])

        model_info = None
        if self._model_detector:
            fingerprint = self._model_detector.detect(text)
            model_info = {
                "model_type": fingerprint.model_type.value,
                "confidence": fingerprint.confidence,
                "evidence": fingerprint.evidence,
            }

        return ChineseVerifyResult(
            verdict=response.verdict.value,
            is_passing=response.is_passing,
            delta_s=response.delta_s_result.cosine_similarity if response.delta_s_result else None,
            risk_level=str(response.delta_s_result.gate_zone.value) if response.delta_s_result else None,
            failures=response.failure_detections,
            model_info=model_info,
            knowledge_issues=knowledge_issues,
            processing_time_ms=response.processing_time_ms,
        )

    def verify_with_model_detection(
        self,
        text: str,
        expected: Optional[str] = None,
    ) -> ChineseVerifyResult:
        """
        验证并识别模型来源

        Args:
            text: AI输出文本
            expected: 期望/标准答案

        Returns:
            ChineseVerifyResult: 包含模型指纹
        """
        return self.verify(text, expected)

    def query_knowledge(
        self,
        text: str,
        category: Optional[str] = None,
    ) -> list[dict]:
        """
        查询中文知识库

        Args:
            text: 查询文本
            category: 指定类别

        Returns:
            相关知识条目
        """
        if not self._knowledge_base:
            return []

        results = self._knowledge_base.query(text, category=category)
        return [
            {
                "content": r.content,
                "category": r.category,
                "source": r.source,
                "keywords": r.keywords,
            }
            for r in results
        ]

    def detect_model(self, text: str) -> ModelFingerprint:
        """
        识别模型来源

        Args:
            text: AI输出文本

        Returns:
            模型指纹
        """
        if not self._model_detector:
            return ModelFingerprint(
                model_type=ModelType.UNKNOWN,
                confidence=0.0,
                evidence=[],
            )
        return self._model_detector.detect(text)


@dataclass
class ChineseVerifyResult:
    """中文验证结果"""
    verdict: str
    is_passing: bool
    delta_s: Optional[float] = None
    risk_level: Optional[str] = None
    failures: list = None
    model_info: Optional[dict] = None
    knowledge_issues: list = None
    processing_time_ms: int = 0

    def __post_init__(self):
        if self.failures is None:
            self.failures = []
        if self.knowledge_issues is None:
            self.knowledge_issues = []

    def __str__(self) -> str:
        parts = [
            f"判定: {self.verdict}",
            f"通过: {'是' if self.is_passing else '否'}",
        ]
        if self.delta_s:
            parts.append(f"ΔS: {self.delta_s:.4f}")
        if self.model_info:
            parts.append(f"模型: {self.model_info['model_type']}")
        return " | ".join(parts)
