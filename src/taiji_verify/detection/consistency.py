"""
Self Consistency Checker - 自一致性检查

对应 SelfConsistencyChecker.ts 的 Python 实现

功能:
- 3种相似度: Jaccard / Levenshtein / Cosine
- Levenshtein用1D数组优化
- 两两比较平均相似度
- 默认3次采样，阈值0.7
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional
import numpy as np


@dataclass
class SimilarityResult:
    """相似度结果"""
    similarity: float
    method: str
    samples: list = field(default_factory=list)


@dataclass
class SamplingConfig:
    """采样配置"""
    num_samples: int = 3
    threshold: float = 0.7
    methods: list[str] = field(default_factory=lambda: ["jaccard", "levenshtein", "cosine"])


@dataclass
class ConsistencyResult:
    """一致性检查结果"""
    passed: bool
    avg_similarity: float
    samples: list
    details: dict = field(default_factory=dict)


class SelfConsistencyChecker:
    """
    自一致性检查器

    Usage::
        checker = SelfConsistencyChecker()
        def sampler():
            return "碳排放权交易管理办法"
        result = checker.check_self_consistency(sampler)
        print(result.passed, result.avg_similarity)
    """

    def __init__(self, default_samples: int = 3, threshold: float = 0.7):
        self.default_samples = default_samples
        self.threshold = threshold

    def jaccard_similarity(self, set1: set, set2: set) -> float:
        """
        Jaccard相似度

        Args:
            set1: 集合1
            set2: 集合2

        Returns:
            Jaccard相似度 ∈ [0, 1]
        """
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def levenshtein_similarity(self, s1: str, s2: str) -> float:
        """
        Levenshtein距离转相似度

        Args:
            s1: 字符串1
            s2: 字符串2

        Returns:
            Levenshtein相似度 ∈ [0, 1]
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        m, n = len(s1), len(s2)
        if m > n:
            s1, s2 = s2, s1
            m, n = n, m

        distances = list(range(m + 1))
        for i in range(1, n + 1):
            prev = [0] * (m + 1)
            prev[0] = i
            for j in range(1, m + 1):
                cost = 0 if s1[j - 1] == s2[i - 1] else 1
                prev[j] = min(
                    distances[j] + 1,
                    prev[j - 1] + 1,
                    distances[j - 1] + cost
                )
            distances = prev

        distance = distances[m]
        max_len = max(len(s1), len(s2))
        return 1.0 - (distance / max_len) if max_len > 0 else 1.0

    def cosine_similarity(self, vec1: list | np.ndarray, vec2: list | np.ndarray) -> float:
        """
        Cosine相似度

        Args:
            vec1: 向量1
            vec2: 向量2

        Returns:
            Cosine相似度 ∈ [-1, 1]
        """
        if isinstance(vec1, list):
            vec1 = np.array(vec1)
        if isinstance(vec2, list):
            vec2 = np.array(vec2)

        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 < 1e-10 or norm2 < 1e-10:
            return 0.0

        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    def check_self_consistency(
        self,
        sampler_fn: Callable[[], str],
        samples: Optional[int] = None,
    ) -> ConsistencyResult:
        """
        自一致性检查

        Args:
            sampler_fn: 采样函数
            samples: 采样次数

        Returns:
            ConsistencyResult 一致性结果
        """
        n = samples or self.default_samples
        texts = [sampler_fn() for _ in range(n)]

        if n < 2:
            return ConsistencyResult(passed=True, avg_similarity=1.0, samples=texts)

        similarities = []
        for i in range(n):
            for j in range(i + 1, n):
                sim = self.levenshtein_similarity(texts[i], texts[j])
                similarities.append(sim)

        avg_sim = np.mean(similarities) if similarities else 1.0
        passed = avg_sim >= self.threshold

        return ConsistencyResult(
            passed=passed,
            avg_similarity=float(avg_sim),
            samples=texts,
            details={
                'pairwise_similarities': similarities,
                'threshold': self.threshold,
            },
        )

    def batch_consistency(self, texts: list[str]) -> ConsistencyResult:
        """
        批量文本一致性检查

        Args:
            texts: 文本列表

        Returns:
            ConsistencyResult 一致性结果
        """
        if len(texts) < 2:
            return ConsistencyResult(passed=True, avg_similarity=1.0, samples=texts)

        similarities = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                sim = self.levenshtein_similarity(texts[i], texts[j])
                similarities.append(sim)

        avg_sim = np.mean(similarities) if similarities else 1.0
        passed = avg_sim >= self.threshold

        return ConsistencyResult(
            passed=passed,
            avg_similarity=float(avg_sim),
            samples=texts,
            details={
                'pairwise_similarities': similarities,
                'threshold': self.threshold,
            },
        )

    def check_with_all_methods(self, text1: str, text2: str) -> dict[str, float]:
        """
        使用所有方法检查相似度

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            各方法的相似度字典
        """
        set1 = set(text1)
        set2 = set(text2)

        vec1 = np.array([1.0 if c in set1 else 0.0 for c in set(set1 | set2)])
        vec2 = np.array([1.0 if c in set2 else 0.0 for c in set(set1 | set2)])

        return {
            'jaccard': self.jaccard_similarity(set1, set2),
            'levenshtein': self.levenshtein_similarity(text1, text2),
            'cosine': self.cosine_similarity(vec1, vec2),
        }
