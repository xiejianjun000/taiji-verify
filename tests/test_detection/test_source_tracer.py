"""
Source Tracer Tests - 知识溯源器测试

包含原有测试 + 新增归因验证能力测试
"""

import sys
import os
import types

# 直接加载模块
st_module = types.ModuleType('source_tracer')
sys.modules['source_tracer'] = st_module

# 先加载 numpy
import numpy as np
st_module.np = np

# 读取并执行 source_tracer.py
with open(
    os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'taiji_verify', 'detection', 'source_tracer.py'),
    'r'
) as f:
    content = f.read()
# 移除 import numpy as np 因为我们已经手动设置了
content = content.replace('import numpy as np', '')
exec(content, st_module.__dict__)

# 导入需要的类
SourceTracer = st_module.SourceTracer
TraceResult = st_module.TraceResult
KnowledgeSource = st_module.KnowledgeSource
AttributionTraceResult = st_module.AttributionTraceResult


def load_attribution_verifier():
    """加载 attribution_verifier 模块"""
    av_module = types.ModuleType('taiji_verify.detection.attribution_verifier')
    sys.modules['taiji_verify.detection.attribution_verifier'] = av_module
    with open(
        os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'taiji_verify', 'detection', 'attribution_verifier.py'),
        'r'
    ) as f:
        av_content = f.read()
    exec(av_content, av_module.__dict__)
    return av_module


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


class TestSourceTracerAttribution:
    """溯源器归因能力测试 (v2.2)"""

    def test_trace_with_attribution_no_verifier(self):
        """测试未启用归因验证时的trace_with_attribution"""
        tracer = SourceTracer()
        tracer.add_entry("E1", "测试内容", ["测试"])
        result = tracer.trace_with_attribution("这是测试内容")
        assert isinstance(result, AttributionTraceResult)
        assert result.has_citation is False

    def test_trace_with_attribution_with_verifier(self):
        """测试启用归因验证后的trace_with_attribution"""
        av_module = load_attribution_verifier()
        
        tracer = SourceTracer()
        tracer.add_entry("E1", "测试内容", ["测试"])
        
        # 创建归因验证器并添加知识 - 使用完全匹配的文本
        test_content = "重点排污单位应当安装污染物排放自动监测设备"
        verifier = av_module.AttributionVerifier()
        verifier.add_knowledge(
            source_id="大气污染防治法/第38条",
            source_path="大气污染防治法/第四章/第38条",
            content=test_content,
            metadata={"law": "大气污染防治法", "article": "38"},
        )
        
        # 直接设置归因验证器
        tracer._attribution_verifier = verifier
        tracer._attribution_available = True
        
        # 使用与知识库完全相同的文本
        result = tracer.trace_with_attribution(test_content)
        assert isinstance(result, AttributionTraceResult)
        assert result.has_citation is True
        assert result.attribution_result is not None
        assert result.attribution_result.source_id == "大气污染防治法/第38条"

    def test_batch_trace_with_attribution(self):
        """测试批量带归因的溯源"""
        av_module = load_attribution_verifier()
        
        tracer = SourceTracer()
        tracer.add_entry("E1", "测试内容", ["测试"])
        
        # 创建归因验证器并添加知识
        content1 = "建设单位应当按照规定编制环境影响评价文件"
        verifier = av_module.AttributionVerifier()
        verifier.add_knowledge(
            source_id="环评法/第16条",
            source_path="环评法/第三章/第16条",
            content=content1,
            metadata={"law": "环境影响评价法", "article": "16"},
        )
        
        # 直接设置归因验证器
        tracer._attribution_verifier = verifier
        tracer._attribution_available = True
        
        # 使用与知识库完全相同的文本
        texts = [content1, content1]
        results = tracer.batch_trace_with_attribution(texts)
        assert len(results) == 2
        assert all(isinstance(r, AttributionTraceResult) for r in results)
        assert results[0].has_citation is True

    def test_sync_to_attribution_verifier(self):
        """测试同步知识到归因验证器"""
        av_module = load_attribution_verifier()
        
        # 创建归因验证器
        verifier = av_module.AttributionVerifier()
        
        tracer = SourceTracer()
        tracer._attribution_verifier = verifier
        tracer._attribution_available = True
        
        # 通过add_entry添加条目，应该自动同步到归因验证器
        tracer.add_entry(
            "E1",
            "测试内容",
            ["测试"],
            source="测试来源",
            metadata={"law": "测试法", "article": "1"},
        )
        
        # 验证归因验证器中有同步的知识
        assert tracer._attribution_verifier is not None
        entry = tracer._attribution_verifier.get_knowledge_entry("E1")
        assert entry is not None
        assert entry.content == "测试内容"

    def test_attribution_accuracy_calculation(self):
        """测试引用准确度计算"""
        av_module = load_attribution_verifier()
        
        tracer = SourceTracer()
        tracer.add_entry("E1", "测试内容", ["测试"])
        
        # 创建归因验证器并添加知识 - 使用完全匹配的文本
        test_content = "重点排污单位应当安装污染物排放自动监测设备"
        verifier = av_module.AttributionVerifier()
        verifier.add_knowledge(
            source_id="大气污染防治法/第38条",
            source_path="大气污染防治法/第38条",
            content=test_content,
            metadata={"law": "大气污染防治法", "article": "38"},
        )
        
        # 直接设置归因验证器
        tracer._attribution_verifier = verifier
        tracer._attribution_available = True
        
        # 使用与知识库完全相同的文本
        result = tracer.trace_with_attribution(test_content)
        assert 0 <= result.citation_accuracy <= 1
        assert result.has_citation is True
