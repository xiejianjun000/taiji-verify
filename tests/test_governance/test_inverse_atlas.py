"""InverseAtlas 逆图测试 - 完整实现"""
import pytest
from taiji_verify.governance.inverse_atlas import (
    InverseAtlas, InverseResult, LogicalGap, GapType, GapSeverity,
)


class TestInverseAtlasInit:
    """逆图初始化测试"""

    def test_default_init(self):
        atlas = InverseAtlas()
        assert atlas is not None

    def test_with_knowledge_base(self):
        kb = {
            "carbon_trading": ["碳排放权", "交易平台", "管理办法"],
            "environmental_law": ["环境保护法", "1989年", "已颁布"],
        }
        atlas = InverseAtlas(knowledge_base=kb)
        assert len(atlas._kb) == 2


class TestValidatePremise:
    """前提验证测试"""

    def test_validate_premise_empty(self):
        atlas = InverseAtlas()
        assert atlas.validate_premise("") is False

    def test_validate_premise_short(self):
        atlas = InverseAtlas()
        assert atlas.validate_premise("短") is False

    def test_validate_premise_valid(self):
        atlas = InverseAtlas()
        assert atlas.validate_premise("这是一个有效的前提") is True

    def test_validate_premise_with_evidence(self):
        atlas = InverseAtlas()
        result = atlas.validate_premise_with_evidence("碳排放权交易管理办法规定")
        assert result['valid'] is True
        assert 'evidence' in result

    def test_validate_premise_multiple(self):
        atlas = InverseAtlas()
        premises = [
            "碳排放权交易管理办法规定",
            "环境保护法已颁布",
        ]
        results = atlas.validate_premises(premises)
        assert len(results) == 2
        assert all(r['valid'] for r in results)


class TestDerivePremises:
    """前提推导测试"""

    def test_derive_premise_valid_conclusion(self):
        atlas = InverseAtlas()
        premises = atlas.derive_premises("碳排放权交易应当遵守管理办法")
        assert len(premises) > 0

    def test_derive_premise_empty(self):
        atlas = InverseAtlas()
        premises = atlas.derive_premises("")
        assert len(premises) == 0

    def test_derive_premise_multiple_patterns(self):
        atlas = InverseAtlas()
        premises = atlas.derive_premises("显然可以得出结论")
        assert len(premises) > 0

    def test_derive_premise_with_context(self):
        atlas = InverseAtlas()
        premises = atlas.derive_premises(
            "分析报告",
            context={"domain": "environmental"},
        )
        assert len(premises) > 0


class TestDetectGaps:
    """逻辑跳跃检测测试"""

    def test_detect_gap_conclusion_only(self):
        atlas = InverseAtlas()
        gaps = atlas.detect_gaps("显然地可以得出结论")
        assert len(gaps) > 0

    def test_detect_gap_empty(self):
        atlas = InverseAtlas()
        gaps = atlas.detect_gaps("", "")
        assert len(gaps) == 0

    def test_detect_gap_severity(self):
        atlas = InverseAtlas()
        gaps = atlas.detect_gaps("显然地，这是一个缺乏证据的陈述")
        assert any(g.severity == GapSeverity.HIGH for g in gaps)

    def test_detect_gap_type(self):
        atlas = InverseAtlas()
        gaps = atlas.detect_gaps("显然地", "结论")
        assert any(g.gap_type == GapType.MISSING_REASONING for g in gaps)

    def test_detect_gap_multiple(self):
        atlas = InverseAtlas()
        gaps = atlas.detect_gaps(
            "显然，显然地，可见，由此可见，从而得出结论",
            "",
        )
        assert len(gaps) >= 2


class TestSuggestFixes:
    """修复建议测试"""

    def test_suggest_fix_for_gap(self):
        atlas = InverseAtlas()
        gap = LogicalGap(
            gap_type=GapType.MISSING_REASONING,
            description="缺少中间推理步骤",
            severity=GapSeverity.HIGH,
        )
        fixes = atlas.suggest_fixes([gap])
        assert len(fixes) > 0
        assert any("补充" in f or "推理" in f for f in fixes)

    def test_suggest_fix_empty_gaps(self):
        atlas = InverseAtlas()
        fixes = atlas.suggest_fixes([])
        assert len(fixes) == 0

    def test_suggest_fix_multiple(self):
        atlas = InverseAtlas()
        gaps = [
            LogicalGap(GapType.MISSING_REASONING, "描述1", GapSeverity.HIGH),
            LogicalGap(GapType.UNSUPPORTED_CLAIM, "描述2", GapSeverity.MEDIUM),
        ]
        fixes = atlas.suggest_fixes(gaps)
        assert len(fixes) >= 2


class TestValidateConclusion:
    """结论验证测试"""

    def test_validate_conclusion_valid(self):
        atlas = InverseAtlas()
        result = atlas.validate_conclusion(
            "碳排放权交易应当遵守管理办法",
            ["碳排放权交易管理办法已发布"],
        )
        assert result.is_valid is True

    def test_validate_conclusion_invalid(self):
        atlas = InverseAtlas()
        result = atlas.validate_conclusion(
            "水不是H2O",
            [],
        )
        assert result.is_valid is False
        assert len(result.missing_premises) > 0

    def test_validate_conclusion_with_gaps(self):
        atlas = InverseAtlas()
        result = atlas.validate_conclusion(
            "显然可以得出结论",
            ["前提条件存在"],
        )
        assert result.is_valid is False
        assert len(result.logical_gaps) > 0


class TestFullValidation:
    """完整验证流程测试"""

    def test_full_validation_valid(self):
        atlas = InverseAtlas()
        result = atlas.validate("有效的问题分析")
        assert isinstance(result, InverseResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'missing_premises')
        assert hasattr(result, 'logical_gaps')
        assert hasattr(result, 'fix_suggestions')
        assert hasattr(result, 'confidence')

    def test_full_validation_invalid(self):
        atlas = InverseAtlas()
        result = atlas.validate(
            "显然地可以得出结论",
            requires_premises=["具体数据支撑"],
        )
        assert isinstance(result, InverseResult)
        assert result.is_valid is False or result.confidence < 1.0

    def test_full_validation_empty(self):
        atlas = InverseAtlas()
        result = atlas.validate("")
        assert result.is_valid is False


class TestLogicalGap:
    """逻辑跳跃数据结构测试"""

    def test_logical_gap_creation(self):
        gap = LogicalGap(
            gap_type=GapType.MISSING_REASONING,
            description="测试描述",
            severity=GapSeverity.HIGH,
        )
        assert gap.gap_type == GapType.MISSING_REASONING
        assert gap.severity == GapSeverity.HIGH

    def test_gap_type_values(self):
        assert GapType.MISSING_REASONING is not None
        assert GapType.UNSUPPORTED_CLAIM is not None
        assert GapType.CIRCULAR_REASONING is not None
        assert GapType.CONTRADICTION is not None

    def test_gap_severity_values(self):
        assert GapSeverity.CRITICAL is not None
        assert GapSeverity.HIGH is not None
        assert GapSeverity.MEDIUM is not None
        assert GapSeverity.LOW is not None


class TestInverseResult:
    """逆图结果测试"""

    def test_inverse_result_creation(self):
        result = InverseResult(
            is_valid=True,
            missing_premises=[],
            logical_gaps=[],
            fix_suggestions=[],
            confidence=0.95,
        )
        assert result.is_valid is True
        assert result.confidence == 0.95

    def test_inverse_result_with_gaps(self):
        gap = LogicalGap(GapType.MISSING_REASONING, "描述", GapSeverity.HIGH)
        result = InverseResult(
            is_valid=False,
            missing_premises=["前提1"],
            logical_gaps=[gap],
            fix_suggestions=["建议1"],
            confidence=0.6,
        )
        assert result.is_valid is False
        assert len(result.missing_premises) == 1
        assert len(result.logical_gaps) == 1
        assert len(result.fix_suggestions) == 1


class TestIntegration:
    """集成测试"""

    def test_detect_and_fix_workflow(self):
        atlas = InverseAtlas()
        gaps = atlas.detect_gaps("显然地", "结论")
        fixes = atlas.suggest_fixes(gaps)
        assert len(gaps) == len(fixes)

    def test_derive_and_validate_workflow(self):
        atlas = InverseAtlas()
        premises = atlas.derive_premises("分析报告")
        for premise in premises:
            assert atlas.validate_premise(premise) is True

    def test_validation_with_world_knowledge(self):
        kb = {
            "water": ["H2O", "水"],
            "carbon": ["碳排放", "交易"],
        }
        atlas = InverseAtlas(knowledge_base=kb)
        result = atlas.validate(
            "水是H2O",
            requires_premises=["水的基本化学性质"],
        )
        assert isinstance(result, InverseResult)
