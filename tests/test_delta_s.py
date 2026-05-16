"""DeltaS 阴阳距计算器测试"""
import math
import pytest
import numpy as np
from numpy.linalg import norm

@pytest.fixture
def dim():
    return 128

@pytest.fixture
def random_vectors(dim):
    rng = np.random.RandomState(42)
    identical = rng.randn(dim).astype(np.float32)
    similar = identical + rng.randn(dim).astype(np.float32) * 0.1
    different = rng.randn(dim).astype(np.float32)
    return {
        'identical': identical / norm(identical),
        'similar': similar / norm(similar),
        'different': different / norm(different),
    }

class TestDeltaS:
    def test_identical_vectors_zero_delta(self, random_vectors):
        from taiji_verify.delta_s import DeltaSCalculator, GateZone
        calc = DeltaSCalculator()
        result = calc.compute(random_vectors['identical'], random_vectors['identical'])
        assert result.delta_s < 0.01
        assert result.zone == GateZone.SAFE
        assert result.cosine_similarity > 0.99
        assert result.is_safe is True

    def test_different_vectors_higher_delta(self, random_vectors):
        from taiji_verify.delta_s import DeltaSCalculator
        calc = DeltaSCalculator()
        result_similar = calc.compute(random_vectors['similar'], random_vectors['identical'])
        result_diff = calc.compute(random_vectors['different'], random_vectors['identical'])
        assert result_diff.delta_s > result_similar.delta_s

    def test_gate_zone_mapping(self):
        from taiji_verify.delta_s import GateZone
        assert GateZone.from_delta(0.1) == GateZone.SAFE
        assert GateZone.from_delta(0.35) == GateZone.SAFE
        assert GateZone.from_delta(0.4) == GateZone.TRANSIT
        assert GateZone.from_delta(0.5) == GateZone.TRANSIT
        assert GateZone.from_delta(0.6) == GateZone.RISK
        assert GateZone.from_delta(0.85) == GateZone.DANGER

    def test_delta_s_zero_at_identical(self):
        vec = np.array([1.0, 0.0, 0.0])
        from taiji_verify.delta_s import DeltaSCalculator
        calc = DeltaSCalculator()
        result = calc.compute(vec, vec)
        assert result.delta_s < 0.001

    def test_delta_s_geometry_bounds(self):
        from taiji_verify.delta_s import DeltaSCalculator
        rng = np.random.RandomState(123)
        calc = DeltaSCalculator()
        for _ in range(10):
            v1 = rng.randn(128).astype(np.float32)
            v2 = rng.randn(128).astype(np.float32)
            v1 /= norm(v1)
            v2 /= norm(v2)
            result = calc.compute(v1, v2)
            assert 0 <= result.delta_s <= math.sqrt(2) + 1e-6
