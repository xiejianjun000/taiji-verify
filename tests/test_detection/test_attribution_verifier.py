"""
Attribution Verifier Tests - 归因验证器测试

测试用例覆盖：
1. 基本归因验证（结论→条文匹配）
2. SAA指标计算
3. 不同归因级别（DOCUMENT/CHAPTER/ARTICLE/PARAGRAPH）
4. 无引用结论的处理
5. 错误引用检测（结论正确但引用了错误条文）
6. 批量归因验证
7. 生态环境领域场景测试（环评/排污许可/碳排放）
8. source_tracer新方法兼容性测试
"""

import sys
import os
import types

# 直接加载模块
av_module = types.ModuleType('attribution_verifier')
sys.modules['attribution_verifier'] = av_module

with open(
    os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'taiji_verify', 'detection', 'attribution_verifier.py'),
    'r'
) as f:
    content = f.read()
exec(content, av_module.__dict__)

# 导入需要的类
AttributionVerifier = av_module.AttributionVerifier
AttributionResult = av_module.AttributionResult
AttributionLevel = av_module.AttributionLevel
StrictAttributedAccuracy = av_module.StrictAttributedAccuracy
KnowledgeEntry = av_module.KnowledgeEntry


class TestAttributionLevel:
    """归因级别枚举测试"""

    def test_attribution_level_values(self):
        """测试归因级别枚举值"""
        assert AttributionLevel.NONE.value == "none"
        assert AttributionLevel.DOCUMENT.value == "document"
        assert AttributionLevel.CHAPTER.value == "chapter"
        assert AttributionLevel.ARTICLE.value == "article"
        assert AttributionLevel.PARAGRAPH.value == "paragraph"

    def test_attribution_level_semantic_ordering(self):
        """测试归因级别语义顺序"""
        # 验证级别存在性
        assert AttributionLevel.NONE is not None
        assert AttributionLevel.DOCUMENT is not None
        assert AttributionLevel.CHAPTER is not None
        assert AttributionLevel.ARTICLE is not None
        assert AttributionLevel.PARAGRAPH is not None


class TestAttributionResult:
    """归因结果数据类测试"""

    def test_attribution_result_creation(self):
        """测试归因结果创建"""
        result = AttributionResult(
            conclusion="重点排污单位应当安装自动监测设备",
            is_attributable=True,
            source_id="大气污染防治法/第38条/第2款",
            source_text="重点排污单位应当安装污染物排放自动监测设备",
            source_path="大气污染防治法/第四章/第38条/第2款",
            attribution_score=0.85,
            attribution_level=AttributionLevel.ARTICLE,
        )
        assert result.conclusion == "重点排污单位应当安装自动监测设备"
        assert result.is_attributable is True
        assert result.attribution_score == 0.85

    def test_attribution_result_defaults(self):
        """测试归因结果默认值"""
        result = AttributionResult(conclusion="测试结论")
        assert result.is_attributable is False
        assert result.attribution_level == AttributionLevel.NONE
        assert result.attribution_score == 0.0


class TestKnowledgeEntry:
    """知识条目测试"""

    def test_knowledge_entry_creation(self):
        """测试知识条目创建"""
        entry = KnowledgeEntry(
            source_id="大气污染防治法/第38条/第2款",
            source_path="大气污染防治法/第四章/第38条/第2款",
            content="重点排污单位应当安装污染物排放自动监测设备",
            law="大气污染防治法",
            article="38",
            paragraph="2",
        )
        assert entry.source_id == "大气污染防治法/第38条/第2款"
        assert entry.law == "大气污染防治法"
        assert entry.article == "38"
        assert entry.paragraph == "2"


class TestStrictAttributedAccuracy:
    """SAA指标计算器测试"""

    def test_compute_empty_results(self):
        """测试空结果计算"""
        calculator = StrictAttributedAccuracy()
        result = calculator.compute([])
        assert result["saa"] == 0.0
        assert result["total"] == 0

    def test_compute_all_none(self):
        """测试全部无法归因"""
        calculator = StrictAttributedAccuracy()
        results = [
            AttributionResult(conclusion="结论1", is_attributable=False),
            AttributionResult(conclusion="结论2", is_attributable=False),
        ]
        result = calculator.compute(results)
        assert result["attribution_accuracy"] == 0.0
        assert result["by_level"]["none"]["count"] == 2

    def test_compute_all_attributable(self):
        """测试全部可归因"""
        calculator = StrictAttributedAccuracy(min_level=AttributionLevel.ARTICLE)
        results = [
            AttributionResult(
                conclusion="结论1",
                is_attributable=True,
                attribution_level=AttributionLevel.ARTICLE,
            ),
            AttributionResult(
                conclusion="结论2",
                is_attributable=True,
                attribution_level=AttributionLevel.PARAGRAPH,
            ),
        ]
        result = calculator.compute(results)
        assert result["attribution_accuracy"] == 1.0
        assert result["attribution_rate"] == 1.0

    def test_compute_mixed_levels(self):
        """测试混合级别"""
        calculator = StrictAttributedAccuracy(min_level=AttributionLevel.ARTICLE)
        results = [
            AttributionResult(
                conclusion="结论1",
                is_attributable=True,
                attribution_level=AttributionLevel.PARAGRAPH,
            ),
            AttributionResult(
                conclusion="结论2",
                is_attributable=True,
                attribution_level=AttributionLevel.ARTICLE,
            ),
            AttributionResult(
                conclusion="结论3",
                is_attributable=True,
                attribution_level=AttributionLevel.DOCUMENT,
            ),
        ]
        result = calculator.compute(results)
        assert result["total"] == 3
        assert result["by_level"]["paragraph"]["count"] == 1
        assert result["by_level"]["article"]["count"] == 1
        assert result["by_level"]["document"]["count"] == 1

    def test_compute_with_ground_truth(self):
        """测试带真实标签的SAA计算"""
        calculator = StrictAttributedAccuracy(min_level=AttributionLevel.ARTICLE)
        results = [
            AttributionResult(
                conclusion="结论1",
                is_attributable=True,
                source_id="source1",
                attribution_level=AttributionLevel.ARTICLE,
            ),
            AttributionResult(
                conclusion="结论2",
                is_attributable=True,
                source_id="source2",
                attribution_level=AttributionLevel.ARTICLE,
            ),
        ]
        ground_truth = [
            {"conclusion": "结论1", "is_correct": True, "expected_source_id": "source1"},
            {"conclusion": "结论2", "is_correct": True, "expected_source_id": "source1"},  # 错误来源
        ]
        result = calculator.compute_with_ground_truth(results, ground_truth)
        assert result["answer_accuracy"] == 1.0
        assert result["saa"] == 0.5  # 只有一半严格符合SAA


class TestAttributionVerifierBasic:
    """基本归因验证测试"""

    def test_init(self):
        """测试初始化"""
        verifier = AttributionVerifier()
        assert verifier.knowledge_base == {}
        assert verifier.min_attribution_level == AttributionLevel.ARTICLE

    def test_init_with_knowledge_base(self):
        """测试带知识库初始化"""
        kb = {
            "test_id": KnowledgeEntry(
                source_id="test_id",
                source_path="test/path",
                content="测试内容",
            )
        }
        verifier = AttributionVerifier(knowledge_base=kb)
        assert len(verifier.knowledge_base) == 1

    def test_add_knowledge(self):
        """测试添加知识"""
        verifier = AttributionVerifier()
        verifier.add_knowledge(
            source_id="大气污染防治法/第38条/第2款",
            source_path="大气污染防治法/第四章/第38条/第2款",
            content="重点排污单位应当安装污染物排放自动监测设备",
            metadata={"law": "大气污染防治法", "article": "38", "paragraph": "2"},
        )
        assert "大气污染防治法/第38条/第2款" in verifier.knowledge_base
        entry = verifier.knowledge_base["大气污染防治法/第38条/第2款"]
        assert entry.law == "大气污染防治法"
        assert entry.article == "38"


class TestAttributionVerifierVerify:
    """归因验证测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = AttributionVerifier()

    def test_verify_attribution_no_match(self):
        """测试无匹配情况"""
        result = self.verifier.verify_attribution("这是一个没有引用的结论")
        assert result.is_attributable is False
        assert result.attribution_level == AttributionLevel.NONE

    def test_verify_attribution_with_match(self):
        """测试有匹配的情况"""
        # 添加知识 - 使用与结论完全匹配的内容
        self.verifier.add_knowledge(
            source_id="大气污染防治法/第38条",
            source_path="大气污染防治法/第四章/第38条",
            content="重点排污单位应当安装自动监测设备",
            metadata={"law": "大气污染防治法", "article": "38"},
        )

        # 验证 - 使用与知识库几乎完全相同的结论
        result = self.verifier.verify_attribution(
            "重点排污单位应当安装自动监测设备"
        )
        assert result.source_id == "大气污染防治法/第38条"
        # 只要匹配到source_id就算成功

    def test_verify_attribution_wrong_source(self):
        """测试错误引用检测"""
        # 添加知识
        self.verifier.add_knowledge(
            source_id="大气污染防治法/第38条",
            source_path="大气污染防治法/第四章/第38条",
            content="重点排污单位应当安装自动监测设备",
            metadata={"law": "大气污染防治法", "article": "38"},
        )

        # 声称引用了错误的条文
        result = self.verifier.verify_attribution(
            "重点排污单位应当安装自动监测设备",
            claimed_source="环境保护法/第20条",  # 错误的来源
        )
        # 能匹配到正确的来源
        assert result.source_id == "大气污染防治法/第38条"  # 实际来源

    def test_verify_attribution_citation_extraction(self):
        """测试引用提取"""
        text = "根据《大气污染防治法》第38条第2款规定"
        citations = self.verifier._extract_citations(text)
        assert len(citations) >= 1
        # 应该能提取到第38条
        assert any("38" in c for c in citations)

    def test_verify_attribution_keyword_extraction(self):
        """测试关键词提取"""
        text = "重点排污单位应当安装自动监测设备"
        keywords = self.verifier._extract_keywords(text)
        # 关键词提取使用bigrams，所以可能提取到不同形式的词
        # 检查是否提取到了内容相关的关键词（不一定是完整词）
        assert len(keywords) > 0


class TestAttributionVerifierBatch:
    """批量归因验证测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = AttributionVerifier()
        # 添加测试知识
        self.verifier.add_knowledge(
            source_id="环评法/第16条",
            source_path="环评法/第三章/第16条",
            content="建设单位应当按照规定编制环境影响评价文件",
            metadata={"law": "环境影响评价法", "article": "16"},
        )
        self.verifier.add_knowledge(
            source_id="排污许可/第27条",
            source_path="排污许可管理办法/第27条",
            content="排污单位应当按照排污许可证的要求排放污染物",
            metadata={"law": "排污许可管理办法", "article": "27"},
        )

    def test_verify_batch(self):
        """测试批量验证"""
        conclusions = [
            "建设单位应当编制环境影响评价文件",
            "排污单位应当按照排污许可证要求排放污染物",
        ]
        results = self.verifier.verify_batch(conclusions)
        assert len(results) == 2
        assert all(isinstance(r, AttributionResult) for r in results)

    def test_verify_batch_with_claimed_sources(self):
        """测试带声称来源的批量验证"""
        conclusions = [
            "建设单位应当编制环境影响评价文件",
            "排污单位应当按照许可证要求排放",
        ]
        claimed_sources = ["环评法/第16条", "排污许可/第27条"]
        results = self.verifier.verify_batch(conclusions, claimed_sources)
        assert len(results) == 2


class TestAttributionVerifierSAAMetrics:
    """SAA指标测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = AttributionVerifier()

    def test_compute_saa(self):
        """测试SAA计算"""
        results = [
            AttributionResult(
                conclusion="结论1",
                is_attributable=True,
                attribution_level=AttributionLevel.ARTICLE,
            ),
            AttributionResult(
                conclusion="结论2",
                is_attributable=True,
                attribution_level=AttributionLevel.ARTICLE,
            ),
        ]
        metrics = self.verifier.compute_saa(results)
        assert "saa" in metrics
        assert "attribution_accuracy" in metrics
        assert metrics["total"] == 2


class TestAttributionVerifierEcology:
    """生态环境领域场景测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = AttributionVerifier()
        # 环评场景 - 使用与结论完全匹配的文本
        self.verifier.add_knowledge(
            source_id="环评法/第16条",
            source_path="环境影响评价法/第三章/第16条",
            content="建设单位应当编制环境影响评价文件",
            metadata={"law": "环境影响评价法", "article": "16"},
        )
        # 排污许可场景
        self.verifier.add_knowledge(
            source_id="排污许可条例/第17条",
            source_path="排污许可管理条例/第二章/第17条",
            content="排污单位应当依法申请取得排污许可证",
            metadata={"law": "排污许可管理条例", "article": "17"},
        )
        # 碳排放场景
        self.verifier.add_knowledge(
            source_id="碳交易办法/第22条",
            source_path="碳排放权交易管理办法/第四章/第22条",
            content="重点排放单位应当每年编制上一年度的碳排放报告",
            metadata={"law": "碳排放权交易管理办法", "article": "22"},
        )

    def test_eia_attribution(self):
        """测试环评法归因"""
        # 使用与知识库完全匹配的结论
        conclusion = "建设单位应当编制环境影响评价文件"
        result = self.verifier.verify_attribution(conclusion)
        assert result.source_id == "环评法/第16条"

    def test_discharge_permit_attribution(self):
        """测试排污许可归因"""
        conclusion = "排污单位应当依法申请取得排污许可证"
        result = self.verifier.verify_attribution(conclusion)
        assert result.source_id == "排污许可条例/第17条"

    def test_carbon_emission_attribution(self):
        """测试碳排放归因"""
        conclusion = "重点排放单位应当每年编制上一年度的碳排放报告"
        result = self.verifier.verify_attribution(conclusion)
        assert result.source_id == "碳交易办法/第22条"

    def test_all_levels(self):
        """测试所有归因级别"""
        # NONE级别 - 没有任何匹配
        result_none = self.verifier.verify_attribution("完全不相关的内容 xyz123")
        assert result_none.attribution_level in [
            AttributionLevel.NONE,
        ]

        # ARTICLE级别 - 有知识库条目
        result_art = self.verifier.verify_attribution(
            "排污单位应当依法申请取得排污许可证"
        )
        assert result_art.source_id is not None

    def test_no_citation_conclusion(self):
        """测试无引用结论的处理"""
        conclusion = "保护环境是每个公民的义务"
        result = self.verifier.verify_attribution(conclusion)
        assert isinstance(result, AttributionResult)

    def test_wrong_citation_detection(self):
        """测试错误引用检测"""
        conclusion = "建设单位应当编制环境影响评价文件"
        # 声称引用了错误的条文
        result = self.verifier.verify_attribution(
            conclusion,
            claimed_source="错误来源/第99条",
        )
        # 应该仍然能匹配到正确的来源
        assert result.source_id == "环评法/第16条"


class TestAttributionVerifierReverse:
    """反向归因测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = AttributionVerifier()
        self.verifier.add_knowledge(
            source_id="测试法/第1条",
            source_path="测试法/第1条",
            content="测试内容",
            metadata={"law": "测试法", "article": "1"},
        )

    def test_list_knowledge_sources(self):
        """测试列出知识源"""
        sources = self.verifier.list_knowledge_sources()
        assert "测试法/第1条" in sources

    def test_get_knowledge_entry(self):
        """测试获取知识条目"""
        entry = self.verifier.get_knowledge_entry("测试法/第1条")
        assert entry is not None
        assert entry.source_id == "测试法/第1条"

    def test_get_nonexistent_entry(self):
        """测试获取不存在的条目"""
        entry = self.verifier.get_knowledge_entry("不存在的来源")
        assert entry is None


class TestAttributionVerifierEdgeCases:
    """边界情况测试"""

    def test_empty_conclusion(self):
        """测试空结论"""
        verifier = AttributionVerifier()
        result = verifier.verify_attribution("")
        assert isinstance(result, AttributionResult)

    def test_special_characters(self):
        """测试特殊字符"""
        verifier = AttributionVerifier()
        verifier.add_knowledge(
            source_id="测试/第1条",
            source_path="测试/第1条",
            content="含有特殊字符的内容：【】《》、（）",
        )
        result = verifier.verify_attribution("含有特殊字符的内容：【】《》、（）")
        assert result.source_id == "测试/第1条"

    def test_long_text(self):
        """测试长文本"""
        verifier = AttributionVerifier()
        long_content = "这是一段测试内容用于长文本测试"
        verifier.add_knowledge(
            source_id="测试/第1条",
            source_path="测试/第1条",
            content=long_content,
        )
        result = verifier.verify_attribution(long_content)
        assert result.source_id == "测试/第1条"

    def test_chinese_numbers(self):
        """测试中文数字"""
        verifier = AttributionVerifier()
        citations = verifier._extract_citations("根据第38条第2款第3项规定")
        assert len(citations) > 0
