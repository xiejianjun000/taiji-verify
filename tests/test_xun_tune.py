"""XunTune 巽调模块测试"""
import numpy as np
import pytest

class TestXunTune:
    def test_xun_tune_init(self):
        from taiji_verify.xun_tune import XunTune
        tuner = XunTune()
        assert tuner is not None

    def test_gamma_value(self):
        from taiji_verify.xun_tune import XunTune
        tuner = XunTune()
        assert tuner.gamma > 0
        assert tuner.GAMMA_PHI is not None

    def test_modulate_method_exists(self):
        from taiji_verify.xun_tune import XunTune
        tuner = XunTune()
        assert hasattr(tuner, 'modulate')
        assert callable(tuner.modulate)
