"""SymptomMap 病候图测试 - 完整覆盖率"""
import pytest
from taiji_verify.symptom_map import (
    SymptomMap, FailureLevel, FailurePattern, FailureDetection,
    DetectionResult, Detector,
    RAGRetrievalFailureDetector, RAGLowRelevanceDetector,
    RAGOutdatedKnowledgeDetector, RAGNoiseInjectionDetector,
    ReasoningLogicalJumpDetector, ReasoningCircularDetector,
    ReasoningHallucinationDetector, ReasoningMathErrorDetector,
    MemoryConfusionDetector, MemoryContextLossDetector, MemoryContaminationDetector,
    AgentRoleMismatchDetector, AgentGoalDriftDetector, AgentRefusalDetector,
    ToolMisuseDetector, ToolAPIFailureDetector,
    SafetyBreachDetector, KnowledgeConflictDetector,
)


class TestSymptomMap:
    """SymptomMap主类测试"""

    def test_symptom_map_init(self):
        symptom_map = SymptomMap()
        assert symptom_map is not None

    def test_failure_level(self):
        assert FailureLevel.RAG is not None
        assert FailureLevel.REASONING is not None
        assert len(FailureLevel) > 0

    def test_failure_pattern(self):
        assert len(FailurePattern) >= 16

    def test_detect_no_failures(self):
        symptom_map = SymptomMap()
        result = symptom_map.detect("验收完成")
        assert result.passed is True
        assert result.overall_risk_score < 0.5

    def test_detect_with_failures(self):
        symptom_map = SymptomMap()
        context = {"retrieved_docs": []}
        result = symptom_map.detect("分析报告", context=context)
        assert len(result.failures) > 0
        assert result.overall_risk_score >= 0.5
        assert result.passed is False

    def test_detect_by_level(self):
        symptom_map = SymptomMap()
        context = {"retrieved_docs": []}
        failures = symptom_map.detect_by_level(
            "测试文本", FailureLevel.RAG, context=context
        )
        assert all(f.level == FailureLevel.RAG for f in failures)

    def test_get_detectors(self):
        symptom_map = SymptomMap()
        detectors = symptom_map.get_detectors()
        assert len(detectors) >= 16

    def test_add_detector(self):
        symptom_map = SymptomMap()
        original_count = len(symptom_map.get_detectors())

        class CustomDetector(Detector):
            pattern = FailurePattern.RAG_RETRIEVAL_FAILURE

            def detect(self, input_text, context=None):
                return None

        symptom_map.add_detector(CustomDetector())
        assert len(symptom_map.get_detectors()) == original_count + 1

    def test_remove_detector(self):
        symptom_map = SymptomMap()
        original_count = len(symptom_map.get_detectors())
        symptom_map.remove_detector(FailurePattern.RAG_RETRIEVAL_FAILURE)
        assert len(symptom_map.get_detectors()) == original_count - 1

    def test_detection_result_metadata(self):
        symptom_map = SymptomMap()
        result = symptom_map.detect("测试")
        assert 'detector_count' in result.metadata
        assert 'failure_count' in result.metadata


class TestRAGRetrievalFailureDetector:
    """RAG检索失败检测器测试"""

    def test_empty_retrieved_docs(self):
        detector = RAGRetrievalFailureDetector()
        context = {"retrieved_docs": []}
        result = detector.detect("测试文本", context)
        assert result is not None
        assert result.pattern == FailurePattern.RAG_RETRIEVAL_FAILURE
        assert result.level == FailureLevel.RAG
        assert result.confidence == 0.95
        assert "检索文档数量为0" in result.evidence

    def test_no_context(self):
        detector = RAGRetrievalFailureDetector()
        result = detector.detect("测试文本", None)
        assert result is None

    def test_no_retrieved_docs_key(self):
        detector = RAGRetrievalFailureDetector()
        context = {"other_key": "value"}
        result = detector.detect("测试文本", context)
        assert result is None

    def test_with_valid_docs(self):
        detector = RAGRetrievalFailureDetector()
        context = {"retrieved_docs": [{"content": "测试文档"}]}
        result = detector.detect("测试文本", context)
        assert result is None


class TestRAGLowRelevanceDetector:
    """RAG相关性不足检测器测试"""

    def test_low_relevance_score(self):
        detector = RAGLowRelevanceDetector()
        context = {"retrieved_docs": [{"content": "测试", "score": 0.2}]}
        result = detector.detect("测试文本", context)
        assert result is not None
        assert result.pattern == FailurePattern.RAG_LOW_RELEVANCE
        assert "0.2" in str(result.evidence)

    def test_high_relevance_score(self):
        detector = RAGLowRelevanceDetector()
        context = {"retrieved_docs": [{"content": "测试", "score": 0.8}]}
        result = detector.detect("测试文本", context)
        assert result is None

    def test_no_score_key(self):
        detector = RAGLowRelevanceDetector()
        context = {"retrieved_docs": [{"content": "测试"}]}
        result = detector.detect("测试文本", context)
        assert result is None

    def test_threshold_boundary(self):
        detector = RAGLowRelevanceDetector()
        context = {"retrieved_docs": [{"content": "测试", "score": 0.3}]}
        result = detector.detect("测试文本", context)
        assert result is None


class TestRAGOutdatedKnowledgeDetector:
    """RAG过时知识检测器测试"""

    def test_outdated_document(self):
        detector = RAGOutdatedKnowledgeDetector()
        context = {
            "retrieved_docs": [
                {"content": "测试", "timestamp": "2020-01-01T00:00:00"}
            ]
        }
        result = detector.detect("测试文本", context)
        assert result is not None
        assert result.pattern == FailurePattern.RAG_OUTDATED_KNOWLEDGE
        assert result.confidence == 0.8

    def test_recent_document(self):
        detector = RAGOutdatedKnowledgeDetector()
        context = {
            "retrieved_docs": [
                {"content": "测试", "timestamp": "2026-01-01T00:00:00"}
            ]
        }
        result = detector.detect("测试文本", context)
        assert result is None

    def test_no_timestamp(self):
        detector = RAGOutdatedKnowledgeDetector()
        context = {"retrieved_docs": [{"content": "测试"}]}
        result = detector.detect("测试文本", context)
        assert result is None


class TestRAGNoiseInjectionDetector:
    """RAG噪声注入检测器测试"""

    def test_noise_indicator(self):
        detector = RAGNoiseInjectionDetector()
        context = {"retrieved_docs": [{"content": "这是[噪声]内容"}]}
        result = detector.detect("测试文本", context)
        assert result is not None
        assert result.pattern == FailurePattern.RAG_NOISE_INJECTION
        assert result.confidence == 0.9

    def test_advertisement_noise(self):
        detector = RAGNoiseInjectionDetector()
        context = {"retrieved_docs": [{"content": "垃圾信息广告"}]}
        result = detector.detect("测试文本", context)
        assert result is not None

    def test_clean_content(self):
        detector = RAGNoiseInjectionDetector()
        context = {"retrieved_docs": [{"content": "正常内容"}]}
        result = detector.detect("测试文本", context)
        assert result is None


class TestReasoningLogicalJumpDetector:
    """逻辑跳跃检测器测试"""

    def test_multiple_jump_indicators(self):
        detector = ReasoningLogicalJumpDetector()
        text = "显然地，由此可见，从而于是我们可以直接得出结论。"
        result = detector.detect(text)
        assert result is not None
        assert result.pattern == FailurePattern.REASONING_LOGICAL_JUMP
        assert result.confidence == 0.75
        assert result.level == FailureLevel.REASONING

    def test_single_jump_indicator(self):
        detector = ReasoningLogicalJumpDetector()
        text = "显然，这是正确的。"
        result = detector.detect(text)
        assert result is None

    def test_boundary_count(self):
        detector = ReasoningLogicalJumpDetector()
        text = "显然。不言而喻。无需多说。"
        result = detector.detect(text)
        assert result is not None
        assert result.confidence == 0.75

    def test_empty_text(self):
        detector = ReasoningLogicalJumpDetector()
        result = detector.detect("")
        assert result is None


class TestReasoningCircularDetector:
    """循环推理检测器测试"""

    def test_circular_reasoning_detected(self):
        detector = ReasoningCircularDetector()
        text = "A是正确的因为B支持A。B是正确的因为A支持B。"
        result = detector.detect(text)
        assert result is not None
        assert result.pattern == FailurePattern.REASONING_CIRCULAR
        assert result.confidence == 0.85

    def test_no_circular(self):
        detector = ReasoningCircularDetector()
        text = "项目通过验收"
        result = detector.detect(text)
        assert result is None

    def test_normal_text_no_false_positive(self):
        detector = ReasoningCircularDetector()
        text = "碳排放权交易管理办法规定碳排放权交易应当遵守本办法。本项目按照碳排放权交易管理办法执行。"
        result = detector.detect(text)
        assert result is None

    def test_exact_duplicate_detected(self):
        detector = ReasoningCircularDetector()
        text = "这是正确的。这是正确的。"
        result = detector.detect(text)
        assert result is not None
        assert result.pattern == FailurePattern.REASONING_CIRCULAR


class TestReasoningHallucinationDetector:
    """幻觉生成检测器测试"""

    def test_unsupported_claims(self):
        detector = ReasoningHallucinationDetector()
        text = "根据内部知识，数据显示研究表明专家认为"
        result = detector.detect(text)
        assert result is not None
        assert result.pattern == FailurePattern.REASONING_HALLUCINATION
        assert result.level == FailureLevel.REASONING

    def test_single_pattern(self):
        detector = ReasoningHallucinationDetector()
        text = "根据内部知识"
        result = detector.detect(text)
        assert result is not None
        assert len(result.evidence) == 1

    def test_no_hallucination(self):
        detector = ReasoningHallucinationDetector()
        text = "这是一个正常的分析报告。"
        result = detector.detect(text)
        assert result is None


class TestReasoningMathErrorDetector:
    """数学错误检测器测试"""

    def test_addition_error(self):
        detector = ReasoningMathErrorDetector()
        text = "计算结果: 5 + 3 = 9"
        result = detector.detect(text)
        assert result is not None
        assert result.pattern == FailurePattern.REASONING_MATH_ERROR
        assert result.confidence == 0.95

    def test_subtraction_error(self):
        detector = ReasoningMathErrorDetector()
        text = "结果: 10 - 4 = 3"
        result = detector.detect(text)
        assert result is not None

    def test_multiplication_error(self):
        detector = ReasoningMathErrorDetector()
        text = "计算: 4 * 5 = 18"
        result = detector.detect(text)
        assert result is not None

    def test_correct_calculation(self):
        detector = ReasoningMathErrorDetector()
        text = "计算: 5 + 3 = 8"
        result = detector.detect(text)
        assert result is None

    def test_division_error(self):
        detector = ReasoningMathErrorDetector()
        text = "结果: 10 / 2 = 4"
        result = detector.detect(text)
        assert result is not None

    def test_no_math_expression(self):
        detector = ReasoningMathErrorDetector()
        text = "这是一个没有数学表达式的文本"
        result = detector.detect(text)
        assert result is None


class TestMemoryConfusionDetector:
    """记忆混淆检测器测试"""

    def test_history_reference_without_history(self):
        detector = MemoryConfusionDetector()
        text = "之前提到的内容是正确的。"
        context = {"history": []}
        result = detector.detect(text, context)
        assert result is not None
        assert result.pattern == FailurePattern.MEMORY_CONFUSION
        assert result.confidence == 0.85

    def test_history_reference_with_history(self):
        detector = MemoryConfusionDetector()
        text = "之前提到的内容是正确的。"
        context = {"history": ["一些历史数据"]}
        result = detector.detect(text, context)
        assert result is None

    def test_no_reference_pattern(self):
        detector = MemoryConfusionDetector()
        text = "这是一个正常的文本。"
        context = {"history": []}
        result = detector.detect(text, context)
        assert result is None


class TestMemoryContextLossDetector:
    """上下文丢失检测器测试"""

    def test_missing_expected_context(self):
        detector = MemoryContextLossDetector()
        text = "这是回答。"
        context = {"expected_context": "关键信息"}
        result = detector.detect(text, context)
        assert result is not None
        assert result.pattern == FailurePattern.MEMORY_CONTEXT_LOSS
        assert result.confidence == 0.8

    def test_contains_expected_context(self):
        detector = MemoryContextLossDetector()
        text = "关键信息在回答中。"
        context = {"expected_context": "关键信息"}
        result = detector.detect(text, context)
        assert result is None

    def test_no_expected_context(self):
        detector = MemoryContextLossDetector()
        text = "测试文本"
        context = {}
        result = detector.detect(text, context)
        assert result is None


class TestMemoryContaminationDetector:
    """记忆污染检测器测试"""

    def test_contamination_detected(self):
        detector = MemoryContaminationDetector()
        text = "用户A的信息出现在这里。"
        context = {"session_id": "abc123"}
        result = detector.detect(text, context)
        assert result is not None
        assert result.pattern == FailurePattern.MEMORY_CONTAMINATION

    def test_no_contamination(self):
        detector = MemoryContaminationDetector()
        text = "正常的回答内容。"
        context = {"session_id": "abc123"}
        result = detector.detect(text, context)
        assert result is None


class TestAgentRoleMismatchDetector:
    """角色错位检测器测试"""

    def test_role_mismatch(self):
        detector = AgentRoleMismatchDetector()
        text = "这个任务很简单。"
        context = {"expected_role": "客服"}
        result = detector.detect(text, context)
        assert result is not None
        assert result.pattern == FailurePattern.AGENT_ROLE_MISMATCH
        assert result.confidence == 0.7

    def test_role_match(self):
        detector = AgentRoleMismatchDetector()
        text = "您好，请问有什么可以帮您？"
        context = {"expected_role": "客服"}
        result = detector.detect(text, context)
        assert result is None

    def test_expert_role(self):
        detector = AgentRoleMismatchDetector()
        text = "根据研究表明"
        context = {"expected_role": "专家"}
        result = detector.detect(text, context)
        assert result is None


class TestAgentGoalDriftDetector:
    """目标漂移检测器测试"""

    def test_goal_drift(self):
        detector = AgentGoalDriftDetector()
        text = "完全不相关的内容"
        context = {"goal": "分析环境影响报告"}
        result = detector.detect(text, context)
        assert result is not None
        assert result.pattern == FailurePattern.AGENT_GOAL_DRIFT
        assert result.confidence == 0.8

    def test_goal_aligned(self):
        detector = AgentGoalDriftDetector()
        text = "环评分析工作已完成"
        context = {"goal": "环评分析"}
        result = detector.detect(text, context)
        assert result is None

    def test_no_goal(self):
        detector = AgentGoalDriftDetector()
        text = "测试文本"
        context = {}
        result = detector.detect(text, context)
        assert result is None


class TestAgentRefusalDetector:
    """拒绝执行检测器测试"""

    def test_multiple_refusals(self):
        detector = AgentRefusalDetector()
        text = "我无法完成这个任务，我不能这样做。"
        result = detector.detect(text)
        assert result is not None
        assert result.pattern == FailurePattern.AGENT_REFUSAL
        assert result.confidence == 0.9

    def test_single_refusal(self):
        detector = AgentRefusalDetector()
        text = "完成。"
        result = detector.detect(text)
        assert result is None

    def test_no_refusal(self):
        detector = AgentRefusalDetector()
        text = "我可以帮您完成这个任务。"
        result = detector.detect(text)
        assert result is None


class TestToolMisuseDetector:
    """工具误用检测器测试"""

    def test_tool_call_error(self):
        detector = ToolMisuseDetector()
        context = {
            "tool_calls": [{"tool_name": "search", "error": "API超时"}]
        }
        result = detector.detect("测试", context)
        assert result is not None
        assert result.pattern == FailurePattern.TOOL_MISUSE
        assert result.confidence == 0.95

    def test_successful_tool_call(self):
        detector = ToolMisuseDetector()
        context = {
            "tool_calls": [{"tool_name": "search", "result": "成功"}]
        }
        result = detector.detect("测试", context)
        assert result is None

    def test_no_tool_calls(self):
        detector = ToolMisuseDetector()
        context = {}
        result = detector.detect("测试", context)
        assert result is None


class TestToolAPIFailureDetector:
    """API调用失败检测器测试"""

    def test_api_error_pattern(self):
        detector = ToolAPIFailureDetector()
        text = "API错误：服务不可用"
        result = detector.detect(text)
        assert result is not None
        assert result.pattern == FailurePattern.TOOL_API_FAILURE
        assert result.confidence == 0.95

    def test_http_error(self):
        detector = ToolAPIFailureDetector()
        text = "请求失败，500错误"
        result = detector.detect(text)
        assert result is not None

    def test_no_api_error(self):
        detector = ToolAPIFailureDetector()
        text = "API调用成功完成"
        result = detector.detect(text)
        assert result is None


class TestSafetyBreachDetector:
    """安全边界突破检测器测试"""

    def test_multiple_safety_violations(self):
        detector = SafetyBreachDetector()
        text = "这是密码账户信息，包含敏感隐私内容"
        result = detector.detect(text)
        assert result is not None
        assert result.pattern == FailurePattern.SAFETY_BREACH
        assert result.confidence == 0.85

    def test_single_safety_violation(self):
        detector = SafetyBreachDetector()
        text = "这是一个密码"
        result = detector.detect(text)
        assert result is None

    def test_no_safety_issue(self):
        detector = SafetyBreachDetector()
        text = "这是一个正常的环境分析报告"
        result = detector.detect(text)
        assert result is None


class TestKnowledgeConflictDetector:
    """知识冲突检测器测试"""

    def test_knowledge_conflict(self):
        detector = KnowledgeConflictDetector()
        text = "该项目不是环境保护法范围"
        context = {"knowledge_base": ["环境保护法"]}
        result = detector.detect(text, context)
        assert result is not None
        assert result.pattern == FailurePattern.KNOWLEDGE_CONFLICT
        assert result.confidence == 0.8

    def test_no_conflict(self):
        detector = KnowledgeConflictDetector()
        text = "环境保护法是法律"
        context = {"knowledge_base": ["环境保护法是法律"]}
        result = detector.detect(text, context)
        assert result is None

    def test_no_knowledge_base(self):
        detector = KnowledgeConflictDetector()
        text = "测试文本"
        context = {}
        result = detector.detect(text, context)
        assert result is None


class TestIntegration:
    """集成测试"""

    def test_full_symptom_detection(self):
        symptom_map = SymptomMap()
        context = {
            "retrieved_docs": [],
            "expected_role": "客服",
            "goal": "环评分析",
            "history": [],
            "session_id": "test123",
        }
        text = "显然我们可以直接得出结论，这显然是环保的。"
        result = symptom_map.detect(text, context)
        assert len(result.failures) >= 2
        assert result.overall_risk_score > 0.5
        assert result.passed is False

    def test_detector_pattern_property(self):
        detector = RAGRetrievalFailureDetector()
        assert detector.pattern == FailurePattern.RAG_RETRIEVAL_FAILURE

    def test_failure_detection_dataclass(self):
        detection = FailureDetection(
            pattern=FailurePattern.RAG_RETRIEVAL_FAILURE,
            level=FailureLevel.RAG,
            confidence=0.9,
            description="测试描述",
            suggested_fix="测试修复",
            evidence=["证据1", "证据2"],
            metadata={"key": "value"},
        )
        assert detection.pattern == FailurePattern.RAG_RETRIEVAL_FAILURE
        assert detection.confidence == 0.9
        assert len(detection.evidence) == 2
