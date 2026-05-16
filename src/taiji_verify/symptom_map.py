"""
病候图 (Symptom Map) - 16种失败模式检测模块

16种失败模式分类:
- RAG层: 检索失败、相关性不足、过时知识、噪声注入
- Reasoning层: 逻辑跳跃、循环推理、幻觉生成、数学错误
- Memory层: 记忆混淆、上下文丢失、记忆污染
- Agent层: 角色错位、目标漂移、拒绝执行
- Tool层: 工具误用、API调用失败
- Safety层: 安全边界突破
- Knowledge层: 知识冲突

数据来源：基于阶段一基线数据推算与行业同类系统对标
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from abc import ABC, abstractmethod


class FailureLevel(str, Enum):
    """失败层级"""
    RAG = "rag"
    REASONING = "reasoning"
    MEMORY = "memory"
    AGENT = "agent"
    TOOL = "tool"
    SAFETY = "safety"
    KNOWLEDGE = "knowledge"


class FailurePattern(str, Enum):
    """失败模式枚举 - 16种失败模式"""
    # RAG层 (4种)
    RAG_RETRIEVAL_FAILURE = "rag_retrieval_failure"
    RAG_LOW_RELEVANCE = "rag_low_relevance"
    RAG_OUTDATED_KNOWLEDGE = "rag_outdated_knowledge"
    RAG_NOISE_INJECTION = "rag_noise_injection"
    
    # Reasoning层 (4种)
    REASONING_LOGICAL_JUMP = "reasoning_logical_jump"
    REASONING_CIRCULAR = "reasoning_circular"
    REASONING_HALLUCINATION = "reasoning_hallucination"
    REASONING_MATH_ERROR = "reasoning_math_error"
    
    # Memory层 (3种)
    MEMORY_CONFUSION = "memory_confusion"
    MEMORY_CONTEXT_LOSS = "memory_context_loss"
    MEMORY_CONTAMINATION = "memory_contamination"
    
    # Agent层 (3种)
    AGENT_ROLE_MISMATCH = "agent_role_mismatch"
    AGENT_GOAL_DRIFT = "agent_goal_drift"
    AGENT_REFUSAL = "agent_refusal"
    
    # Tool层 (2种)
    TOOL_MISUSE = "tool_misuse"
    TOOL_API_FAILURE = "tool_api_failure"
    
    # Safety层 (1种)
    SAFETY_BREACH = "safety_breach"
    
    # Knowledge层 (1种)
    KNOWLEDGE_CONFLICT = "knowledge_conflict"


@dataclass
class FailureDetection:
    """失败检测结果"""
    pattern: FailurePattern
    level: FailureLevel
    confidence: float
    description: str
    suggested_fix: str
    evidence: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class DetectionResult:
    """检测结果汇总"""
    failures: List[FailureDetection]
    overall_risk_score: float
    passed: bool
    metadata: Dict = field(default_factory=dict)


class Detector(ABC):
    """检测器基类"""
    
    @abstractmethod
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        """检测失败模式"""
        pass
    
    @property
    @abstractmethod
    def pattern(self) -> FailurePattern:
        """检测器对应的失败模式"""
        pass


class RAGRetrievalFailureDetector(Detector):
    """RAG检索失败检测器"""
    
    pattern = FailurePattern.RAG_RETRIEVAL_FAILURE
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        if context and "retrieved_docs" in context:
            docs = context["retrieved_docs"]
            if len(docs) == 0:
                return FailureDetection(
                    pattern=self.pattern,
                    level=FailureLevel.RAG,
                    confidence=0.95,
                    description="检索结果为空，无法获取相关知识",
                    suggested_fix="检查检索查询词是否合适，考虑扩展查询词或调整检索参数",
                    evidence=["检索文档数量为0"],
                )
        return None


class RAGLowRelevanceDetector(Detector):
    """RAG相关性不足检测器"""
    
    pattern = FailurePattern.RAG_LOW_RELEVANCE
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        if context and "retrieved_docs" in context:
            docs = context["retrieved_docs"]
            for doc in docs:
                if "score" in doc and doc["score"] < 0.3:
                    return FailureDetection(
                        pattern=self.pattern,
                        level=FailureLevel.RAG,
                        confidence=0.85,
                        description="检索到的文档相关性分数过低",
                        suggested_fix="优化检索策略，增加查询扩展，调整相似度阈值",
                        evidence=[f"文档相关性分数: {doc['score']}"],
                    )
        return None


class RAGOutdatedKnowledgeDetector(Detector):
    """RAG过时知识检测器"""
    
    pattern = FailurePattern.RAG_OUTDATED_KNOWLEDGE
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        import datetime
        if context and "retrieved_docs" in context:
            docs = context["retrieved_docs"]
            now = datetime.datetime.now()
            for doc in docs:
                if "timestamp" in doc:
                    doc_date = datetime.datetime.fromisoformat(doc["timestamp"])
                    days_old = (now - doc_date).days
                    if days_old > 365:
                        return FailureDetection(
                            pattern=self.pattern,
                            level=FailureLevel.RAG,
                            confidence=0.8,
                            description=f"检索到的知识已超过{days_old}天，可能已过时",
                            suggested_fix="检查知识库更新频率，考虑添加时效性检查机制",
                            evidence=[f"文档时间戳: {doc['timestamp']}"],
                        )
        return None


class RAGNoiseInjectionDetector(Detector):
    """RAG噪声注入检测器"""
    
    pattern = FailurePattern.RAG_NOISE_INJECTION
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        if context and "retrieved_docs" in context:
            docs = context["retrieved_docs"]
            noise_indicators = ["[噪声]", "[干扰]", "[广告]", "垃圾信息"]
            for doc in docs:
                if "content" in doc:
                    for indicator in noise_indicators:
                        if indicator in doc["content"]:
                            return FailureDetection(
                                pattern=self.pattern,
                                level=FailureLevel.RAG,
                                confidence=0.9,
                                description="检索结果包含噪声内容",
                                suggested_fix="增加文档过滤机制，清理知识库中的噪声数据",
                                evidence=[f"检测到噪声指示符: {indicator}"],
                            )
        return None


class ReasoningLogicalJumpDetector(Detector):
    """逻辑跳跃检测器"""
    
    pattern = FailurePattern.REASONING_LOGICAL_JUMP
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        jump_indicators = [
            "显然", "显然地", "不言而喻", "无需多说",
            "由此可见", "因此", "从而", "于是",
            "直接得出", "可以看出", "不难发现"
        ]
        count = sum(1 for indicator in jump_indicators if indicator in input_text)
        if count >= 3:
            return FailureDetection(
                pattern=self.pattern,
                level=FailureLevel.REASONING,
                confidence=0.75,
                description="推理过程中存在多处逻辑跳跃，可能缺少关键推导步骤",
                suggested_fix="增加推理步骤的详细说明，补充中间逻辑环节",
                evidence=[f"检测到{count}个逻辑跳跃指示词"],
            )
        return None


class ReasoningCircularDetector(Detector):
    """循环推理检测器"""
    
    pattern = FailurePattern.REASONING_CIRCULAR
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        sentences = input_text.split('。')
        for i, sentence in enumerate(sentences):
            for j in range(i + 1, len(sentences)):
                if sentence in sentences[j] or sentences[j] in sentence:
                    return FailureDetection(
                        pattern=self.pattern,
                        level=FailureLevel.REASONING,
                        confidence=0.8,
                        description="检测到循环推理，后续结论重复或包含前面的陈述",
                        suggested_fix="重构推理链，确保每个步骤都提供新信息",
                        evidence=[f"句子{i+1}与句子{j+1}存在重复"],
                    )
        return None


class ReasoningHallucinationDetector(Detector):
    """幻觉生成检测器"""
    
    pattern = FailurePattern.REASONING_HALLUCINATION
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        hallucination_patterns = [
            "根据内部知识", "根据我们的分析", "研究表明",
            "数据显示", "专家认为", "据报道"
        ]
        unsupported_claims = []
        
        for pattern in hallucination_patterns:
            if pattern in input_text:
                unsupported_claims.append(pattern)
        
        if unsupported_claims:
            return FailureDetection(
                pattern=self.pattern,
                level=FailureLevel.REASONING,
                confidence=0.7,
                description=f"检测到{len(unsupported_claims)}处未经证实的断言",
                suggested_fix="为每个断言提供引用来源或证据支持",
                evidence=unsupported_claims,
            )
        return None


class ReasoningMathErrorDetector(Detector):
    """数学错误检测器"""
    
    pattern = FailurePattern.REASONING_MATH_ERROR
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        import re
        
        # 简单的数字关系检测
        patterns = [
            (r'(\d+)\s*[+\-*/]\s*(\d+)\s*=\s*(\d+)', lambda m: self._check_math(m)),
        ]
        
        for pattern, checker in patterns:
            match = re.search(pattern, input_text)
            if match and checker(match):
                return FailureDetection(
                    pattern=self.pattern,
                    level=FailureLevel.REASONING,
                    confidence=0.95,
                    description=f"检测到数学计算错误: {match.group()}",
                    suggested_fix="验证计算步骤，使用计算器核对结果",
                    evidence=[match.group()],
                )
        return None
    
    def _check_math(self, match) -> bool:
        """检查数学表达式是否正确"""
        try:
            a, b, result = int(match.group(1)), int(match.group(2)), int(match.group(3))
            expr = match.group(0)
            if '+' in expr and a + b != result:
                return True
            elif '-' in expr and a - b != result:
                return True
            elif '*' in expr and a * b != result:
                return True
            elif '/' in expr and b != 0 and a / b != result:
                return True
        except Exception:
            pass
        return False


class MemoryConfusionDetector(Detector):
    """记忆混淆检测器"""
    
    pattern = FailurePattern.MEMORY_CONFUSION
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        confusion_patterns = [
            "之前提到的", "如前所述", "正如我们讨论的",
            "在上一轮", "之前的对话", "之前的回答"
        ]
        
        if context and "history" in context:
            history = context["history"]
            for pattern in confusion_patterns:
                if pattern in input_text:
                    # 检查是否确实有相关历史
                    if not history or len(history) == 0:
                        return FailureDetection(
                            pattern=self.pattern,
                            level=FailureLevel.MEMORY,
                            confidence=0.85,
                            description="引用了不存在或不相关的历史内容",
                            suggested_fix="检查对话历史是否正确加载，验证引用的内容",
                            evidence=[f"检测到引用模式: {pattern}"],
                        )
        return None


class MemoryContextLossDetector(Detector):
    """上下文丢失检测器"""
    
    pattern = FailurePattern.MEMORY_CONTEXT_LOSS
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        if context and "expected_context" in context:
            expected = context["expected_context"]
            if expected and expected not in input_text:
                return FailureDetection(
                    pattern=self.pattern,
                    level=FailureLevel.MEMORY,
                    confidence=0.8,
                    description=f"回答中缺少关键上下文信息: {expected}",
                    suggested_fix="确保在回答中包含所有必要的上下文信息",
                    evidence=[f"期望上下文: {expected}"],
                )
        return None


class MemoryContaminationDetector(Detector):
    """记忆污染检测器"""
    
    pattern = FailurePattern.MEMORY_CONTAMINATION
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        if context and "session_id" in context:
            session_id = context["session_id"]
            # 检查是否有其他会话的信息混入
            contamination_indicators = [
                f"会话{session_id[:4]}",
                f"对话{session_id[:4]}",
                f"历史{session_id[:4]}"
            ]
            for indicator in contamination_indicators:
                if indicator not in input_text:
                    # 检查是否有不属于当前会话的信息
                    other_session_patterns = [
                        "用户A", "用户B", "上一个用户", "另一位用户"
                    ]
                    if any(p in input_text for p in other_session_patterns):
                        return FailureDetection(
                            pattern=self.pattern,
                            level=FailureLevel.MEMORY,
                            confidence=0.75,
                            description="检测到可能的记忆污染，回答包含不属于当前会话的信息",
                            suggested_fix="检查会话隔离机制，确保记忆不跨会话泄漏",
                            evidence=other_session_patterns,
                        )
        return None


class AgentRoleMismatchDetector(Detector):
    """角色错位检测器"""
    
    pattern = FailurePattern.AGENT_ROLE_MISMATCH
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        if context and "expected_role" in context:
            expected_role = context["expected_role"]
            role_keywords = {
                "客服": ["您好", "请问", "帮您", "服务"],
                "专家": ["根据", "分析", "研究", "结论"],
                "助手": ["好的", "没问题", "我来", "可以"],
            }
            
            if expected_role in role_keywords:
                expected_keywords = role_keywords[expected_role]
                matched = sum(1 for kw in expected_keywords if kw in input_text)
                if matched == 0:
                    return FailureDetection(
                        pattern=self.pattern,
                        level=FailureLevel.AGENT,
                        confidence=0.7,
                        description=f"回答不符合{expected_role}角色定位",
                        suggested_fix="调整回答风格以符合预期角色",
                        evidence=[f"期望角色: {expected_role}"],
                    )
        return None


class AgentGoalDriftDetector(Detector):
    """目标漂移检测器"""
    
    pattern = FailurePattern.AGENT_GOAL_DRIFT
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        if context and "goal" in context:
            goal = context["goal"]
            # 简单检查目标关键词是否在回答中出现
            goal_words = goal.split()[:5]
            matched = sum(1 for word in goal_words if word in input_text)
            if matched == 0:
                return FailureDetection(
                    pattern=self.pattern,
                    level=FailureLevel.AGENT,
                    confidence=0.8,
                    description="回答偏离了原始目标",
                    suggested_fix="重新聚焦目标，确保回答与任务相关",
                    evidence=[f"原始目标: {goal}"],
                )
        return None


class AgentRefusalDetector(Detector):
    """拒绝执行检测器"""
    
    pattern = FailurePattern.AGENT_REFUSAL
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        refusal_patterns = [
            "我无法", "我不能", "我不可以", "我做不到",
            "无法完成", "无法回答", "抱歉", "对不起"
        ]
        
        count = sum(1 for pattern in refusal_patterns if pattern in input_text)
        if count >= 2:
            return FailureDetection(
                pattern=self.pattern,
                level=FailureLevel.AGENT,
                confidence=0.9,
                description="检测到拒绝执行模式",
                suggested_fix="检查是否有必要的权限或工具，考虑降级策略",
                evidence=[f"检测到{count}个拒绝模式"],
            )
        return None


class ToolMisuseDetector(Detector):
    """工具误用检测器"""
    
    pattern = FailurePattern.TOOL_MISUSE
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        if context and "tool_calls" in context:
            tool_calls = context["tool_calls"]
            for tool_call in tool_calls:
                if "error" in tool_call:
                    return FailureDetection(
                        pattern=self.pattern,
                        level=FailureLevel.TOOL,
                        confidence=0.95,
                        description=f"工具调用失败: {tool_call.get('error', '未知错误')}",
                        suggested_fix="检查工具参数是否正确，验证工具可用性",
                        evidence=[f"工具: {tool_call.get('tool_name', '未知')}"],
                    )
        return None


class ToolAPIFailureDetector(Detector):
    """API调用失败检测器"""
    
    pattern = FailurePattern.TOOL_API_FAILURE
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        api_error_patterns = [
            "API错误", "API调用失败", "服务不可用",
            "超时", "连接失败", "500错误", "404错误"
        ]
        
        for pattern in api_error_patterns:
            if pattern in input_text:
                return FailureDetection(
                    pattern=self.pattern,
                    level=FailureLevel.TOOL,
                    confidence=0.95,
                    description=f"检测到API调用失败: {pattern}",
                    suggested_fix="检查API服务状态，实现重试机制",
                    evidence=[pattern],
                )
        return None


class SafetyBreachDetector(Detector):
    """安全边界突破检测器"""
    
    pattern = FailurePattern.SAFETY_BREACH
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        safety_violations = [
            "密码", "账号", "登录", "验证码",
            "攻击", "入侵", "破解", "漏洞",
            "敏感", "隐私", "机密", "内部"
        ]
        
        count = sum(1 for violation in safety_violations if violation in input_text)
        if count >= 2:
            return FailureDetection(
                pattern=self.pattern,
                level=FailureLevel.SAFETY,
                confidence=0.85,
                description=f"检测到{count}处安全敏感内容",
                suggested_fix="审查回答内容，确保不泄露敏感信息",
                evidence=[f"检测到{count}个安全敏感词"],
            )
        return None


class KnowledgeConflictDetector(Detector):
    """知识冲突检测器"""
    
    pattern = FailurePattern.KNOWLEDGE_CONFLICT
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> Optional[FailureDetection]:
        if context and "knowledge_base" in context:
            kb = context["knowledge_base"]
            for fact in kb:
                if fact in input_text:
                    # 简单检查是否有直接冲突
                    negations = ["不是", "没有", "错误", "不正确"]
                    for negation in negations:
                        if negation in input_text:
                            return FailureDetection(
                                pattern=self.pattern,
                                level=FailureLevel.KNOWLEDGE,
                                confidence=0.8,
                                description=f"回答与知识库内容冲突: {fact}",
                                suggested_fix="核对知识库，确保回答与已知事实一致",
                                evidence=[f"知识库事实: {fact}"],
                            )
        return None


class SymptomMap:
    """
    病候图 - 失败模式检测系统
    
    核心功能:
    1. 16种失败模式检测
    2. 多层级检测（RAG/Reasoning/Memory/Agent/Tool/Safety/Knowledge）
    3. 风险评分计算
    4. 修复建议生成
    
    Usage::
        symptom_map = SymptomMap()
        result = symptom_map.detect("分析结果表明...", context={"retrieved_docs": [...]})
        print(result.overall_risk_score)
        for failure in result.failures:
            print(failure.pattern, failure.confidence)
    """
    
    def __init__(self):
        self._detectors: List[Detector] = [
            # RAG层
            RAGRetrievalFailureDetector(),
            RAGLowRelevanceDetector(),
            RAGOutdatedKnowledgeDetector(),
            RAGNoiseInjectionDetector(),
            
            # Reasoning层
            ReasoningLogicalJumpDetector(),
            ReasoningCircularDetector(),
            ReasoningHallucinationDetector(),
            ReasoningMathErrorDetector(),
            
            # Memory层
            MemoryConfusionDetector(),
            MemoryContextLossDetector(),
            MemoryContaminationDetector(),
            
            # Agent层
            AgentRoleMismatchDetector(),
            AgentGoalDriftDetector(),
            AgentRefusalDetector(),
            
            # Tool层
            ToolMisuseDetector(),
            ToolAPIFailureDetector(),
            
            # Safety层
            SafetyBreachDetector(),
            
            # Knowledge层
            KnowledgeConflictDetector(),
        ]
    
    def detect(self, input_text: str, context: Optional[Dict] = None) -> DetectionResult:
        """
        检测所有失败模式
        
        Args:
            input_text: 待检测文本
            context: 上下文信息
            
        Returns:
            DetectionResult 检测结果
        """
        failures = []
        
        for detector in self._detectors:
            result = detector.detect(input_text, context)
            if result:
                failures.append(result)
        
        # 计算总体风险评分
        if failures:
            overall_risk = sum(f.confidence for f in failures) / len(failures)
        else:
            overall_risk = 0.0
        
        # 判断是否通过检测
        passed = overall_risk < 0.5
        
        return DetectionResult(
            failures=failures,
            overall_risk_score=overall_risk,
            passed=passed,
            metadata={
                'detector_count': len(self._detectors),
                'failure_count': len(failures),
            },
        )
    
    def detect_by_level(self, input_text: str, level: FailureLevel, context: Optional[Dict] = None) -> List[FailureDetection]:
        """
        按层级检测失败模式
        
        Args:
            input_text: 待检测文本
            level: 失败层级
            context: 上下文信息
            
        Returns:
            该层级的失败检测结果列表
        """
        level_detectors = [d for d in self._detectors if self._get_level(d.pattern) == level]
        failures = []
        
        for detector in level_detectors:
            result = detector.detect(input_text, context)
            if result:
                failures.append(result)
        
        return failures
    
    def _get_level(self, pattern: FailurePattern) -> FailureLevel:
        """获取失败模式所属层级"""
        if pattern.value.startswith("rag_"):
            return FailureLevel.RAG
        elif pattern.value.startswith("reasoning_"):
            return FailureLevel.REASONING
        elif pattern.value.startswith("memory_"):
            return FailureLevel.MEMORY
        elif pattern.value.startswith("agent_"):
            return FailureLevel.AGENT
        elif pattern.value.startswith("tool_"):
            return FailureLevel.TOOL
        elif pattern.value.startswith("safety_"):
            return FailureLevel.SAFETY
        elif pattern.value.startswith("knowledge_"):
            return FailureLevel.KNOWLEDGE
        return FailureLevel.REASONING
    
    def get_detectors(self) -> List[Detector]:
        """获取所有检测器"""
        return self._detectors.copy()
    
    def add_detector(self, detector: Detector):
        """添加自定义检测器"""
        self._detectors.append(detector)
    
    def remove_detector(self, pattern: FailurePattern):
        """移除指定类型的检测器"""
        self._detectors = [d for d in self._detectors if d.pattern != pattern]
