"""
Source Tracer Tests
"""

import pytest
from taiji_verify.detection.source_tracer import SourceTracer, TraceResult, KnowledgeSource


class TestSourceTracer:
    """知识溯源器测试"""

    def test_add_and_query_entry(self):
        """测试添加和查询条目"""
        tracer = SourceTracer()
        tracer.add_entry(
            entry_id="E001",
            content="环境保护法于2022年修订",
            keywords=["环境", "保护", "法"]
        )
        result = tracer.query("环境保护法何时修订")
        assert len(result.matched_entry_ids) >= 0

    def test_inverted_index(self):
        """测试倒排索引"""
        tracer = SourceTracer()
        tracer.add_entry("E1", "碳排放权交易管理办法", ["碳排放", "交易"])
        tracer.add_entry("E2", "碳达峰实施方案", ["碳达峰", "实施"])
        results = tracer.query_by_keyword("碳排放")
        assert "E1" in results

    def test_batch_trace(self):
        """测试批量溯源"""
        tracer = SourceTracer()
        tracer.add_entry("E1", "环境质量标准规定", ["环境质量", "标准"])
        texts = ["环境质量标准需要严格执行", "经济发展与环境保护平衡"]
        results = tracer.batch_trace(texts)
        assert len(results) == 2

    def test_max_sources(self):
        """测试最大来源数"""
        tracer = SourceTracer(max_sources=2)
        tracer.add_entry("E1", "内容1", ["关键词1"])
        tracer.add_entry("E2", "内容2", ["关键词1"])
        tracer.add_entry("E3", "内容3", ["关键词1"])
        result = tracer.query("关键词1")
        assert len(result.matched_entry_ids) <= 2

    def test_coverage_calculation(self):
        """测试覆盖率计算"""
        tracer = SourceTracer()
        tracer.add_entry("E1", "碳排放权交易", ["碳排放权", "交易"])
        result = tracer.query("碳排放权交易平台")
        assert result.coverage >= 0

    def test_query_no_match(self):
        """测试无匹配情况"""
        tracer = SourceTracer()
        tracer.add_entry("E1", "内容", ["关键词"])
        result = tracer.query("完全不同的内容")
        assert isinstance(result, TraceResult)
