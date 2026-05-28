"""
Source Tracer - 知识溯源

对应 SourceTracer.ts 的 Python 实现

功能:
- 倒排索引: 关键词→条目ID集合
- Jaccard内容相似度
- 覆盖率 = 匹配关键词/总关键词
- maxSources默认10
- trace_with_attribution: 增加归因验证能力

新增功能 (v2.2):
- trace_with_attribution(): 结合归因验证器进行深度溯源
- 支持引用精准度评估
- 向后兼容原有 query() 方法
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

import numpy as np

# 使用 TYPE_CHECKING 来避免循环导入
if TYPE_CHECKING:
    from taiji_verify.detection.attribution_verifier import (
        AttributionVerifier,
        AttributionResult,
        AttributionLevel,
    )


@dataclass
class TraceResult:
    """溯源结果"""

    matched_entry_ids: list[str]
    coverage: float
    similarity_scores: list[float]
    matched_keywords: list[str]


@dataclass
class KnowledgeSource:
    """知识源"""

    entry_id: str
    content: str
    keywords: list[str]
    source: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class AttributionTraceResult:
    """
    带归因的溯源结果

    继承 TraceResult 的基础溯源能力，增加：
    - attribution_result: 归因验证结果
    - citation_accuracy: 引用准确度
    - attribution_level: 归因级别
    """

    matched_entry_ids: list[str]
    coverage: float
    similarity_scores: list[float]
    matched_keywords: list[str]
    # 新增归因字段
    attribution_result: Optional["AttributionResult"] = None
    citation_accuracy: float = 0.0
    has_citation: bool = False


class SourceTracer:
    """
    知识溯源器

    Usage::
        tracer = SourceTracer()
        tracer.add_entry("E001", "环境保护法", ["环境保护", "法律"])
        result = tracer.query("环境保护法规定")
        print(result.matched_entry_ids)
    """

    def __init__(self, max_sources: int = 10):
        self.max_sources = max_sources
        self._entries: dict[str, KnowledgeSource] = {}
        self._inverted_index: dict[str, set[str]] = {}
        # 归因验证器（可选）
        self._attribution_verifier: Optional["AttributionVerifier"] = None
        self._attribution_available: bool = False

    @property
    def attribution_verifier(self) -> Optional["AttributionVerifier"]:
        """获取归因验证器"""
        return self._attribution_verifier

    def enable_attribution(
        self, verifier: Optional["AttributionVerifier"] = None
    ) -> "AttributionVerifier":
        """
        启用归因验证功能

        Args:
            verifier: 可选的归因验证器实例，如果为None则创建新实例

        Returns:
            AttributionVerifier: 归因验证器实例
        """
        if self._attribution_available and self._attribution_verifier is None:
            # 尝试导入
            try:
                from taiji_verify.detection.attribution_verifier import (
                    AttributionVerifier,
                )

                self._attribution_verifier_class = AttributionVerifier
                self._attribution_available = True
            except ImportError:
                self._attribution_available = False
                raise ImportError(
                    "归因验证功能不可用，请确保已安装 taiji_verify.detection.attribution_verifier"
                )

        if not self._attribution_available:
            raise ImportError(
                "归因验证功能不可用，请确保已安装 taiji_verify.detection.attribution_verifier"
            )

        if verifier is None:
            verifier = self._attribution_verifier_class()
            # 将现有知识条目同步到归因验证器
            for entry_id, entry in self._entries.items():
                verifier.add_knowledge(
                    source_id=entry_id,
                    source_path=entry.source or entry_id,
                    content=entry.content,
                    metadata=entry.metadata,
                )

        self._attribution_verifier = verifier
        return verifier

    def disable_attribution(self) -> None:
        """禁用归因验证功能"""
        self._attribution_verifier = None

    def add_entry(
        self,
        entry_id: str,
        content: str,
        keywords: list[str],
        source: str = "",
        metadata: Optional[dict] = None,
    ) -> None:
        """添加知识条目"""
        entry = KnowledgeSource(
            entry_id=entry_id,
            content=content,
            keywords=keywords,
            source=source,
            metadata=metadata or {},
        )
        self._entries[entry_id] = entry

        for keyword in keywords:
            if keyword not in self._inverted_index:
                self._inverted_index[keyword] = set()
            self._inverted_index[keyword].add(entry_id)

        # 同步到归因验证器
        if self._attribution_verifier is not None:
            self._attribution_verifier.add_knowledge(
                source_id=entry_id,
                source_path=source or entry_id,
                content=content,
                metadata=metadata,
            )

    def query(self, text: str) -> TraceResult:
        """查询文本的知识来源"""
        text_keywords = self._extract_keywords(text)
        matched_ids: set[str] = set()

        for keyword in text_keywords:
            if keyword in self._inverted_index:
                matched_ids.update(self._inverted_index[keyword])

        matched_ids = list(matched_ids)[: self.max_sources]

        coverage = len(matched_ids) / max(len(text_keywords), 1)
        similarity_scores = []
        matched_keywords_list = []

        for entry_id in matched_ids:
            entry = self._entries[entry_id]
            entry_keywords = set(entry.keywords)
            intersection = text_keywords & entry_keywords
            if intersection:
                similarity_scores.append(len(intersection) / len(entry_keywords | text_keywords))
                matched_keywords_list.extend(list(intersection))

        return TraceResult(
            matched_entry_ids=matched_ids,
            coverage=coverage,
            similarity_scores=similarity_scores,
            matched_keywords=list(set(matched_keywords_list)),
        )

    def query_by_keyword(self, keyword: str) -> list[str]:
        """通过关键词查询"""
        return list(self._inverted_index.get(keyword, set()))

    def batch_trace(self, texts: list[str]) -> list[TraceResult]:
        """批量溯源"""
        return [self.query(text) for text in texts]

    def trace_with_attribution(
        self,
        text: str,
        claimed_source: Optional[str] = None,
    ) -> AttributionTraceResult:
        """
        带归因的溯源查询

        结合关键词溯源和归因验证，提供更全面的来源分析：
        1. 执行基础关键词溯源
        2. 进行归因验证（如果启用）
        3. 综合评估引用准确度

        Args:
            text: 待溯源文本
            claimed_source: 声称的来源（可选）

        Returns:
            AttributionTraceResult: 带归因信息的溯源结果

        Raises:
            ImportError: 如果归因验证功能不可用且被调用
        """
        # 基础溯源
        trace_result = self.query(text)

        # 如果归因验证未启用，返回简化结果
        if self._attribution_verifier is None:
            return AttributionTraceResult(
                matched_entry_ids=trace_result.matched_entry_ids,
                coverage=trace_result.coverage,
                similarity_scores=trace_result.similarity_scores,
                matched_keywords=trace_result.matched_keywords,
                has_citation=False,
            )

        # 归因验证
        attribution_result = self._attribution_verifier.verify_attribution(
            conclusion=text,
            claimed_source=claimed_source,
        )

        # 计算引用准确度
        citation_accuracy = self._calculate_citation_accuracy(trace_result, attribution_result)

        return AttributionTraceResult(
            matched_entry_ids=trace_result.matched_entry_ids,
            coverage=trace_result.coverage,
            similarity_scores=trace_result.similarity_scores,
            matched_keywords=trace_result.matched_keywords,
            attribution_result=attribution_result,
            citation_accuracy=citation_accuracy,
            has_citation=attribution_result.is_attributable,
        )

    def batch_trace_with_attribution(
        self,
        texts: list[str],
        claimed_sources: Optional[list[str]] = None,
    ) -> list[AttributionTraceResult]:
        """
        批量带归因的溯源查询

        Args:
            texts: 待溯源文本列表
            claimed_sources: 声称的来源列表（可选）

        Returns:
            list[AttributionTraceResult]: 溯源结果列表
        """
        if claimed_sources is None:
            claimed_sources = [None] * len(texts)

        return [
            self.trace_with_attribution(text, claimed)
            for text, claimed in zip(texts, claimed_sources)
        ]

    def _calculate_citation_accuracy(
        self,
        trace_result: TraceResult,
        attribution_result: Optional["AttributionResult"],
    ) -> float:
        """
        计算引用准确度

        综合考虑：
        1. 关键词覆盖率
        2. 归因验证结果
        3. 相似度分数

        Args:
            trace_result: 基础溯源结果
            attribution_result: 归因验证结果

        Returns:
            float: 引用准确度 0-1
        """
        if attribution_result is None:
            return trace_result.coverage

        # 归因置信度权重
        attribution_weight = 0.6
        coverage_weight = 0.4

        # 归因分数（如果可归因则为归因分数，否则为0）
        attribution_score = (
            attribution_result.attribution_score if attribution_result.is_attributable else 0.0
        )

        # 加权平均
        accuracy = attribution_score * attribution_weight + trace_result.coverage * coverage_weight

        return min(accuracy, 1.0)

    def _extract_keywords(self, text: str) -> set[str]:
        """提取关键词"""
        keywords = set()
        import re

        tokens = re.findall(r"[\u4e00-\u9fff]+|[A-Za-z]+", text)
        for token in tokens:
            if len(token) >= 2:
                keywords.add(token)
        return keywords

    def sync_to_attribution_verifier(self) -> None:
        """
        同步当前知识条目到归因验证器

        用于在启用归因验证后，将已添加的知识条目批量同步
        """
        if self._attribution_verifier is None:
            return

        for entry_id, entry in self._entries.items():
            self._attribution_verifier.add_knowledge(
                source_id=entry_id,
                source_path=entry.source or entry_id,
                content=entry.content,
                metadata=entry.metadata,
            )
