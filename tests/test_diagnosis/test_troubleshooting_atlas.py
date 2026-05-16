"""
Troubleshooting Atlas Tests
"""

import pytest
from taiji_verify.diagnosis.troubleshooting_atlas import (
    TroubleshootingAtlas, DiagnosisNode, DiagnosisResult
)


class TestTroubleshootingAtlas:
    """故障排除地图测试"""

    def test_diagnosis_tree_creation(self):
        """测试诊断树创建"""
        atlas = TroubleshootingAtlas()
        tree = atlas.get_diagnosis_tree()
        assert tree is not None
        assert len(tree.children) > 0

    def test_diagnose(self):
        """测试诊断"""
        atlas = TroubleshootingAtlas()
        result = atlas.diagnose(
            symptom="检索结果不准确",
            context={"failure_mode": "FM01"}
        )
        assert isinstance(result, DiagnosisResult)

    def test_rank_fixes(self):
        """测试修复排序"""
        atlas = TroubleshootingAtlas()
        fixes = atlas.rank_fixes(
            failure_mode="FM01",
            priority_hint="high"
        )
        assert isinstance(fixes, list)
