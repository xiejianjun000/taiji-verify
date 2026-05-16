"""
Eco Rules Tests
"""

import pytest
import re
from taiji_verify.detection.eco_rules import (
    FakeStandardRule, TimeTravelRule, SelfContradictionRule,
    WrongLegalStatusRule, FakeHistoryRule, get_all_rules, EcoRule
)


class TestEcoRules:
    """生态规则测试"""

    def test_fake_standard_rule(self):
        """测试假标准编号规则"""
        rule = FakeStandardRule()
        match = re.search(rule.pattern, "GB99999标准")
        assert match is not None
        assert rule.check("GB99999标准", match) is True
        assert rule.base_confidence == 0.95

    def test_time_travel_rule(self):
        """测试时间穿越规则"""
        rule = TimeTravelRule()
        match = re.search(rule.pattern, "该法律于2050年颁布")
        assert match is not None
        assert rule.check("该法律于2050年颁布", match) is True

    def test_self_contradiction_rule(self):
        """测试自相矛盾规则"""
        rule = SelfContradictionRule()
        assert rule.check("该物质有毒但也无害", None) is True
        assert rule.check("该物质有毒", None) is False

    def test_wrong_legal_status_rule(self):
        """测试错误法律状态规则"""
        rule = WrongLegalStatusRule()
        match = re.search(rule.pattern, "环境保护法未颁布")
        assert match is not None
        assert rule.check("环境保护法未颁布", match) is True

    def test_fake_history_rule(self):
        """测试虚假历史规则"""
        rule = FakeHistoryRule()
        match = re.search(rule.pattern, "环境保护法2025年发布")
        assert match is not None
        assert rule.check("环境保护法2025年发布", match) is True

    def test_get_all_rules(self):
        """测试获取所有规则"""
        rules = get_all_rules()
        assert len(rules) == 5
        assert all(isinstance(r, EcoRule) for r in rules)
        assert all(r.base_confidence >= 0.9 for r in rules)

    def test_correction(self):
        """测试修正"""
        rule = FakeStandardRule()
        corrected = rule.correction(None, "GB99999有问题")
        assert isinstance(corrected, str)

    def test_rule_ids(self):
        """测试规则ID"""
        rules = get_all_rules()
        ids = {r.id for r in rules}
        assert "R001" in ids
        assert "R003" in ids
        assert "R004" in ids
        assert "R005" in ids
        assert "R006" in ids
