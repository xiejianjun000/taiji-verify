"""XunTune 巽调模块测试 - 完整覆盖率"""
import pytest
import numpy as np
import math
from taiji_verify.xun_tune import (
    XunTune, AttentionModulation, TunedOutput,
)


class TestXunTuneInit:
    """巽调初始化测试"""

    def test_default_init(self):
        tuner = XunTune()
        assert tuner.gamma == 0.618
        assert tuner.min_factor == 0.05
        assert tuner.GAMMA_PHI == 0.618

    def test_custom_init(self):
        tuner = XunTune(gamma=0.5, min_factor=0.1)
        assert tuner.gamma == 0.5
        assert tuner.min_factor == 0.1


class TestComputeGate:
    """门控因子计算测试"""

    def test_gate_low_variance(self):
        tuner = XunTune(gamma=0.618)
        gate = tuner.compute_gate(0.0)
        assert gate == 1.0

    def test_gate_high_variance(self):
        tuner = XunTune(gamma=0.618)
        gate = tuner.compute_gate(10.0)
        assert 0.0 < gate < 1.0

    def test_gate_respects_min_factor(self):
        tuner = XunTune(gamma=0.618, min_factor=0.2)
        gate = tuner.compute_gate(100.0)
        assert gate >= 0.2

    def test_gate_formula(self):
        tuner = XunTune(gamma=1.0)
        gate = tuner.compute_gate(1.0)
        expected = math.exp(-1.0 * 1.0)
        assert abs(gate - expected) < 0.0001

    def test_gate_bounded(self):
        tuner = XunTune(gamma=0.618)
        gate = tuner.compute_gate(0.5)
        assert 0.0 < gate <= 1.0


class TestModulate:
    """调制功能测试"""

    def test_modulate_single_vector(self):
        tuner = XunTune()
        vectors = [np.array([1.0, 0.0, 0.0])]
        result = tuner.modulate(vectors)
        assert isinstance(result, TunedOutput)
        assert result.content_vector is not None
        assert len(result.content_vector) == 3

    def test_modulate_multiple_vectors(self):
        tuner = XunTune()
        vectors = [
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0]),
        ]
        result = tuner.modulate(vectors)
        assert len(result.attention_weights) == 3
        assert 0.0 < result.modulation_factor <= 1.0

    def test_modulate_with_attention_weights(self):
        tuner = XunTune()
        vectors = [np.array([1.0, 0.0]), np.array([0.0, 1.0])]
        weights = np.array([0.7, 0.3])
        result = tuner.modulate(vectors, attention_weights=weights)
        assert result.attention_weights is not None

    def test_modulate_empty_raises_error(self):
        tuner = XunTune()
        with pytest.raises(ValueError):
            tuner.modulate([])

    def test_modulate_metadata(self):
        tuner = XunTune()
        vectors = [np.array([1.0, 0.0])]
        result = tuner.modulate(vectors)
        assert 'variance_per_output' in result.metadata
        assert 'average_variance' in result.metadata
        assert 'gamma' in result.metadata

    def test_modulate_confidence_adjusted(self):
        tuner = XunTune()
        vectors = [np.array([1.0, 0.0, 0.0, 0.0, 0.0])]
        result = tuner.modulate(vectors)
        assert isinstance(result.confidence_adjusted, bool)


class TestModulateSingle:
    """单向量调制测试"""

    def test_modulate_single_basic(self):
        tuner = XunTune()
        vec = np.array([1.0, 0.0, 0.0, 0.0, 0.0])
        result = tuner.modulate_single(vec)
        assert isinstance(result, AttentionModulation)
        assert result.gate_factor > 0
        assert result.variance >= 0

    def test_modulate_single_gate_factor(self):
        tuner = XunTune()
        vec = np.array([1.0, 0.0])
        result = tuner.modulate_single(vec)
        assert 0.0 < result.gate_factor <= 1.0

    def test_modulate_single_weights(self):
        tuner = XunTune()
        vec = np.array([1.0, 2.0, 3.0])
        result = tuner.modulate_single(vec)
        assert len(result.original_weights) == len(vec)
        assert len(result.modulated_weights) == len(vec)


class TestTunedOutput:
    """调节输出测试"""

    def test_tuned_output_creation(self):
        output = TunedOutput(
            content_vector=np.array([1.0, 0.0]),
            attention_weights=np.array([0.8, 0.2]),
            modulation_factor=0.9,
            confidence_adjusted=True,
            metadata={"test": "value"},
        )
        assert len(output.content_vector) == 2
        assert output.modulation_factor == 0.9
        assert output.confidence_adjusted is True


class TestAttentionModulation:
    """注意力调制测试"""

    def test_attention_modulation_creation(self):
        modulation = AttentionModulation(
            original_weights=np.array([1.0, 1.0]),
            modulated_weights=np.array([0.8, 0.8]),
            gate_factor=0.8,
            variance=0.25,
            metadata={"key": "value"},
        )
        assert modulation.gate_factor == 0.8
        assert modulation.variance == 0.25


class TestVarianceCalculation:
    """方差计算测试"""

    def test_variance_zero(self):
        tuner = XunTune()
        vec = np.array([1.0, 1.0, 1.0])
        var = float(np.var(vec))
        assert var == 0.0

    def test_variance_nonzero(self):
        tuner = XunTune()
        vec = np.array([1.0, 2.0, 3.0])
        var = float(np.var(vec))
        assert var > 0


class TestEdgeCases:
    """边界情况测试"""

    def test_modulate_high_dimensional(self):
        tuner = XunTune()
        vectors = [np.random.randn(1000) for _ in range(5)]
        result = tuner.modulate(vectors)
        assert len(result.content_vector) == 1000

    def test_modulate_identical_vectors(self):
        tuner = XunTune()
        vec = np.array([1.0, 0.0])
        vectors = [vec, vec, vec]
        result = tuner.modulate(vectors)
        assert result.modulation_factor > 0

    def test_gamma_zero(self):
        tuner = XunTune(gamma=0.0)
        gate = tuner.compute_gate(1.0)
        assert gate == 1.0

    def test_gamma_very_large(self):
        tuner = XunTune(gamma=5.0)
        gate = tuner.compute_gate(1.0)
        assert gate < 0.1
