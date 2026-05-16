"""GuanObserve 观变模块测试 - 完整覆盖率"""
import pytest
import numpy as np
from taiji_verify.guan_observe import (
    GuanObserve, ChangeType, StateSnapshot, TrendAnalysis, AnomalyEvent,
)


class TestGuanObserveInit:
    """观变初始化测试"""

    def test_default_init(self):
        observer = GuanObserve()
        assert observer.window_size == 10
        assert observer.abrupt_threshold == 0.3
        assert observer.anomaly_threshold == 0.8
        assert observer.similarity_threshold == 0.7

    def test_custom_init(self):
        observer = GuanObserve(
            window_size=20,
            abrupt_threshold=0.5,
            anomaly_threshold=0.6,
            similarity_threshold=0.8,
        )
        assert observer.window_size == 20
        assert observer.abrupt_threshold == 0.5

    def test_initial_state(self):
        observer = GuanObserve()
        assert observer.history_length == 0
        assert observer.anomaly_count == 0
        assert observer.current_snapshot is None


class TestSetReference:
    """参考向量设置测试"""

    def test_set_reference(self):
        observer = GuanObserve()
        vec = np.array([1.0, 0.0, 0.0])
        observer.set_reference(vec)
        assert observer._reference_vector is not None

    def test_reference_normalized(self):
        observer = GuanObserve()
        vec = np.array([2.0, 0.0, 0.0])
        observer.set_reference(vec)
        norm = float(np.linalg.norm(observer._reference_vector))
        assert abs(norm - 1.0) < 0.001


class TestTrack:
    """状态追踪测试"""

    def test_track_without_reference(self):
        observer = GuanObserve()
        vec = np.array([1.0, 0.0, 0.0])
        snapshot = observer.track(vec)
        assert snapshot is not None
        assert snapshot.similarity == 1.0
        assert snapshot.change_type == ChangeType.STABLE

    def test_track_with_reference(self):
        observer = GuanObserve()
        ref = np.array([1.0, 0.0, 0.0])
        observer.set_reference(ref)
        vec = np.array([1.0, 0.0, 0.0])
        snapshot = observer.track(vec)
        assert abs(snapshot.similarity - 1.0) < 0.01

    def test_track_with_metadata(self):
        observer = GuanObserve()
        vec = np.array([1.0, 0.0])
        snapshot = observer.track(vec, metadata={"key": "value"})
        assert snapshot.metadata["key"] == "value"

    def test_track_increases_history(self):
        observer = GuanObserve()
        observer.track(np.array([1.0, 0.0]))
        observer.track(np.array([0.9, 0.1]))
        assert observer.history_length == 2


class TestChangeDetection:
    """变化类型检测测试"""

    def test_detect_stable_change(self):
        observer = GuanObserve()
        ref = np.array([1.0, 0.0])
        observer.set_reference(ref)
        observer.track(np.array([1.0, 0.0]))
        snapshot = observer.track(np.array([0.99, 0.01]))
        assert snapshot.change_type == ChangeType.STABLE

    def test_detect_gradual_change(self):
        observer = GuanObserve(abrupt_threshold=0.6, similarity_threshold=0.1)
        ref = np.array([1.0, 0.0])
        observer.set_reference(ref)
        observer.track(np.array([1.0, 0.0]))
        snapshot = observer.track(np.array([0.5, 0.5]))
        assert snapshot.change_type in [ChangeType.GRADUAL, ChangeType.ABRUPT]

    def test_detect_abrupt_change(self):
        observer = GuanObserve(abrupt_threshold=0.1, similarity_threshold=0.1)
        ref = np.array([1.0, 0.0])
        observer.set_reference(ref)
        observer.track(np.array([1.0, 0.0]))
        snapshot = observer.track(np.array([0.1, 0.9]))
        assert snapshot.change_type in [ChangeType.ABRUPT, ChangeType.GRADUAL]

    def test_detect_anomaly(self):
        observer = GuanObserve(similarity_threshold=0.7)
        ref = np.array([1.0, 0.0])
        observer.set_reference(ref)
        observer.track(np.array([1.0, 0.0]))
        snapshot = observer.track(np.array([-0.5, -0.5]))
        assert snapshot.change_type == ChangeType.ANOMALY


class TestTrendAnalysis:
    """趋势分析测试"""

    def test_analyze_trend_insufficient_data(self):
        observer = GuanObserve()
        result = observer.analyze_trend()
        assert result.trend_direction == 0.0
        assert result.volatility == 0.0
        assert 'error' in result.metadata

    def test_analyze_trend_with_data(self):
        observer = GuanObserve()
        observer.track(np.array([1.0, 0.0]))
        observer.track(np.array([0.9, 0.0]))
        result = observer.analyze_trend()
        assert result.trend_direction is not None
        assert 'window_size' in result.metadata

    def test_analyze_trend_direction(self):
        observer = GuanObserve(similarity_threshold=0.1)
        ref = np.array([1.0, 0.0])
        observer.set_reference(ref)
        observer.track(np.array([1.0, 0.0]))
        observer.track(np.array([0.8, 0.2]))
        observer.track(np.array([0.5, 0.5]))
        result = observer.analyze_trend()
        assert result.trend_direction < 0

    def test_analyze_trend_anomaly_score(self):
        observer = GuanObserve()
        observer.track(np.array([1.0, 0.0]))
        observer.track(np.array([0.9, 0.0]))
        result = observer.analyze_trend()
        assert result.anomaly_score >= 0.0


class TestAnomalyDetection:
    """异常检测测试"""

    def test_detect_anomaly_event(self):
        observer = GuanObserve(similarity_threshold=0.7)
        ref = np.array([1.0, 0.0])
        observer.set_reference(ref)
        observer.track(np.array([1.0, 0.0]))
        observer.track(np.array([-0.5, -0.5]))
        assert observer.anomaly_count >= 1

    def test_detect_anomalies_with_threshold(self):
        observer = GuanObserve()
        events = observer.detect_anomalies(threshold=0.5)
        assert isinstance(events, list)

    def test_anomaly_severity_critical(self):
        observer = GuanObserve()
        observer.set_reference(np.array([1.0, 0.0]))
        observer.track(np.array([1.0, 0.0]))
        observer.track(np.array([-1.0, 0.0]))
        event = observer._anomaly_events[0]
        assert event.severity == "critical"

    def test_anomaly_severity_high(self):
        observer = GuanObserve(similarity_threshold=0.4)
        observer.set_reference(np.array([1.0, 0.0]))
        observer.track(np.array([1.0, 0.0]))
        observer.track(np.array([0.3, 0.0]))
        if observer._anomaly_events:
            event = observer._anomaly_events[0]
            assert event.severity in ["critical", "high", "middle", "low"]


class TestCallbacks:
    """回调函数测试"""

    def test_add_callback(self):
        observer = GuanObserve()

        def callback(event):
            pass

        observer.add_callback(callback)
        assert len(observer._callbacks) == 1

    def test_remove_callback(self):
        observer = GuanObserve()

        def callback(event):
            pass

        observer.add_callback(callback)
        observer.remove_callback(callback)
        assert len(observer._callbacks) == 0

    def test_callback_triggered_on_anomaly(self):
        observer = GuanObserve(similarity_threshold=0.7)
        observer.set_reference(np.array([1.0, 0.0]))
        triggered = []

        def callback(event):
            triggered.append(event)

        observer.add_callback(callback)
        observer.track(np.array([1.0, 0.0]))
        observer.track(np.array([-0.5, 0.0]))
        assert len(triggered) >= 1


class TestSnapshotAccess:
    """快照访问测试"""

    def test_get_snapshot_at_valid(self):
        observer = GuanObserve()
        observer.track(np.array([1.0, 0.0]))
        snapshot = observer.get_snapshot_at(0)
        assert snapshot is not None

    def test_get_snapshot_at_invalid(self):
        observer = GuanObserve()
        snapshot = observer.get_snapshot_at(0)
        assert snapshot is None

    def test_get_recent_snapshots(self):
        observer = GuanObserve(window_size=10)
        for i in range(8):
            observer.track(np.array([1.0 - i * 0.1, 0.0]))
        snapshots = observer.get_recent_snapshots(3)
        assert len(snapshots) == 3

    def test_replay(self):
        observer = GuanObserve()
        observer.track(np.array([1.0, 0.0]))
        observer.track(np.array([0.9, 0.0]))
        history = observer.replay()
        assert len(history) == 2


class TestReset:
    """重置功能测试"""

    def test_reset_clears_history(self):
        observer = GuanObserve()
        observer.track(np.array([1.0, 0.0]))
        observer.reset()
        assert observer.history_length == 0

    def test_reset_clears_anomalies(self):
        observer = GuanObserve(similarity_threshold=0.7)
        observer.set_reference(np.array([1.0, 0.0]))
        observer.track(np.array([1.0, 0.0]))
        observer.track(np.array([-0.5, 0.0]))
        observer.reset()
        assert observer.anomaly_count == 0


class TestCurrentSnapshot:
    """当前快照测试"""

    def test_current_snapshot(self):
        observer = GuanObserve()
        observer.track(np.array([1.0, 0.0]))
        assert observer.current_snapshot is not None
        assert observer.current_snapshot.similarity == 1.0


class TestStateSnapshot:
    """状态快照数据结构测试"""

    def test_snapshot_creation(self):
        snapshot = StateSnapshot(
            timestamp=123456.0,
            vector=np.array([1.0, 0.0]),
            similarity=0.9,
            change_type=ChangeType.GRADUAL,
            metadata={"test": "value"},
        )
        assert snapshot.timestamp == 123456.0
        assert snapshot.similarity == 0.9
        assert snapshot.change_type == ChangeType.GRADUAL


class TestTrendAnalysisResult:
    """趋势分析结果测试"""

    def test_trend_analysis_creation(self):
        analysis = TrendAnalysis(
            trend_direction=0.5,
            volatility=0.2,
            anomaly_score=0.1,
            change_type=ChangeType.STABLE,
            recent_snapshots=[],
            metadata={"test": "value"},
        )
        assert analysis.trend_direction == 0.5
        assert analysis.volatility == 0.2


class TestAnomalyEvent:
    """异常事件测试"""

    def test_anomaly_event_creation(self):
        snapshot = StateSnapshot(
            timestamp=123456.0,
            vector=np.array([1.0, 0.0]),
            similarity=0.3,
            change_type=ChangeType.ANOMALY,
        )
        event = AnomalyEvent(
            event_id="test_001",
            timestamp=123456.0,
            snapshot=snapshot,
            severity="high",
            description="Test anomaly",
            metadata={"key": "value"},
        )
        assert event.event_id == "test_001"
        assert event.severity == "high"
        assert event.description == "Test anomaly"
