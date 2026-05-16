"""
Global Fix Map Tests
"""

import pytest
from taiji_verify.diagnosis.global_fix_map import FixEntry, GlobalFixMap


class TestGlobalFixMap:
    """全局修复图测试"""

    def test_load_fix_entries(self):
        """测试加载修复条目"""
        fix_map = GlobalFixMap()
        assert len(fix_map.entries) > 0

    def test_get_by_category(self):
        """测试按类别获取"""
        fix_map = GlobalFixMap()
        entries = fix_map.get_by_category("Embeddings")
        assert all(e.category == "Embeddings" for e in entries)

    def test_get_by_failure_mode(self):
        """测试按失败模式获取"""
        fix_map = GlobalFixMap()
        entries = fix_map.get_by_failure_mode("FM01")
        assert all("FM01" in e.failure_mode_id for e in entries)

    def test_search_fixes(self):
        """测试搜索修复"""
        fix_map = GlobalFixMap()
        results = fix_map.search("embedding")
        assert len(results) > 0

    def test_fix_entry_structure(self):
        """测试修复条目结构"""
        entry = FixEntry(
            id="F001",
            category="Embeddings",
            failure_mode_id="FM01",
            description="优化embedding质量",
            priority=3,
            steps=["step1", "step2"],
            references=["ref1"]
        )
        assert entry.priority == 3
        assert len(entry.steps) == 2
