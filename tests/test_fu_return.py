"""FuReturn 复归模块测试"""
import pytest

class TestFuReturn:
    def test_initial_state(self):
        from taiji_verify.fu_return import FuReturn, RecoveryState
        fr = FuReturn()
        assert fr.current_state == RecoveryState.NORMAL
    
    def test_reset(self):
        from taiji_verify.fu_return import FuReturn, RecoveryState
        fr = FuReturn()
        fr.reset()
        assert fr.current_state == RecoveryState.NORMAL
    
    def test_recover_method_exists(self):
        from taiji_verify.fu_return import FuReturn
        fr = FuReturn()
        # 检查方法存在
        assert hasattr(fr, 'recover')
        assert hasattr(fr, 'detect_crash')
        assert callable(fr.recover)
