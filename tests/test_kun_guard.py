"""KunGuard 坤守模块测试"""
import numpy as np
import pytest

class TestKunGuard:
    def test_kun_guard_init(self):
        from taiji_verify.kun_guard import KunGuard
        guard = KunGuard(correction_factor=0.5)
        assert guard.m == 0.5

    def test_compute_residual(self):
        from taiji_verify.kun_guard import KunGuard
        guard = KunGuard()
        input_vec = np.array([1.0, 0.0, 0.0])
        ground_vec = np.array([0.0, 1.0, 0.0])
        residual = guard.compute_residual(input_vec, ground_vec)
        assert 0 <= residual <= 1.0

    def test_check_hazard(self):
        from taiji_verify.kun_guard import KunGuard, HazardLevel
        guard = KunGuard()
        level, needs_correction = guard.check_hazard(0.2)
        assert level == HazardLevel.LOW
        assert not needs_correction
        level, needs_correction = guard.check_hazard(0.7)
        assert level == HazardLevel.HIGH
        assert needs_correction

    def test_correct(self):
        from taiji_verify.kun_guard import KunGuard
        guard = KunGuard()
        input_vec = np.array([1.0, 0.5, 0.2])
        ground_vec = np.array([0.9, 0.4, 0.3])
        result = guard.correct(input_vec, ground_vec)
        assert result.corrected_vector is not None
        assert 0 <= result.residual <= 1.0

    def test_add_knowledge_anchor(self):
        from taiji_verify.kun_guard import KunGuard
        guard = KunGuard()
        vec = np.array([1.0, 0.0, 0.0])
        anchor_id = guard.add_knowledge_anchor("测试锚点", vec)
        assert anchor_id is not None
        assert guard.anchors_count == 1

    def test_correct_with_projection(self):
        from taiji_verify.kun_guard import KunGuard
        guard = KunGuard()
        guard.add_knowledge_anchor("锚点", np.array([1.0, 0.0, 0.0]))
        input_vec = np.array([1.0, 0.0, 0.0])
        ground_vec = np.array([0.0, 1.0, 0.0])
        result = guard.correct_with_projection(input_vec, ground_vec)
        assert result.corrected_vector is not None
