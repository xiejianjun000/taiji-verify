"""
Troubleshooting Atlas - 故障排除地图

路由优先诊断：diagnose() → get_diagnosis_tree() → rank_fixes()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from taiji_verify.diagnosis.global_fix_map import FixEntry, GlobalFixMap


@dataclass
class DiagnosisNode:
    """诊断节点"""

    symptom: str
    possible_causes: list[str]
    recommended_fixes: list[str]
    children: list[DiagnosisNode] = field(default_factory=list)


@dataclass
class DiagnosisResult:
    """诊断结果"""

    primary_cause: Optional[str]
    all_causes: list[str]
    recommended_fixes: list[FixEntry]
    confidence: float


class TroubleshootingAtlas:
    """
    故障排除地图

    Usage::
        atlas = TroubleshootingAtlas()
        result = atlas.diagnose(symptom="检索结果不准确")
        print(result.primary_cause)
    """

    def __init__(self):
        self.fix_map = GlobalFixMap()
        self._symptom_map = self._init_symptom_map()

    def _init_symptom_map(self) -> dict:
        """初始化症状映射"""
        return {
            "检索": {
                "causes": ["检索失败", "相关性不足", "过时知识"],
                "fixes": ["FM01", "FM02", "FM03"],
            },
            "推理": {
                "causes": ["逻辑跳跃", "循环推理", "幻觉生成"],
                "fixes": ["FM10", "FM11", "FM01"],
            },
            "记忆": {
                "causes": ["记忆混淆", "上下文丢失", "记忆污染"],
                "fixes": ["FM06", "FM07", "FM08"],
            },
            "Agent": {
                "causes": ["角色错位", "目标漂移", "拒绝执行"],
                "fixes": ["FM12", "FM13", "FM14"],
            },
            "工具": {"causes": ["工具误用", "API调用失败"], "fixes": ["FM15", "FM16"]},
            "安全": {"causes": ["安全边界突破"], "fixes": ["FM08"]},
        }

    def get_diagnosis_tree(self) -> DiagnosisNode:
        """获取诊断树"""
        children = []
        for symptom, data in self._symptom_map.items():
            child = DiagnosisNode(
                symptom=symptom,
                possible_causes=data["causes"],
                recommended_fixes=data["fixes"],
            )
            children.append(child)

        return DiagnosisNode(
            symptom="AI输出异常",
            possible_causes=["各层级失败"],
            recommended_fixes=[],
            children=children,
        )

    def diagnose(
        self,
        symptom: str,
        context: Optional[dict] = None,
    ) -> DiagnosisResult:
        """诊断问题"""
        matched_symptom = None
        for key in self._symptom_map.keys():
            if key in symptom:
                matched_symptom = key
                break

        if not matched_symptom:
            return DiagnosisResult(
                primary_cause=None,
                all_causes=[],
                recommended_fixes=[],
                confidence=0.0,
            )

        data = self._symptom_map[matched_symptom]
        fixes = []
        for fm_id in data["fixes"]:
            fixes.extend(self.fix_map.get_by_failure_mode(fm_id))

        return DiagnosisResult(
            primary_cause=data["causes"][0] if data["causes"] else None,
            all_causes=data["causes"],
            recommended_fixes=fixes[:5],
            confidence=0.8,
        )

    def rank_fixes(
        self,
        failure_mode: str,
        priority_hint: str = "medium",
    ) -> list[FixEntry]:
        """排序修复方案"""
        fixes = self.fix_map.get_by_failure_mode(failure_mode)

        priority_map = {"high": 4, "medium": 3, "low": 2}
        min_priority = priority_map.get(priority_hint, 3)

        fixes = [f for f in fixes if f.priority >= min_priority]
        fixes.sort(key=lambda x: x.priority, reverse=True)

        return fixes
