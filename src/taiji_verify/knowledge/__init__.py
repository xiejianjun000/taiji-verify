"""
环境知识库模块
"""

from taiji_verify.knowledge.chinese_knowledge import (
    ChineseKnowledgeBase,
    KnowledgeEntry,
    create_default_knowledge_base,
)
from taiji_verify.knowledge.environmental_knowledge import (
    EnvironmentalKnowledgeBase,
    EnvKnowledgeEntry,
    create_default_env_knowledge_base,
)

__all__ = [
    "ChineseKnowledgeBase",
    "KnowledgeEntry",
    "create_default_knowledge_base",
    "EnvironmentalKnowledgeBase",
    "EnvKnowledgeEntry",
    "create_default_env_knowledge_base",
]
