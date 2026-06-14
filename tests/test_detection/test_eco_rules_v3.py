"""
ECO-Audit V3.0 规则引擎验证测试

验证 taiji_verify.detection.eco_rules 中的 73 条规则能正常加载、查询、分类。

共 11+ 个测试用例，全部通过才算成功。
"""

import pytest
from taiji_verify.detection.eco_rules import (
    EcoRule,
    RuleEngine,
    get_all_rules,
    get_rules_by_dimension,
    get_rules_by_mode,
    ALL_DIMENSIONS,
    ALL_MODES,
    DIMENSION_TECHNICAL_COMPLIANCE,
    DIMENSION_DATA_LOGIC,
    DIMENSION_PHYSICAL_LINK,
    DIMENSION_OPS_QC,
    DIMENSION_THIRD_PARTY,
    DIMENSION_INDUSTRY_SPECIFIC,
)


# ============================================================================
# 辅助函数
# ============================================================================

def _engine() -> RuleEngine:
    """创建 RuleEngine 实例（用于测试 get_statistics 等实例方法）。"""
    return RuleEngine()


# ============================================================================
# TC1: get_all_rules() 返回 73 条规则
# ============================================================================

class TestGetAllRules:
    def test_total_rule_count_is_73(self):
        """验证 get_all_rules() 返回 73 条规则。"""
        rules = get_all_rules()
        assert len(rules) == 73, f"预期 73 条规则，实际 {len(rules)} 条"

    def test_all_rules_are_eco_rule_instances(self):
        """验证返回的每条规则都是 EcoRule 实例。"""
        rules = get_all_rules()
        assert all(isinstance(r, EcoRule) for r in rules), "存在非 EcoRule 实例"

    def test_all_rules_enabled(self):
        """验证所有规则均为启用状态。"""
        rules = get_all_rules()
        assert all(r.enabled for r in rules), "存在被禁用的规则"


# ============================================================================
# TC2: get_rules_by_dimension("技术合规与反造假") 返回 25 条
# ============================================================================

class TestDimensionTechnicalCompliance:
    def test_technical_compliance_count_is_25(self):
        rules = get_rules_by_dimension(DIMENSION_TECHNICAL_COMPLIANCE)
        assert len(rules) == 25, (
            f"维度 '{DIMENSION_TECHNICAL_COMPLIANCE}' 预期 25 条，实际 {len(rules)} 条"
        )


# ============================================================================
# TC3: get_rules_by_dimension("数据逻辑与真实性校验") 返回 15 条
# ============================================================================

class TestDimensionDataLogic:
    def test_data_logic_count_is_15(self):
        rules = get_rules_by_dimension(DIMENSION_DATA_LOGIC)
        assert len(rules) == 15, (
            f"维度 '{DIMENSION_DATA_LOGIC}' 预期 15 条，实际 {len(rules)} 条"
        )


# ============================================================================
# TC4: get_rules_by_dimension("物理链路与环境完整性") 返回 10 条
# ============================================================================

class TestDimensionPhysicalLink:
    def test_physical_link_count_is_10(self):
        rules = get_rules_by_dimension(DIMENSION_PHYSICAL_LINK)
        assert len(rules) == 10, (
            f"维度 '{DIMENSION_PHYSICAL_LINK}' 预期 10 条，实际 {len(rules)} 条"
        )


# ============================================================================
# TC5: get_rules_by_dimension("运维与质控规范") 返回 10 条
# ============================================================================

class TestDimensionOpsQc:
    def test_ops_qc_count_is_10(self):
        rules = get_rules_by_dimension(DIMENSION_OPS_QC)
        assert len(rules) == 10, (
            f"维度 '{DIMENSION_OPS_QC}' 预期 10 条，实际 {len(rules)} 条"
        )


# ============================================================================
# TC6: get_rules_by_dimension("第三方检测") 返回 5 条
# ============================================================================

class TestDimensionThirdParty:
    def test_third_party_count_is_5(self):
        rules = get_rules_by_dimension(DIMENSION_THIRD_PARTY)
        assert len(rules) == 5, (
            f"维度 '{DIMENSION_THIRD_PARTY}' 预期 5 条，实际 {len(rules)} 条"
        )


# ============================================================================
# TC7: get_rules_by_dimension("特定行业/因子专项规则") 返回 8 条
# ============================================================================

class TestDimensionIndustrySpecific:
    def test_industry_specific_count_is_8(self):
        rules = get_rules_by_dimension(DIMENSION_INDUSTRY_SPECIFIC)
        assert len(rules) == 8, (
            f"维度 '{DIMENSION_INDUSTRY_SPECIFIC}' 预期 8 条，实际 {len(rules)} 条"
        )


# ============================================================================
# TC8: 维度规则总数等于 73
# ============================================================================

class TestDimensionSumEqualsTotal:
    def test_sum_of_all_dimensions_equals_73(self):
        """验证所有维度规则数之和等于总规则数 73。"""
        total = sum(len(get_rules_by_dimension(d)) for d in ALL_DIMENSIONS)
        assert total == 73, f"各维度规则数之和为 {total}，预期 73"


# ============================================================================
# TC9: get_rules_by_mode("快速") 返回 9 条
# ============================================================================

class TestModeFast:
    def test_fast_mode_count_is_9(self):
        rules = get_rules_by_mode("快速")
        assert len(rules) == 9, f"模式 '快速' 预期 9 条，实际 {len(rules)} 条"


# ============================================================================
# TC10: get_statistics() 返回正确的统计信息
# ============================================================================

class TestGetStatistics:
    def test_statistics_total_is_73(self):
        stats = _engine().get_statistics()
        assert stats["total_rules"] == 73, f"total_rules 预期 73，实际 {stats['total_rules']}"

    def test_statistics_enabled_is_73(self):
        stats = _engine().get_statistics()
        assert stats["enabled_rules"] == 73, f"enabled_rules 预期 73，实际 {stats['enabled_rules']}"

    def test_statistics_disabled_is_0(self):
        stats = _engine().get_statistics()
        assert stats["disabled_rules"] == 0, f"disabled_rules 预期 0，实际 {stats['disabled_rules']}"

    def test_statistics_by_dimension_counts(self):
        stats = _engine().get_statistics()
        by_dim = stats["by_dimension"]
        expected = {
            DIMENSION_TECHNICAL_COMPLIANCE: 25,
            DIMENSION_DATA_LOGIC: 15,
            DIMENSION_PHYSICAL_LINK: 10,
            DIMENSION_OPS_QC: 10,
            DIMENSION_THIRD_PARTY: 5,
            DIMENSION_INDUSTRY_SPECIFIC: 8,
        }
        for dim, count in expected.items():
            assert by_dim.get(dim) == count, (
                f"维度 '{dim}' 统计预期 {count}，实际 {by_dim.get(dim)}"
            )

    def test_statistics_has_all_required_keys(self):
        stats = _engine().get_statistics()
        required_keys = [
            "total_rules", "enabled_rules", "disabled_rules",
            "by_dimension", "by_mode", "rule_id_range",
        ]
        for key in required_keys:
            assert key in stats, f"statistics 缺少必填键: '{key}'"


# ============================================================================
# TC11: 每条规则的必填字段都不为空
# ============================================================================

class TestRuleFieldCompleteness:
    REQUIRED_FIELDS = [
        "id", "name", "description",
        "detection_logic", "legal_basis", "applicable_modes",
    ]

    def test_all_rules_have_required_fields(self):
        """验证每条规则的 id、name、description、detection_logic、legal_basis、applicable_modes 都不为空。"""
        rules = get_all_rules()
        missing = []
        for rule in rules:
            for field_name in self.REQUIRED_FIELDS:
                value = getattr(rule, field_name, None)
                if value is None or (isinstance(value, str) and value.strip() == ""):
                    missing.append(f"{rule.id}.{field_name}")
                elif field_name == "applicable_modes" and (not isinstance(value, list) or len(value) == 0):
                    missing.append(f"{rule.id}.{field_name}")

        assert not missing, (
            f"以下规则的必填字段为空: {', '.join(missing)}"
        )

    def test_dimension_field_not_empty(self):
        """验证 dimension 字段不为空。"""
        rules = get_all_rules()
        for rule in rules:
            assert rule.dimension and rule.dimension.strip(), (
                f"规则 {rule.id} 的 dimension 字段为空"
            )
            assert rule.dimension in ALL_DIMENSIONS, (
                f"规则 {rule.id} 的 dimension '{rule.dimension}' 不在已定义的维度列表中"
            )

    def test_applicable_modes_is_valid_list(self):
        """验证 applicable_modes 是包含有效模式名称的非空列表。"""
        rules = get_all_rules()
        for rule in rules:
            assert isinstance(rule.applicable_modes, list), (
                f"规则 {rule.id} 的 applicable_modes 不是列表"
            )
            assert len(rule.applicable_modes) > 0, (
                f"规则 {rule.id} 的 applicable_modes 为空列表"
            )
            for mode in rule.applicable_modes:
                assert mode in ALL_MODES, (
                    f"规则 {rule.id} 的 applicable_modes 包含无效模式: '{mode}'"
                )
