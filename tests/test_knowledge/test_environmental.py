"""
生态环境知识库测试
"""

import pytest
from taiji_verify.knowledge.environmental_knowledge import (
    EnvironmentalKnowledgeBase,
    create_default_env_knowledge_base,
)


class TestEnvironmentalKnowledgeBase:
    """环境知识库测试"""

    def setup_method(self):
        self.kb = create_default_env_knowledge_base()

    def test_entry_count(self):
        total = self.kb.entry_count()
        assert total >= 80

    def test_load_all(self):
        kb = EnvironmentalKnowledgeBase()
        kb.load_all()
        assert len(kb._entries["air"]) >= 10
        assert len(kb._entries["water"]) >= 10
        assert len(kb._entries["soil"]) >= 3
        assert len(kb._entries["solid_waste"]) >= 6
        assert len(kb._entries["noise"]) >= 4
        assert len(kb._entries["radiation"]) >= 3
        assert len(kb._entries["ecology"]) >= 6
        assert len(kb._entries["eia"]) >= 6
        assert len(kb._entries["carbon"]) >= 6
        assert len(kb._entries["permit"]) >= 6
        assert len(kb._entries["monitoring"]) >= 6
        assert len(kb._entries["emergency"]) >= 6
        assert len(kb._entries["clean_production"]) >= 6
        assert len(kb._entries["vehicle"]) >= 6
        assert len(kb._entries["wastefree"]) >= 6
        assert len(kb._entries["soil_remediation"]) >= 6

    def test_query_air_pollution(self):
        results = self.kb.query("PM2.5空气质量", subcategory="air")
        assert len(results) > 0
        assert "PM2.5" in results[0].content

    def test_query_water_pollution(self):
        results = self.kb.query("COD水质指标", subcategory="water")
        assert len(results) > 0
        assert "COD" in results[0].content

    def test_query_soil_pollution(self):
        results = self.kb.query("土壤重金属镉", subcategory="soil")
        assert len(results) > 0

    def test_query_solid_waste(self):
        results = self.kb.query("危险废物贮存标准", subcategory="solid_waste")
        assert len(results) > 0

    def test_query_noise(self):
        results = self.kb.query("昼间夜间噪声", subcategory="noise")
        assert len(results) > 0

    def test_query_radiation(self):
        results = self.kb.query("电磁辐射基站", subcategory="radiation")
        assert len(results) > 0

    def test_query_ecology(self):
        results = self.kb.query("生态保护红线", subcategory="ecology")
        assert len(results) > 0

    def test_query_eia(self):
        results = self.kb.query("环境影响评价报告书", subcategory="eia")
        assert len(results) > 0

    def test_query_carbon(self):
        results = self.kb.query("碳排放权交易", subcategory="carbon")
        assert len(results) > 0

    def test_query_all_categories(self):
        results = self.kb.query("环境保护标准")
        assert len(results) > 0

    def test_verify_fact_true(self):
        is_true, content, source = self.kb.verify_fact("PM2.5是指直径小于2.5微米的颗粒物")
        assert is_true is True
        assert content is not None

    def test_verify_fact_with_standard(self):
        is_true, content, source = self.kb.verify_fact("水质标准分为Ⅰ-Ⅴ类")
        assert is_true is True
        assert "GB" in source

    def test_verify_fact_false(self):
        is_true, content, source = self.kb.verify_fact("完全不相关的XYZ123内容")
        assert is_true is False

    def test_verify_carbon_market(self):
        is_true, content, source = self.kb.verify_fact("碳排放权交易市场交易碳配额")
        assert is_true is True

    def test_verify_noise_standard(self):
        is_true, content, source = self.kb.verify_fact("1类区昼间噪声不超过55分贝")
        assert is_true is True

    def test_verify_eia_classification(self):
        is_true, content, source = self.kb.verify_fact("环评分为报告书报告表和登记表")
        assert is_true is True

    def test_get_categories(self):
        categories = self.kb.get_categories()
        assert "air" in categories
        assert "water" in categories
        assert "carbon" in categories

    def test_standard_code_recognition(self):
        results = self.kb.query("GB 3095")
        assert len(results) > 0
        assert results[0].standard_code == "GB 3095"

    def test_pm25_knowledge(self):
        results = self.kb.query("PM2.5")
        pm25_entries = [r for r in results if "PM2.5" in r.content]
        assert len(pm25_entries) > 0

    def test_carbon_neutral(self):
        results = self.kb.query("碳中和")
        assert len(results) > 0

    def test_three_simultaneously(self):
        results = self.kb.query("三同时")
        assert len(results) > 0

    def test_query_permit(self):
        results = self.kb.query("排污许可", subcategory="permit")
        assert len(results) > 0

    def test_query_monitoring(self):
        results = self.kb.query("自动监测", subcategory="monitoring")
        assert len(results) > 0

    def test_query_emergency(self):
        results = self.kb.query("应急预案", subcategory="emergency")
        assert len(results) > 0

    def test_query_clean_production(self):
        results = self.kb.query("清洁生产审核", subcategory="clean_production")
        assert len(results) > 0

    def test_query_vehicle(self):
        results = self.kb.query("国六标准", subcategory="vehicle")
        assert len(results) > 0

    def test_query_wastefree(self):
        results = self.kb.query("无废城市", subcategory="wastefree")
        assert len(results) > 0

    def test_query_soil_remediation(self):
        results = self.kb.query("异位修复", subcategory="soil_remediation")
        assert len(results) > 0

    def test_verify_permit(self):
        is_true, content, source = self.kb.verify_fact("排污许可分为重点管理简化管理和登记管理")
        assert is_true is True

    def test_verify_monitoring(self):
        is_true, content, source = self.kb.verify_fact("环境监测数据应真实准确")
        assert is_true is True

    def test_verify_emergency(self):
        is_true, content, source = self.kb.verify_fact("突发环境事件应急预案")
        assert is_true is True

    def test_verify_vehicle(self):
        is_true, content, source = self.kb.verify_fact("机动车排放标准分为国一到国六")
        assert is_true is True

    def test_verify_wastefree(self):
        is_true, content, source = self.kb.verify_fact("生活垃圾实行分类投放分类收集")
        assert is_true is True

    def test_verify_soil_remediation(self):
        is_true, content, source = self.kb.verify_fact("土壤修复技术包括异位修复和原位修复")
        assert is_true is True

    def test_entry_count_extended(self):
        total = self.kb.entry_count()
        assert total >= 150
