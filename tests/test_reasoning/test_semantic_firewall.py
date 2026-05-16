"""
Semantic Firewall Tests
"""

import pytest
from taiji_verify.reasoning.semantic_firewall import SemanticFirewall, FirewallResult


class TestSemanticFirewall:
    """语义防火墙测试"""

    def test_firewall_pass(self):
        """测试防火墙通过"""
        firewall = SemanticFirewall()
        result = firewall.check("正确的环境保护法分析")
        assert result.decision in ["PASS", "MODIFIED", "BLOCK"]

    def test_firewall_block(self):
        """测试防火墙拦截"""
        firewall = SemanticFirewall()
        result = firewall.check("根据GB123456标准规定")
        assert isinstance(result, FirewallResult)

    def test_firewall_pipeline(self):
        """测试防火墙流水线"""
        firewall = SemanticFirewall()
        result = firewall.check_with_pipeline("测试文本")
        assert result.delta_s is not None
        assert len(result.step_results) > 0

    def test_firewall_result_structure(self):
        """测试防火墙结果结构"""
        firewall = SemanticFirewall()
        result = firewall.check("测试内容")
        assert hasattr(result, 'decision')
        assert hasattr(result, 'delta_s')
        assert hasattr(result, 'step_results')
