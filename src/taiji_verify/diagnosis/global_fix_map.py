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

    def __init__(self, data_path: Optional[str] = None):
        self.entries: list[FixEntry] = []
        if data_path and os.path.exists(data_path):
            self._load_from_file(data_path)
        else:
            self._init_default_entries()

    def _load_from_file(self, data_path: str) -> None:
        """从文件加载"""
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.entries = [
                FixEntry(**item) for item in data
            ]

    def _init_default_entries(self) -> None:
        """初始化默认条目"""
        self.entries = [
            FixEntry(
                id="F001",
                category="Embeddings",
                failure_mode_id="FM01",
                description="优化embedding维度",
                priority=3,
                steps=["选择合适维度", "重新训练模型"],
                references=["ref1"]
            ),
            FixEntry(
                id="F002",
                category="RAG",
                failure_mode_id="FM02",
                description="增加检索召回率",
                priority=4,
                steps=["扩展检索范围", "优化查询语句"],
                references=["ref2"]
            ),
            FixEntry(
                id="F003",
                category="Reasoning&Memory",
                failure_mode_id="FM10",
                description="打断循环推理链",
                priority=3,
                steps=["检测循环模式", "注入外部事实"],
                references=["ref3"]
            ),
            FixEntry(
                id="F004",
                category="Language",
                failure_mode_id="FM13",
                description="统一输出语言",
                priority=2,
                steps=["检测语言不一致", "强制语言设置"],
                references=["ref4"]
            ),
            FixEntry(
                id="F005",
                category="Multi-Agent",
                failure_mode_id="FM07",
                description="协调多Agent通信",
                priority=4,
                steps=["定义通信协议", "实现状态同步"],
                references=["ref5"]
            ),
            FixEntry(
                id="F006",
                category="Chunking",
                failure_mode_id="FM03",
                description="优化文档分块策略",
                priority=3,
                steps=["分析内容结构", "调整分块大小"],
                references=["ref6"]
            ),
            FixEntry(
                id="F007",
                category="Embeddings",
                failure_mode_id="FM05",
                description="补充知识库条目",
                priority=4,
                steps=["识别知识缺口", "添加相关知识"],
                references=["ref7"]
            ),
            FixEntry(
                id="F008",
                category="RAG",
                failure_mode_id="FM01",
                description="增强检索相关性",
                priority=5,
                steps=["重排序结果", "过滤低相关度"],
                references=["ref8"]
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
