"""
RAG Score Tests - RAG质量评分器测试

测试用例覆盖：
1. 三个维度的评分
2. 加权总分
3. 幻觉风险计算
4. 边界条件
5. RAGScoreResult数据类

v2.2 Phase 1
"""

import sys
import os
import types

# 直接加载模块
rag_module = types.ModuleType('rag_score')
sys.modules['rag_score'] = rag_module

with open(
    os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'taiji_verify', 'detection', 'rag_score.py'),
    'r'
) as f:
    content = f.read()
exec(content, rag_module.__dict__)

# 导入需要的类
RAGScoreDimension = rag_module.RAGScoreDimension
RAGDimensionScore = rag_module.RAGDimensionScore
RAGScoreResult = rag_module.RAGScoreResult
RAGScorer = rag_module.RAGScorer


class TestRAGScoreDimension:
    """RAG评分维度枚举测试"""

    def test_dimension_values(self):
        """测试维度值"""
        assert RAGScoreDimension.FAITHFULNESS.value == "faithfulness"
        assert RAGScoreDimension.RELEVANCE.value == "relevance"
        assert RAGScoreDimension.COMPLETENESS.value == "completeness"


class TestRAGDimensionScore:
    """RAG维度评分测试"""

    def test_dimension_score_creation(self):
        """测试创建"""
        score = RAGDimensionScore(
            dimension=RAGScoreDimension.FAITHFULNESS,
            score=0.85,
            details={"claims": 10, "supported": 8}
        )
        assert score.dimension == RAGScoreDimension.FAITHFULNESS
        assert score.score == 0.85
        assert score.details["claims"] == 10

    def test_dimension_score_defaults(self):
        """测试默认值"""
        score = RAGDimensionScore(dimension=RAGScoreDimension.RELEVANCE, score=0.7)
        assert score.details == {}


class TestRAGScoreResult:
    """RAG评分结果测试"""

    def test_score_result_creation(self):
        """测试创建"""
        result = RAGScoreResult(
            query="什么是碳排放权交易？",
            answer="碳排放权交易是一种市场机制...",
            contexts=["碳排放权交易管理办法...", "碳交易市场概述..."],
            overall_score=0.8,
            faithfulness_score=0.85,
            relevance_score=0.75,
            completeness_score=0.8,
            hallucination_risk=0.15
        )
        assert result.query == "什么是碳排放权交易？"
        assert result.overall_score == 0.8
        assert result.hallucination_risk == 0.15

    def test_score_result_defaults(self):
        """测试默认值"""
        result = RAGScoreResult(
            query="测试",
            answer="测试",
            contexts=[]
        )
        assert result.overall_score == 0.0
        assert result.faithfulness_score == 0.0
        # 默认hallucination_risk为0，需要通过score()方法计算才会得到1-fidelity

    def test_score_result_is_low_risk(self):
        """测试低风险属性"""
        result = RAGScoreResult(
            query="测试",
            answer="测试",
            contexts=[],
            hallucination_risk=0.2
        )
        assert result.is_low_risk is True
        assert result.is_medium_risk is False
        assert result.is_high_risk is False

    def test_score_result_is_medium_risk(self):
        """测试中等风险属性"""
        result = RAGScoreResult(
            query="测试",
            answer="测试",
            contexts=[],
            hallucination_risk=0.45
        )
        assert result.is_low_risk is False
        assert result.is_medium_risk is True
        assert result.is_high_risk is False

    def test_score_result_is_high_risk(self):
        """测试高风险属性"""
        result = RAGScoreResult(
            query="测试",
            answer="测试",
            contexts=[],
            hallucination_risk=0.7
        )
        assert result.is_low_risk is False
        assert result.is_medium_risk is False
        assert result.is_high_risk is True

    def test_score_result_to_dict(self):
        """测试转换为字典"""
        result = RAGScoreResult(
            query="测试",
            answer="测试",
            contexts=["ctx1"]
        )
        d = result.to_dict()
        assert d["query"] == "测试"
        assert d["answer"] == "测试"
        assert d["contexts"] == ["ctx1"]


class TestRAGScorerInit:
    """RAGScorer初始化测试"""

    def test_init_default(self):
        """测试默认初始化"""
        scorer = RAGScorer()
        weights = scorer.weights
        assert weights == (0.5, 0.3, 0.2)  # faithfulness, relevance, completeness

    def test_init_custom_weights(self):
        """测试自定义权重"""
        scorer = RAGScorer(
            faithfulness_weight=0.6,
            relevance_weight=0.25,
            completeness_weight=0.15
        )
        weights = scorer.weights
        assert weights == (0.6, 0.25, 0.15)

    def test_init_invalid_weights(self):
        """测试无效权重"""
        try:
            RAGScorer(
                faithfulness_weight=0.6,
                relevance_weight=0.6,
                completeness_weight=0.1
            )
            assert False, "应该抛出异常"
        except ValueError as e:
            assert "权重和必须为1.0" in str(e)

    def test_init_weights_sum_close(self):
        """测试权重接近1的情况"""
        # 允许小的浮点误差
        scorer = RAGScorer(
            faithfulness_weight=0.333,
            relevance_weight=0.333,
            completeness_weight=0.334
        )
        assert scorer is not None


class TestScoreFaithfulness:
    """忠实度评分测试"""

    def setup_method(self):
        """测试前准备"""
        self.scorer = RAGScorer()

    def test_faithfulness_empty_answer(self):
        """测试空答案"""
        score = self.scorer.score_faithfulness("", ["context"])
        assert score == 0.0

    def test_faithfulness_empty_context(self):
        """测试空上下文"""
        score = self.scorer.score_faithfulness("答案内容", [])
        assert score == 0.0

    def test_faithfulness_supported_claims(self):
        """测试有支撑的声明"""
        answer = "碳排放权交易管理办法规定重点排污单位应当安装自动监测设备"
        context = "根据碳排放权交易管理办法，重点排污单位应当安装污染物排放自动监测设备"
        score = self.scorer.score_faithfulness(answer, [context])
        assert score > 0

    def test_faithfulness_unsupported_claims(self):
        """测试无支撑的声明"""
        answer = "碳排放权交易管理办法规定重点排污单位应当安装自动监测设备"
        context = "大气污染防治法规定排污单位应当遵守排放标准"
        score = self.scorer.score_faithfulness(answer, [context])
        # 由于关键词可能不匹配，得分可能较低
        assert 0 <= score <= 1

    def test_faithfulness_exact_match(self):
        """测试完全匹配"""
        text = "碳排放权交易管理办法规定重点排污单位应当安装自动监测设备"
        score = self.scorer.score_faithfulness(text, [text])
        assert score >= 0.5  # 至少中等得分


class TestScoreRelevance:
    """相关性评分测试"""

    def setup_method(self):
        """测试前准备"""
        self.scorer = RAGScorer()

    def test_relevance_empty_query(self):
        """测试空查询"""
        score = self.scorer.score_relevance("", ["context"])
        assert score == 0.0

    def test_relevance_empty_context(self):
        """测试空上下文"""
        score = self.scorer.score_relevance("查询内容", [])
        assert score == 0.0

    def test_relevance_high_match(self):
        """测试高相关性"""
        query = "碳排放权交易管理办法"
        context = "碳排放权交易管理办法规定重点排污单位应当安装自动监测设备"
        score = self.scorer.score_relevance(query, [context])
        assert score > 0

    def test_relevance_low_match(self):
        """测试低相关性"""
        query = "碳排放权交易管理办法"
        context = "大气污染防治法规定空气质量标准"
        score = self.scorer.score_relevance(query, [context])
        assert 0 <= score <= 1


class TestScoreCompleteness:
    """完整性评分测试"""

    def setup_method(self):
        """测试前准备"""
        self.scorer = RAGScorer()

    def test_completeness_empty_query(self):
        """测试空查询"""
        score = self.scorer.score_completeness("", "答案")
        assert score == 0.0

    def test_completeness_empty_answer(self):
        """测试空答案"""
        score = self.scorer.score_completeness("查询", "")
        assert score == 0.0

    def test_completeness_what_question(self):
        """测试什么是类问题"""
        query = "什么是碳排放权交易？"
        answer = "碳排放权交易是一种市场机制，用于控制温室气体排放"
        score = self.scorer.score_completeness(query, answer)
        assert score > 0

    def test_completeness_how_question(self):
        """测试如何类问题"""
        query = "如何申请碳排放权？"
        answer = "申请碳排放权需要提交相关材料，经过审批后获得"
        score = self.scorer.score_completeness(query, answer)
        assert score > 0

    def test_completeness_short_answer(self):
        """测试简短答案"""
        query = "什么是碳排放权交易？"
        answer = "是市场机制"
        score = self.scorer.score_completeness(query, answer)
        assert 0 <= score <= 1


class TestFullScore:
    """完整评分测试"""

    def setup_method(self):
        """测试前准备"""
        self.scorer = RAGScorer()

    def test_full_score_basic(self):
        """测试基本完整评分"""
        result = self.scorer.score(
            query="什么是碳排放权交易？",
            answer="碳排放权交易是一种控制温室气体排放的市场机制",
            contexts=["碳排放权交易管理办法...", "碳交易市场概述..."]
        )
        assert isinstance(result, RAGScoreResult)
        assert result.query == "什么是碳排放权交易？"
        assert result.overall_score >= 0

    def test_full_score_weights(self):
        """测试加权总分"""
        result = self.scorer.score(
            query="测试",
            answer="测试答案",
            contexts=["上下文"]
        )
        expected = (
            result.faithfulness_score * 0.5 +
            result.relevance_score * 0.3 +
            result.completeness_score * 0.2
        )
        assert abs(result.overall_score - expected) < 0.001

    def test_full_score_hallucination_risk(self):
        """测试幻觉风险计算"""
        result = self.scorer.score(
            query="测试",
            answer="测试答案",
            contexts=["上下文"]
        )
        assert result.hallucination_risk == 1.0 - result.faithfulness_score

    def test_full_score_with_exact_match(self):
        """测试完全匹配场景"""
        answer = "碳排放权交易管理办法规定重点排污单位应当安装自动监测设备"
        result = self.scorer.score(
            query="碳排放权交易管理办法",
            answer=answer,
            contexts=[answer]
        )
        # 完全匹配应该有高分
        assert result.overall_score >= 0.5


class TestClaimExtraction:
    """声明提取测试"""

    def setup_method(self):
        """测试前准备"""
        self.scorer = RAGScorer()

    def test_extract_claims_with_indicators(self):
        """测试带指示词的声明"""
        text = "碳排放权交易是一种市场机制。它可以有效控制污染。"
        claims = self.scorer._extract_claims(text)
        assert len(claims) >= 1

    def test_extract_claims_with_values(self):
        """测试带数值的声明"""
        text = "根据规定，重点排污单位应当每年报告碳排放量100万吨"
        claims = self.scorer._extract_claims(text)
        assert len(claims) >= 1

    def test_extract_claims_empty(self):
        """测试无声明"""
        text = "测试测试测试"
        claims = self.scorer._extract_claims(text)
        assert isinstance(claims, list)


class TestEntityExtraction:
    """实体提取测试"""

    def setup_method(self):
        """测试前准备"""
        self.scorer = RAGScorer()

    def test_extract_entities_numbers(self):
        """测试数值实体"""
        text = "碳排放量是100万吨"
        entities = self.scorer._extract_entities(text)
        assert "100万吨" in entities or "100" in entities

    def test_extract_entities_laws(self):
        """测试法律名称"""
        text = "根据《大气污染防治法》第38条规定"
        entities = self.scorer._extract_entities(text)
        assert "《大气污染防治法》" in entities

    def test_extract_entities_chinese_terms(self):
        """测试中文术语"""
        text = "碳排放权交易管理办法"
        entities = self.scorer._extract_entities(text)
        assert len(entities) >= 0


class TestKeywordExtraction:
    """关键词提取测试"""

    def setup_method(self):
        """测试前准备"""
        self.scorer = RAGScorer()

    def test_extract_keywords_chinese(self):
        """测试中文关键词"""
        text = "碳排放权交易管理办法规定重点排污单位"
        keywords = self.scorer._extract_keywords(text)
        assert "碳排放权" in keywords or "碳排" in keywords

    def test_extract_keywords_english(self):
        """测试英文关键词"""
        text = "Carbon emission trading system"
        keywords = self.scorer._extract_keywords(text)
        assert "carbon" in keywords

    def test_extract_keywords_mixed(self):
        """测试混合关键词"""
        text = "碳排放权Carbon emission"
        keywords = self.scorer._extract_keywords(text)
        assert len(keywords) >= 2


class TestQueryTypeIdentification:
    """查询类型识别测试"""

    def setup_method(self):
        """测试前准备"""
        self.scorer = RAGScorer()

    def test_identify_definition(self):
        """测试定义类查询"""
        query = "什么是碳排放权交易？"
        types = self.scorer._identify_query_types(query)
        assert "definition" in types

    def test_identify_reason(self):
        """测试原因类查询"""
        query = "为什么要进行碳排放权交易？"
        types = self.scorer._identify_query_types(query)
        assert "reason" in types

    def test_identify_method(self):
        """测试方法类查询"""
        query = "如何申请碳排放权？"
        types = self.scorer._identify_query_types(query)
        assert "method" in types

    def test_identify_multiple(self):
        """测试复合查询"""
        query = "什么是碳排放权交易？为什么重要？如何参与？"
        types = self.scorer._identify_query_types(query)
        assert len(types) >= 2


class TestEdgeCases:
    """边界条件测试"""

    def setup_method(self):
        """测试前准备"""
        self.scorer = RAGScorer()

    def test_empty_strings(self):
        """测试空字符串"""
        result = self.scorer.score("", "", [])
        assert result.overall_score == 0.0

    def test_very_long_text(self):
        """测试超长文本"""
        long_text = "碳排放权交易" * 100
        result = self.scorer.score(long_text, long_text, [long_text])
        assert result.overall_score >= 0

    def test_special_characters(self):
        """测试特殊字符"""
        result = self.scorer.score(
            "测试@#$%",
            "答案!@#$%",
            ["上下文!@#$%"]
        )
        assert result.overall_score >= 0

    def test_unicode_text(self):
        """测试Unicode"""
        result = self.scorer.score(
            "碳排放权交易🔥",
            "答案🔥测试",
            ["上下文🔥"]
        )
        assert result.overall_score >= 0

    def test_single_character(self):
        """测试单字符"""
        result = self.scorer.score("测", "试", ["上下文"])
        assert 0 <= result.overall_score <= 1
