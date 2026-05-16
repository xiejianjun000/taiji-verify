"""QianAdvance 乾进模块测试"""
import numpy as np
import pytest

class TestQianAdvance:
    def test_qian_advance_init(self):
        from taiji_verify.qian_advance import QianAdvance
        advance = QianAdvance(k_paths=5)
        assert advance.k_paths == 5

    def test_perturb(self):
        from taiji_verify.qian_advance import QianAdvance
        advance = QianAdvance(k_paths=3)
        vec = np.array([1.0, 0.0, 0.0])
        results = advance.perturb(vec)
        assert len(results) == 3
        for r in results:
            assert r.similarity >= 0.0

    def test_perturb_result(self):
        from taiji_verify.qian_advance import PerturbationResult
        result = PerturbationResult(
            path_id=0,
            perturbed_vector=np.array([1.0, 0.0]),
            distance_change=0.1,
            similarity=0.9
        )
        assert result.path_id == 0
        assert result.similarity == 0.9
