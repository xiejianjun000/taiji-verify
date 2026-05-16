"""
Source Tracer - 知识溯源

对应 SourceTracer.ts 的 Python 实现

功能:
- 倒排索引: 关键词→条目ID集合
- Jaccard内容相似度
- 覆盖率 = 匹配关键词/总关键词
- maxSources默认10
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


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

    def query(self, text: str) -> TraceResult:
        """查询文本的知识来源"""
        text_keywords = self._extract_keywords(text)
        matched_ids: set[str] = set()

        for keyword in text_keywords:
            if keyword in self._inverted_index:
                matched_ids.update(self._inverted_index[keyword])

        matched_ids = list(matched_ids)[:self.max_sources]

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

    def _extract_keywords(self, text: str) -> set[str]:
        """提取关键词"""
        keywords = set()
        import re
        tokens = re.findall(r'[\u4e00-\u9fff]+|[A-Za-z]+', text)
        for token in tokens:
            if len(token) >= 2:
                keywords.add(token)
        return keywords
