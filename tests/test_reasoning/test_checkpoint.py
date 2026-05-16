"""
Checkpoint Tests
"""

import pytest
from taiji_verify.reasoning.checkpoint import Checkpoint, CheckpointManager


class TestCheckpoint:
    """检查点测试"""

    def test_save_and_restore(self):
        """测试保存和恢复"""
        manager = CheckpointManager()
        cp_id = manager.save("step1", {"data": "value"}, delta_s=0.5)
        checkpoint = manager.restore(cp_id)
        assert checkpoint is not None
        assert checkpoint.data["data"] == "value"
        assert checkpoint.delta_s == 0.5

    def test_gate_check(self):
        """测试门控检查"""
        manager = CheckpointManager()
        assert manager.gate_check("SAFE", "TRANSIT") is True
        assert manager.gate_check("RISK", "DANGER") is True

    def test_checkpoint_list(self):
        """测试检查点列表"""
        manager = CheckpointManager()
        manager.save("cp1", {}, delta_s=0.1)
        manager.save("cp2", {}, delta_s=0.2)
        checkpoints = manager.list_checkpoints()
        assert len(checkpoints) == 2

    def test_clear(self):
        """测试清除"""
        manager = CheckpointManager()
        manager.save("cp1", {}, delta_s=0.1)
        manager.clear()
        assert len(manager.list_checkpoints()) == 0

    def test_get_latest(self):
        """测试获取最新"""
        manager = CheckpointManager()
        manager.save("cp1", {}, delta_s=0.1)
        manager.save("cp2", {}, delta_s=0.2)
        latest = manager.get_latest()
        assert latest.delta_s == 0.2
