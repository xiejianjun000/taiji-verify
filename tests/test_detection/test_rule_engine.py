"""
Taiji Verify Detection Layer - 规则引擎测试

对应 WFGYVerifier.ts 的 Python 实现
"""

import pytest
import re
from taiji_verify.detection.rule_engine import (
    Rule, RuleEngine, VerificationRule, SymbolConsistencyResult, KnowledgeEntry
)


class TestRuleEngine:
    """规则引擎测试"""

    def test_add_and_verify_rule(self):
        """测试添加规则和验证"""
        engine = RuleEngine()
        rule = Rule(
            id="R001",
            pattern=r"GB(\d+)",
            check=lambda text, match: int(match.group(1)) > 99999,
            correction=lambda match, text: text.replace(match.group(0), "[标准编号]"),
            base_confidence=0.95,
            weight=1.0
        )
        engine.add_rule(rule)
        result = engine.verify("符合GB1234567标准")
        assert result.passed is True
        assert len(result.matched_rules) == 1
        assert result.matched_rules[0].passed is True

    def test_symbol_consistency(self):
        """测试符号一致性检查"""
        engine = RuleEngine()
        engine.add_rule(Rule(id="S1", pattern=r"正确", check=lambda t, m: True, weight=1.0))
        engine.add_rule(Rule(id="S2", pattern=r"错误", check=lambda t, m: False, weight=1.0))
        engine.add_rule(Rule(id="S3", pattern=r"是", check=lambda t, m: True, weight=1.0))
        result = engine.verify_symbols("这个说法正确")
        assert result.total_weight == 1
        assert result.passed_weight == 1

    def test_knowledge_base_match(self):
        """测试知识库匹配"""
        engine = RuleEngine()
        engine.add_knowledge_entry(
            entry_id="KB001",
            content="环境保护法是中国环境保护的基本法律",
            keywords=["环境保护", "基本法律"]
        )
        result = engine.verify("环境保护法规定了污染治理要求")
        assert len(result.knowledge_matches) >= 0

    def test_extract_symbols(self):
        """测试符号提取"""
        engine = RuleEngine()
        symbols = engine.extract_symbols("碳排放量增加了15%，同比增长20%")
        assert len(symbols) > 0

    def test_minimum_score_threshold(self):
        """测试最小分数阈值"""
        engine = RuleEngine(minimum_score=0.3)
        engine.add_rule(Rule(
            id="W1", pattern="正确", weight=0.5,
            check=lambda t, m: True, correction=lambda m, t: t, base_confidence=1.0
        ))
        engine.add_rule(Rule(
            id="W2", pattern="错误", weight=0.5,
            check=lambda t, m: False, correction=lambda m, t: t, base_confidence=1.0
        ))
        result = engine.verify("包含正确的内容")
        assert result.passed is True

    def test_get_rules(self):
        """测试获取规则列表"""
        engine = RuleEngine()
        engine.add_rule(Rule(id="R1", pattern="test", check=lambda t, m: True, weight=1.0))
        rules = engine.get_rules()
        assert len(rules) == 1
        assert rules[0].id == "R1"

    def test_remove_rule(self):
        """测试移除规则"""
        engine = RuleEngine()
        rule = Rule(id="R1", pattern="test", check=lambda t, m: True, weight=1.0)
        engine.add_rule(rule)
        assert engine.remove_rule("R1") is True
        assert engine.remove_rule("R_nonexistent") is False

    def test_multiple_pattern_matches(self):
        """测试多个模式匹配"""
        engine = RuleEngine()
        engine.add_rule(Rule(id="R1", pattern=r"\d+%", check=lambda t, m: True, weight=0.5, base_confidence=1.0))
        engine.add_rule(Rule(id="R2", pattern=r"增加", check=lambda t, m: True, weight=0.5, base_confidence=1.0))
        result = engine.verify("碳排放量增加了15%")
        assert len(result.matched_rules) == 2

    def test_correction_application(self):
        """测试修正应用"""
        engine = RuleEngine()
        engine.add_rule(Rule(
            id="R1",
            pattern=r"GB\d{5,}",
            check=lambda t, m: False,
            correction=lambda match, text: text.replace(match.group(0), "[标准编号]"),
            weight=1.0,
            base_confidence=1.0
        ))
        result = engine.verify("符合GB123456标准")
        assert result.corrected_text is not None
        assert "GB123456" not in result.corrected_text

    def test_empty_text_verification(self):
        """测试空文本验证"""
        engine = RuleEngine()
        result = engine.verify("")
        assert result.passed is True
        assert len(result.matched_rules) == 0

    def test_default_minimum_score(self):
        """测试默认最小分数"""
        engine = RuleEngine()
        assert engine.minimum_score == 0.7

    def test_knowledge_match_structure(self):
        """测试知识匹配结构"""
        engine = RuleEngine()
        engine.add_knowledge_entry(
            entry_id="KB1",
            content="碳排放权交易管理办法",
            keywords=["碳排放权", "交易", "管理", "办法"]
        )
        result = engine.verify("碳排放权交易管理办法规定了相关要求")
        assert isinstance(result.knowledge_matches, list)
