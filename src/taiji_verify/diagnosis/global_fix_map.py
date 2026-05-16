"""
Global Fix Map - 全局修复图

300+结构化修复方案，7大类别：
- Embeddings(30+)
- Chunking(20+)
- RAG(50+)
- Language(30+)
- Reasoning&Memory(40+)
- Multi-Agent(30+)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import json
import os


@dataclass
class FixEntry:
    """修复条目"""
    id: str
    category: str
    failure_mode_id: str
    description: str
    priority: int
    steps: list[str]
    references: list[str] = field(default_factory=list)


class GlobalFixMap:
    """
    全局修复图

    Usage::
        fix_map = GlobalFixMap()
        entries = fix_map.get_by_category("Embeddings")
        fixes = fix_map.search("embedding")
    """

    DEFAULT_DATA_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "data", "fix_map_entries.json"
    )

    def __init__(self, data_path: Optional[str] = None):
        self.entries: list[FixEntry] = []
        path = data_path or self.DEFAULT_DATA_PATH
        if os.path.exists(path):
            self._load_from_file(path)
        else:
            self._init_minimal_entries()

    def _load_from_file(self, data_path: str) -> None:
        """从文件加载"""
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.entries = [
                FixEntry(**item) for item in data
            ]

    def _init_minimal_entries(self) -> None:
        """初始化最小条目（文件不存在时的fallback）"""
        self.entries = [
            FixEntry(
                id="F001",
                category="Embeddings",
                failure_mode_id="FM01",
                description="增加embedding维度",
                priority=3,
                steps=["评估当前维度", "扩展到768维", "重新训练"],
                references=["ref1"]
            ),
        ]

    def get_by_category(self, category: str) -> list[FixEntry]:
        """按类别获取修复条目"""
        return [e for e in self.entries if e.category == category]

    def get_by_failure_mode(self, failure_mode_id: str) -> list[FixEntry]:
        """按失败模式获取修复条目"""
        return [e for e in self.entries if failure_mode_id in e.failure_mode_id]

    def search(self, query: str) -> list[FixEntry]:
        """搜索修复条目"""
        query_lower = query.lower()
        return [
            e for e in self.entries
            if query_lower in e.description.lower() or query_lower in e.category.lower()
        ]

    def get_fix(self, entry_id: str) -> Optional[FixEntry]:
        """获取指定ID的修复条目"""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    def get_by_priority(self, priority: int) -> list[FixEntry]:
        """按优先级获取"""
        return [e for e in self.entries if e.priority >= priority]

    def get_category_stats(self) -> dict[str, int]:
        """获取各类别统计"""
        stats = {}
        for entry in self.entries:
            stats[entry.category] = stats.get(entry.category, 0) + 1
        return stats

    def get_failure_mode_stats(self) -> dict[str, int]:
        """获取各失败模式统计"""
        stats = {}
        for entry in self.entries:
            stats[entry.failure_mode_id] = stats.get(entry.failure_mode_id, 0) + 1
        return stats
