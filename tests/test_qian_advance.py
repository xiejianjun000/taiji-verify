"""QianAdvance 乾进模块测试 - 完整覆盖率"""
import pytest
import numpy as np
from taiji_verify.qian_advance import (
    QianAdvance, PerturbationResult, QianAdvanceResult,
)


class TestQianAdvanceInit:
    """乾进初始化测试"""

    def test_default_init(self):
        advance = QianAdvance()
        assert advance.k_paths == 5
        assert advance.noise_scale == 0.1
        assert advance.max_iterations == 10
        assert advance.convergence_threshold == 0.01
        assert advance.stability_threshold == 0.7

    def test_custom_init(self):
        advance = QianAdvance(
            k_paths=10,
            noise_scale=0.2,
            max_iterations=20,
            convergence_threshold=0.05,
            stability_threshold=0.8,
        )
        assert advance.k_paths == 10
        assert advance.noise_scale == 0.2
        assert advance.max_iterations == 20


class TestPerturbation:
    """扰动功能测试"""

    def test_perturb_single_vector(self):
        advance = QianAdvance(k_paths=5)
        vec = np.array([1.0, 0.0, 0.0])
        results = advance.perturb(vec)
        assert len(results) == 5

    def test_perturb_all_results_valid(self):
        advance = QianAdvance(k_paths=3)
        vec = np.array([1.0, 0.0, 0.0])
        results = advance.perturb(vec)
        for r in results:
            assert isinstance(r, PerturbationResult)
            assert r.path_id in [0, 1, 2]
            assert r.similarity >= -1.0
            assert r.similarity <= 1.0
            assert r.distance_change >= 0.0

    def test_perturb_high_dimensional(self):
        advance = QianAdvance(k_paths=5)
        vec = np.random.randn(100)
        results = advance.perturb(vec)
        assert len(results) == 5


class TestStabilityComputation:
    """稳定性计算测试"""

    def test_compute_stability_with_results(self):
        advance = QianAdvance()
        results = [
            PerturbationResult(0, np.array([1.0, 0.0]), 0.1, 0.9),
            PerturbationResult(1, np.array([0.0, 1.0]), 0.2, 0.8),
            PerturbationResult(2, np.array([0.5, 0.5]), 0.15, 0.85),
        ]
        stability = advance.compute_stability(results)
        assert 0.0 <= stability <= 1.0

    def test_compute_stability_empty_results(self):
        advance = QianAdvance()
        stability = advance.compute_stability([])
        assert stability == 1.0

    def test_stability_formula(self):
        advance = QianAdvance()
        results = [
            PerturbationResult(0, np.array([1.0, 0.0]), 0.0, 1.0),
        ]
        stability = advance.compute_stability(results)
        assert stability == 1.0


class TestEvolve:
    """演进功能测试"""

    def test_evolve_basic(self):
        advance = QianAdvance(k_paths=5, max_iterations=3)
        vec = np.array([1.0, 0.0, 0.0])
        result = advance.evolve(vec)
        assert isinstance(result, QianAdvanceResult)
        assert result.original_vector is not None
        assert result.evolved_vector is not None

    def test_evolve_iterations(self):
        advance = QianAdvance(k_paths=5, max_iterations=3)
        vec = np.array([1.0, 0.0, 0.0])
        result = advance.evolve(vec)
        assert result.iterations >= 1

    def test_evolve_converged(self):
        advance = QianAdvance(
            k_paths=5,
            max_iterations=100,
            stability_threshold=0.7,
        )
        vec = np.array([1.0, 0.0, 0.0])
        result = advance.evolve(vec)
        assert result.converged is not None

    def test_evolve_metadata(self):
        advance = QianAdvance(k_paths=5)
        vec = np.array([1.0, 0.0, 0.0])
        result = advance.evolve(vec)
        assert 'k_paths' in result.metadata
        assert 'noise_scale' in result.metadata


class TestStabilityProperties:
    """稳定性属性测试"""

    def test_is_stable_true(self):
        result = QianAdvanceResult(
            original_vector=np.array([1.0, 0.0]),
            evolved_vector=np.array([1.0, 0.0]),
            stability_score=0.8,
            path_results=[],
            converged=True,
            iterations=5,
        )
        assert result.is_stable is True

    def test_is_stable_false(self):
        result = QianAdvanceResult(
            original_vector=np.array([1.0, 0.0]),
            evolved_vector=np.array([1.0, 0.0]),
            stability_score=0.5,
            path_results=[],
            converged=False,
            iterations=5,
        )
        assert result.is_stable is False

    def test_needs_revision_true(self):
        result = QianAdvanceResult(
            original_vector=np.array([1.0, 0.0]),
            evolved_vector=np.array([1.0, 0.0]),
            stability_score=0.3,
            path_results=[],
            converged=False,
            iterations=5,
        )
        assert result.needs_revision is True

    def test_needs_revision_false(self):
        result = QianAdvanceResult(
            original_vector=np.array([1.0, 0.0]),
            evolved_vector=np.array([1.0, 0.0]),
            stability_score=0.5,
            path_results=[],
            converged=False,
            iterations=5,
        )
        assert result.needs_revision is False


class TestAnalyzePaths:
    """路径分析测试"""

    def test_analyze_paths(self):
        advance = QianAdvance(k_paths=5)
        vec = np.array([1.0, 0.0, 0.0])
        avg_delta, avg_sim, stability = advance.analyze_paths(vec)
        assert avg_delta >= 0.0
        assert -1.0 <= avg_sim <= 1.0
        assert 0.0 <= stability <= 1.0

    def test_analyze_paths_deterministic(self):
        advance = QianAdvance(k_paths=3)
        vec = np.array([1.0, 0.0, 0.0])
        avg_delta1, avg_sim1, stability1 = advance.analyze_paths(vec)
        avg_delta2, avg_sim2, stability2 = advance.analyze_paths(vec)
        assert avg_delta1 == avg_delta2


class TestOptimizeVector:
    """向量优化测试"""

    def test_optimize_vector(self):
        advance = QianAdvance(k_paths=5, max_iterations=3)
        vec = np.array([1.0, 0.0, 0.0])
        optimized = advance.optimize_vector(vec)
        assert optimized is not None
        assert len(optimized) == len(vec)

    def test_optimize_vector_with_iterations(self):
        advance = QianAdvance(k_paths=5, max_iterations=10)
        vec = np.array([1.0, 0.0, 0.0])
        optimized = advance.optimize_vector(vec, iterations=5)
        assert optimized is not None


class TestBatchEvolve:
    """批量演进测试"""

    def test_batch_evolve(self):
        advance = QianAdvance(k_paths=3, max_iterations=3)
        vectors = [
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0]),
        ]
        results = advance.batch_evolve(vectors)
        assert len(results) == 3
        for result in results:
            assert isinstance(result, QianAdvanceResult)

    def test_batch_evolve_empty(self):
        advance = QianAdvance()
        results = advance.batch_evolve([])
        assert len(results) == 0


class TestPerturbationResult:
    """扰动结果测试"""

    def test_perturbation_result_creation(self):
        result = PerturbationResult(
            path_id=5,
            perturbed_vector=np.array([0.5, 0.5]),
            distance_change=0.2,
            similarity=0.9,
        )
        assert result.path_id == 5
        assert result.distance_change == 0.2
        assert result.similarity == 0.9


class TestDistanceChange:
    """距离变化计算测试"""

    def test_identical_vectors(self):
        advance = QianAdvance()
        vec = np.array([1.0, 0.0])
        delta = advance._compute_distance_change(vec, vec)
        assert delta == 0.0

    def test_opposite_vectors(self):
        advance = QianAdvance()
        v1 = np.array([1.0, 0.0])
        v2 = np.array([-1.0, 0.0])
        delta = advance._compute_distance_change(v1, v2)
        assert delta > 1.0


class TestSimilarity:
    """相似度计算测试"""

    def test_identical_similarity(self):
        advance = QianAdvance()
        vec = np.array([1.0, 0.0])
        sim = advance._compute_similarity(vec, vec)
        assert abs(sim - 1.0) < 0.0001

    def test_orthogonal_similarity(self):
        advance = QianAdvance()
        v1 = np.array([1.0, 0.0])
        v2 = np.array([0.0, 1.0])
        sim = advance._compute_similarity(v1, v2)
        assert abs(sim) < 0.0001

    def test_opposite_similarity(self):
        advance = QianAdvance()
        v1 = np.array([1.0, 0.0])
        v2 = np.array([-1.0, 0.0])
        sim = advance._compute_similarity(v1, v2)
        assert abs(sim - (-1.0)) < 0.0001
