"""GuanObserve 观变模块测试"""
import pytest

class TestGuanObserve:
    def test_observe_basic(self):
        from taiji_verify.guan_observe import GuanObserve
        observer = GuanObserve()
        assert observer is not None
        assert observer.history_length == 0

    def test_guan_observe_init(self):
        from taiji_verify.guan_observe import GuanObserve
        observer = GuanObserve(anomaly_threshold=0.5)
        assert observer.anomaly_threshold == 0.5
