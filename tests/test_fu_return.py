"""FuReturn 复归模块测试 - 完整覆盖率"""
import pytest
import numpy as np
from taiji_verify.fu_return import (
    FuReturn, RecoveryState, CrashingEvent, RecoveryResult,
)


class TestFuReturnInit:
    """FuReturn初始化测试"""

    def test_default_init(self):
        fr = FuReturn()
        assert fr.Bc == 0.8
        assert fr.eps == 0.01
        assert fr.max_retries == 3
        assert fr.recovery_timeout == 30.0

    def test_custom_init(self):
        fr = FuReturn(Bc=0.9, eps=0.02, max_retries=5, recovery_timeout=60.0)
        assert fr.Bc == 0.9
        assert fr.eps == 0.02
        assert fr.max_retries == 5
        assert fr.recovery_timeout == 60.0

    def test_current_state_initial(self):
        fr = FuReturn()
        assert fr.current_state == RecoveryState.NORMAL

    def test_event_history_initial_empty(self):
        fr = FuReturn()
        assert len(fr.event_history) == 0


class TestLyapunovExponent:
    """李雅普诺夫指数计算测试"""

    def test_convergent_history(self):
        fr = FuReturn()
        history = [
            np.array([1.0, 0.0]),
            np.array([0.5, 0.0]),
            np.array([0.25, 0.0]),
            np.array([0.125, 0.0]),
        ]
        lyapunov = fr.compute_lyapunov_exponent(history)
        assert lyapunov < 0

    def test_divergent_history(self):
        fr = FuReturn()
        history = [
            np.array([1.0, 0.0]),
            np.array([1.5, 0.0]),
            np.array([2.25, 0.0]),
            np.array([3.375, 0.0]),
        ]
        lyapunov = fr.compute_lyapunov_exponent(history)
        assert lyapunov > 0

    def test_stable_history(self):
        fr = FuReturn()
        history = [
            np.array([1.0, 1.0]),
            np.array([1.0, 1.0]),
            np.array([1.0, 1.0]),
        ]
        lyapunov = fr.compute_lyapunov_exponent(history)
        assert abs(lyapunov) < 1.0

    def test_insufficient_history(self):
        fr = FuReturn()
        history = [np.array([1.0, 0.0])]
        lyapunov = fr.compute_lyapunov_exponent(history)
        assert lyapunov == 0.0

    def test_empty_history(self):
        fr = FuReturn()
        lyapunov = fr.compute_lyapunov_exponent([])
        assert lyapunov == 0.0


class TestCrashDetection:
    """崩溃检测测试"""

    def test_crashing_high_lyapunov(self):
        fr = FuReturn()
        state = fr.detect_crash(lyapunov=0.9, residual=0.1)
        assert state == RecoveryState.CRASHING

    def test_crashing_high_residual(self):
        fr = FuReturn()
        state = fr.detect_crash(lyapunov=0.3, residual=0.95)
        assert state == RecoveryState.CRASHING

    def test_warning_elevated_lyapunov(self):
        fr = FuReturn()
        state = fr.detect_crash(lyapunov=0.6, residual=0.2)
        assert state == RecoveryState.WARNING

    def test_warning_elevated_residual(self):
        fr = FuReturn()
        state = fr.detect_crash(lyapunov=0.3, residual=0.7)
        assert state == RecoveryState.WARNING

    def test_normal_low_values(self):
        fr = FuReturn()
        state = fr.detect_crash(lyapunov=0.3, residual=0.3)
        assert state == RecoveryState.NORMAL


class TestRecovery:
    """恢复功能测试"""

    def test_recover_success(self):
        fr = FuReturn(Bc=0.8, eps=0.1, max_retries=100)
        current = np.array([0.05, 0.0])
        stable = np.array([0.0, 0.0])
        result = fr.recover(current, stable)
        assert result.final_state == RecoveryState.RECOVERED

    def test_recover_iterations(self):
        fr = FuReturn(Bc=0.8, eps=0.1, max_retries=5)
        current = np.array([0.05, 0.0])
        stable = np.array([0.01, 0.0])
        result = fr.recover(current, stable)
        assert result.iterations >= 1

    def test_recover_failure_max_retries(self):
        fr = FuReturn(Bc=0.8, eps=0.000001, max_retries=1)
        current = np.array([1.0, 1.0])
        stable = np.array([0.0, 0.0])
        result = fr.recover(current, stable)
        assert result.success is False
        assert result.final_state == RecoveryState.FAILED

    def test_recover_records_events(self):
        fr = FuReturn(max_retries=3)
        current = np.array([0.5, 0.5])
        stable = np.array([0.0, 0.0])
        initial_events = len(fr.event_history)
        fr.recover(current, stable)
        assert len(fr.event_history) > initial_events


class TestAdaptiveRecovery:
    """自适应恢复测试"""

    def test_hard_reset_severe_instability(self):
        fr = FuReturn()
        current = np.array([1.0, 0.0])
        stable = np.array([0.0, 1.0])
        result = fr.adaptive_recover(current, stable, lyapunov=1.5)
        assert result.success is True
        assert result.metadata.get('strategy') == 'hard_reset'

    def test_fast_convergence_moderate_instability(self):
        fr = FuReturn()
        current = np.array([0.001, 0.0])
        stable = np.array([0.0, 0.0])
        result = fr.adaptive_recover(current, stable, lyapunov=0.7)
        assert result.final_state == RecoveryState.RECOVERED

    def test_fine_tune_mild_instability(self):
        fr = FuReturn()
        current = np.array([1.0, 0.0])
        stable = np.array([0.0, 1.0])
        result = fr.adaptive_recover(current, stable, lyapunov=0.3)
        assert result.success is True
        assert result.metadata.get('strategy') == 'fine_tune'


class TestMonitorAndRecover:
    """监控与恢复测试"""

    def test_monitor_insufficient_history(self):
        fr = FuReturn()
        history = [np.array([1.0, 0.0])]
        stable = np.array([0.0, 1.0])
        result = fr.monitor_and_recover(history, stable)
        assert result.success is True
        assert result.final_state == RecoveryState.NORMAL

    def test_monitor_no_action_needed(self):
        fr = FuReturn()
        history = [
            np.array([0.0, 0.0]),
            np.array([0.1, 0.0]),
            np.array([0.1, 0.0]),
        ]
        stable = np.array([0.0, 0.0])
        result = fr.monitor_and_recover(history, stable)
        assert result.final_state == RecoveryState.NORMAL
        assert result.iterations == 0

    def test_monitor_warning_state(self):
        fr = FuReturn(Bc=0.8)
        history = [
            np.array([0.0, 0.0]),
            np.array([0.6, 0.0]),
            np.array([0.7, 0.0]),
        ]
        stable = np.array([0.0, 0.0])
        result = fr.monitor_and_recover(history, stable)
        assert result.final_state == RecoveryState.RECOVERED

    def test_monitor_crashing_state(self):
        fr = FuReturn(Bc=0.8)
        history = [
            np.array([0.0, 0.0]),
            np.array([0.5, 0.0]),
            np.array([1.0, 0.0]),
            np.array([1.5, 0.0]),
        ]
        stable = np.array([0.0, 0.0])
        result = fr.monitor_and_recover(history, stable)
        assert result.final_state == RecoveryState.RECOVERED

    def test_monitor_records_events(self):
        fr = FuReturn()
        history = [
            np.array([0.0, 0.0]),
            np.array([0.5, 0.0]),
            np.array([1.0, 0.0]),
        ]
        stable = np.array([0.0, 0.0])
        initial_count = len(fr.event_history)
        fr.monitor_and_recover(history, stable)
        assert len(fr.event_history) > initial_count


class TestStateTransitions:
    """状态转换测试"""

    def test_state_machine_normal_to_warning(self):
        fr = FuReturn()
        fr._record_event(RecoveryState.NORMAL, 0.0, 0.1)
        fr._record_event(RecoveryState.WARNING, 0.6, 0.5)
        assert fr.current_state == RecoveryState.WARNING

    def test_state_machine_warning_to_crashing(self):
        fr = FuReturn()
        fr._record_event(RecoveryState.WARNING, 0.6, 0.5)
        fr._record_event(RecoveryState.CRASHING, 0.9, 0.95)
        assert fr.current_state == RecoveryState.CRASHING

    def test_state_machine_full_recovery_cycle(self):
        fr = FuReturn()
        fr._record_event(RecoveryState.NORMAL, 0.1, 0.1)
        fr._record_event(RecoveryState.WARNING, 0.6, 0.5)
        fr._record_event(RecoveryState.CRASHING, 0.9, 0.95)
        fr._record_event(RecoveryState.RECOVERING, 0.5, 0.3)
        fr._record_event(RecoveryState.RECOVERED, 0.0, 0.01)
        assert fr.current_state == RecoveryState.RECOVERED
        assert len(fr.event_history) == 5

    def test_state_machine_failure_recovery(self):
        fr = FuReturn()
        fr._record_event(RecoveryState.CRASHING, 0.95, 0.95)
        fr._record_event(RecoveryState.RECOVERING, 0.9, 0.8)
        fr._record_event(RecoveryState.FAILED, 0.9, 0.9)
        assert fr.current_state == RecoveryState.FAILED


class TestCallbacks:
    """回调函数测试"""

    def test_add_callback(self):
        fr = FuReturn()
        def dummy_callback(event):
            pass
        fr.add_recovery_callback(dummy_callback)
        assert len(fr._recovery_callbacks) == 1

    def test_remove_callback(self):
        fr = FuReturn()
        def dummy_callback(event):
            pass
        fr.add_recovery_callback(dummy_callback)
        fr.remove_recovery_callback(dummy_callback)
        assert len(fr._recovery_callbacks) == 0

    def test_remove_nonexistent_callback(self):
        fr = FuReturn()
        def dummy_callback(event):
            pass
        fr.remove_recovery_callback(dummy_callback)
        assert len(fr._recovery_callbacks) == 0

    def test_trigger_callbacks(self):
        fr = FuReturn()
        results = []

        def callback1(event):
            results.append(1)

        def callback2(event):
            results.append(2)

        fr.add_recovery_callback(callback1)
        fr.add_recovery_callback(callback2)

        event = CrashingEvent(
            event_id="test",
            timestamp=0.0,
            state=RecoveryState.NORMAL,
            lyapunov_exponent=0.0,
            residual=0.0,
        )
        fr._trigger_callbacks(event)
        assert len(results) == 2
        assert 1 in results
        assert 2 in results

    def test_trigger_callback_exception_handling(self):
        fr = FuReturn()

        def failing_callback(event):
            raise ValueError("Test exception")

        def good_callback(event):
            pass

        fr.add_recovery_callback(failing_callback)
        fr.add_recovery_callback(good_callback)

        event = CrashingEvent(
            event_id="test",
            timestamp=0.0,
            state=RecoveryState.NORMAL,
            lyapunov_exponent=0.0,
            residual=0.0,
        )
        fr._trigger_callbacks(event)


class TestReset:
    """重置功能测试"""

    def test_reset_clears_events(self):
        fr = FuReturn()
        fr._record_event(RecoveryState.NORMAL, 0.0, 0.1)
        fr._record_event(RecoveryState.WARNING, 0.6, 0.5)
        fr.reset()
        assert len(fr.event_history) == 0

    def test_reset_restores_normal_state(self):
        fr = FuReturn()
        fr._record_event(RecoveryState.CRASHING, 0.9, 0.9)
        fr.reset()
        assert fr.current_state == RecoveryState.NORMAL


class TestRecoveryResult:
    """恢复结果数据结构测试"""

    def test_result_metadata(self):
        fr = FuReturn(Bc=0.8, eps=0.01, max_retries=3)
        current = np.array([0.5, 0.0])
        stable = np.array([0.0, 0.0])
        result = fr.recover(current, stable)
        assert 'attempts' in result.metadata
        assert 'Bc' in result.metadata
        assert 'eps' in result.metadata


class TestCrashingEvent:
    """崩溃事件测试"""

    def test_event_creation(self):
        event = CrashingEvent(
            event_id="test_001",
            timestamp=1234567890.0,
            state=RecoveryState.CRASHING,
            lyapunov_exponent=0.95,
            residual=0.9,
            metadata={"test": "value"},
        )
        assert event.event_id == "test_001"
        assert event.state == RecoveryState.CRASHING
        assert event.metadata["test"] == "value"

    def test_event_default_metadata(self):
        event = CrashingEvent(
            event_id="test_002",
            timestamp=0.0,
            state=RecoveryState.NORMAL,
            lyapunov_exponent=0.0,
            residual=0.0,
        )
        assert event.metadata == {}
