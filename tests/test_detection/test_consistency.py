"""
Self Consistency Checker Tests
"""

import pytest
import numpy as np
from taiji_verify.detection.consistency import (
    SelfConsistencyChecker, SimilarityResult, SamplingConfig, ConsistencyResult
)


class TestSelfConsistencyChecker:
    """自一致性检查器测试"""

    def test_jaccard_similarity(self):
        """测试Jaccard相似度"""
        checker = SelfConsistencyChecker()
        set1 = {"环境", "保护", "法"}
        set2 = {"环境", "法", "规"}
        sim = checker.jaccard_similarity(set1, set2)
        assert 0.4 < sim < 0.7

    def test_levenshtein_similarity(self):
        """测试Levenshtein相似度"""
        checker = SelfConsistencyChecker()
        sim = checker.levenshtein_similarity("环境保护", "环境保护法")
        assert sim > 0.5

    def test_cosine_similarity(self):
        """测试余弦相似度"""
        checker = SelfConsistencyChecker()
        vec1 = np.array([1.0, 0.0, 1.0])
        vec2 = np.array([1.0, 1.0, 1.0])
        sim = checker.cosine_similarity(vec1, vec2)
        assert 0.8 < sim <= 1.0

    def test_check_self_consistency(self):
        """测试自一致性检查"""
        checker = SelfConsistencyChecker(default_samples=3)
        counter = [0]
        def sampler():
            counter[0] += 1
            return "环境保护法是中国环境保护的基本法律"
        result = checker.check_self_consistency(sampler)
        assert result.avg_similarity > 0.7
        assert len(result.samples) == 3

    def test_batch_consistency(self):
        """测试批量一致性"""
        checker = SelfConsistencyChecker()
        texts = ["环境保护法", "环境保护法律", "环境保护法规"]
        result = checker.batch_consistency(texts)
        assert result.avg_similarity > 0.3

    def test_all_methods(self):
        """测试所有相似度方法"""
        checker = SelfConsistencyChecker()
        results = checker.check_with_all_methods("环境保护法", "环境保护法规")
        assert 'jaccard' in results
        assert 'levenshtein' in results
        assert 'cosine' in results
        assert all(0 <= r <= 1 for r in results.values())

    def test_empty_sets(self):
        """测试空集合"""
        checker = SelfConsistencyChecker()
        assert checker.jaccard_similarity(set(), set()) == 0.0
        assert checker.levenshtein_similarity("", "") == 1.0

    def test_threshold(self):
        """测试阈值"""
        checker = SelfConsistencyChecker(threshold=0.9)
        result = checker.batch_consistency(["相同文本", "相同文本"])
        assert result.avg_similarity == 1.0
