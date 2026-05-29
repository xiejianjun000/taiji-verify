"""
Cross Model Verifier - ARIS交叉模型验证器

ARIS = Agreement and Robustness via Independent Systems

核心概念：
- 用多个独立LLM验证同一结论，交叉比对提高可信度
- 模型分歧 = 潜在幻觉信号
- 参考EcoMind-OS的ModelRouter模式，独立实现

功能：
- ModelProvider抽象基类，支持DeepSeek/Qwen/GLM/Mock
- CrossModelVerifier交叉验证器
- 一致性矩阵计算
- 分歧检测与标记
- 交叉验证置信度计算

v2.2 Phase 1
"""

from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from taiji_verify.embedding import EmbeddingProvider
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np


class CrossModelVerdict(str, Enum):
    """
    交叉验证判定

    - AGREE: 所有模型达成一致
    - DISAGREE: 模型之间存在明显分歧
    - PARTIAL: 部分一致，部分分歧
    - INSUFFICIENT: 样本不足，无法判定
    """

    AGREE = "agree"
    DISAGREE = "disagree"
    PARTIAL = "partial"
    INSUFFICIENT = "insufficient"


class ModelProvider(ABC):
    """
    模型提供者抽象基类

    定义LLM模型调用的标准接口。
    所有具体实现需遵循此接口规范。

    Usage:
        class MyProvider(ModelProvider):
            def generate(self, prompt: str, **kwargs) -> str:
                # 实现调用逻辑
                return "模型回复"

        provider = MyProvider()
        response = provider.generate("你好")
        print(provider.get_model_id())
    """

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成回复

        Args:
            prompt: 输入提示词
            **kwargs: 额外参数（temperature, max_tokens等）

        Returns:
            str: 模型生成的回复文本
        """
        pass

    @abstractmethod
    def get_model_id(self) -> str:
        """
        获取模型标识符

        Returns:
            str: 模型ID，如 "deepseek-chat", "qwen-turbo" 等
        """
        pass

    def get_api_base(self) -> Optional[str]:
        """
        获取API端点（可选实现）

        Returns:
            Optional[str]: API基础URL
        """
        return None


class MockProvider(ModelProvider):
    """
    测试用Mock模型提供者

    基于规则生成回复，用于零依赖测试环境。
    支持配置返回模式：agree（一致）/ disagree（分歧）/ partial（部分）

    Usage:
        provider = MockProvider(model_id="mock-1")
        response = provider.generate("地球是圆的吗？")  # 返回预设回复
    """

    def __init__(
        self,
        model_id: str = "mock-default",
        response_mode: str = "agree",
        fixed_response: Optional[str] = None,
    ):
        """
        初始化Mock提供者

        Args:
            model_id: 模型标识符
            response_mode: 回复模式
                - "agree": 所有模型返回相似内容
                - "disagree": 返回相互矛盾的内容
                - "partial": 返回部分相似
            fixed_response: 固定回复内容（优先使用）
        """
        self._model_id = model_id
        self._response_mode = response_mode
        self._fixed_response = fixed_response

    def generate(self, prompt: str, **kwargs) -> str:
        """根据模式生成Mock回复"""
        if self._fixed_response:
            return self._fixed_response

        # 分析问题类型
        prompt_lower = prompt.lower()

        # 事实类问题
        if any(keyword in prompt_lower for keyword in ["是", "是什么", "谁", "哪个", "多少"]):
            if self._response_mode == "agree":
                return self._generate_agree_response(prompt)
            elif self._response_mode == "disagree":
                return self._generate_disagree_response(prompt)
            else:
                return self._generate_partial_response(prompt)

        # 是非类问题
        if any(keyword in prompt_lower for keyword in ["对", "错", "应该", "可以"]):
            if self._response_mode == "agree":
                return "根据现有知识，该判断是正确的。"
            elif self._response_mode == "disagree":
                return "该判断存在问题，需要进一步验证。"
            else:
                return "该判断需要结合具体情况分析。"

        # 默认回复
        return f"【{self._model_id}】这是一个需要综合分析的结论。"

    def _generate_agree_response(self, prompt: str) -> str:
        """生成一致的回复"""
        return "该结论与现有知识体系一致，可以作为参考。"

    def _generate_disagree_response(self, prompt: str) -> str:
        """生成分歧的回复"""
        return "该结论存在争议，不同来源有不同观点，需要谨慎对待。"

    def _generate_partial_response(self, prompt: str) -> str:
        """生成部分一致的回复"""
        return "该结论部分正确，但需要补充更多证据支持。"

    def get_model_id(self) -> str:
        """获取模型ID"""
        return self._model_id


class DeepSeekProvider(ModelProvider):
    """
    DeepSeek模型提供者

    直连DeepSeek API，默认使用 deepseek-chat 模型。
    使用OpenAI兼容接口格式。

    环境变量:
        DEEPSEEK_API_KEY: API密钥

    Usage:
        provider = DeepSeekProvider(api_key="sk-xxx")
        response = provider.generate("解释量子力学")
    """

    def __init__(
        self,
        model: str = "deepseek-chat",
        api_base: str = "https://api.deepseek.com",
        api_key: Optional[str] = None,
    ):
        """
        初始化DeepSeek提供者

        Args:
            model: 模型名称，默认 deepseek-chat
            api_base: API基础URL
            api_key: API密钥，默认从环境变量获取
        """
        self._model = model
        self._api_base = api_base
        self._api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self._client = None

    def _get_client(self):
        """延迟初始化OpenAI兼容客户端"""
        if self._client is None:
            try:
                from openai import OpenAI

                self._client = OpenAI(
                    api_key=self._api_key,
                    base_url=self._api_base,
                )
            except ImportError:
                raise ImportError("openai package required. Install: pip install openai")
        return self._client

    def generate(self, prompt: str, **kwargs) -> str:
        """调用DeepSeek API生成回复"""
        client = self._get_client()

        default_kwargs = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1024),
        }

        response = client.chat.completions.create(**default_kwargs)
        return response.choices[0].message.content

    def get_model_id(self) -> str:
        """获取模型ID"""
        return self._model

    def get_api_base(self) -> Optional[str]:
        """获取API端点"""
        return self._api_base


class QwenProvider(ModelProvider):
    """
    通义千问模型提供者

    直连阿里云百炼API，使用OpenAI兼容接口格式。

    环境变量:
        DASHSCOPE_API_KEY: API密钥

    Usage:
        provider = QwenProvider(api_key="sk-xxx")
        response = provider.generate("解释量子力学")
    """

    def __init__(
        self,
        model: str = "qwen-turbo",
        api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key: Optional[str] = None,
    ):
        """
        初始化Qwen提供者

        Args:
            model: 模型名称，默认 qwen-turbo
            api_base: API基础URL
            api_key: API密钥，默认从环境变量获取
        """
        self._model = model
        self._api_base = api_base
        self._api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self._client = None

    def _get_client(self):
        """延迟初始化OpenAI兼容客户端"""
        if self._client is None:
            try:
                from openai import OpenAI

                self._client = OpenAI(
                    api_key=self._api_key,
                    base_url=self._api_base,
                )
            except ImportError:
                raise ImportError("openai package required. Install: pip install openai")
        return self._client

    def generate(self, prompt: str, **kwargs) -> str:
        """调用Qwen API生成回复"""
        client = self._get_client()

        default_kwargs = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1024),
        }

        response = client.chat.completions.create(**default_kwargs)
        return response.choices[0].message.content

    def get_model_id(self) -> str:
        """获取模型ID"""
        return self._model

    def get_api_base(self) -> Optional[str]:
        """获取API端点"""
        return self._api_base


class GLMProvider(ModelProvider):
    """
    智谱GLM模型提供者

    直连智谱AI API，使用OpenAI兼容接口格式。

    环境变量:
        ZHIPUAI_API_KEY: API密钥

    Usage:
        provider = GLMProvider(api_key="sk-xxx")
        response = provider.generate("解释量子力学")
    """

    def __init__(
        self,
        model: str = "glm-4",
        api_base: str = "https://open.bigmodel.cn/api/paas/v4",
        api_key: Optional[str] = None,
    ):
        """
        初始化GLM提供者

        Args:
            model: 模型名称，默认 glm-4
            api_base: API基础URL
            api_key: API密钥，默认从环境变量获取
        """
        self._model = model
        self._api_base = api_base
        self._api_key = api_key or os.getenv("ZHIPUAI_API_KEY")
        self._client = None

    def _get_client(self):
        """延迟初始化OpenAI兼容客户端"""
        if self._client is None:
            try:
                from openai import OpenAI

                self._client = OpenAI(
                    api_key=self._api_key,
                    base_url=self._api_base,
                )
            except ImportError:
                raise ImportError("openai package required. Install: pip install openai")
        return self._client

    def generate(self, prompt: str, **kwargs) -> str:
        """调用GLM API生成回复"""
        client = self._get_client()

        default_kwargs = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1024),
        }

        response = client.chat.completions.create(**default_kwargs)
        return response.choices[0].message.content

    def get_model_id(self) -> str:
        """获取模型ID"""
        return self._model

    def get_api_base(self) -> Optional[str]:
        """获取API端点"""
        return self._api_base


@dataclass
class CrossModelResult:
    """
    交叉验证结果

    存储单个结论的交叉验证结果，包括各模型回复、一致性分析和判定。

    Attributes:
        conclusion: 待验证的结论文本
        model_responses: 各模型的回复字典 {model_id: response}
        agreement_matrix: N×N一致性矩阵
        agreement_rate: 整体一致率（0-1）
        disagreement_flags: 检测到的分歧标记列表
        verdict: 交叉验证判定（AGREE/DISAGREE/PARTIAL/INSUFFICIENT）
        confidence: 交叉验证置信度（0-1）
    """

    conclusion: str
    model_responses: dict[str, str] = field(default_factory=dict)
    agreement_matrix: np.ndarray = field(default_factory=lambda: np.array([]))
    agreement_rate: float = 0.0
    disagreement_flags: list[str] = field(default_factory=list)
    verdict: CrossModelVerdict = CrossModelVerdict.INSUFFICIENT
    confidence: float = 0.0

    @property
    def model_count(self) -> int:
        """参与的模型数量"""
        return len(self.model_responses)

    @property
    def has_disagreement(self) -> bool:
        """是否存在分歧"""
        return len(self.disagreement_flags) > 0

    def get_response(self, model_id: str) -> Optional[str]:
        """获取指定模型的回复"""
        return self.model_responses.get(model_id)


class CrossModelVerifier:
    """
    ARIS交叉模型验证器

    使用多个独立LLM验证同一结论，通过交叉比对提高结论可信度。
    核心假设：真正的知识应该在不同模型间保持一致，而幻觉往往因模型而异。

    设计原则：
    - 默认使用MockProvider，确保零依赖下可测试
    - 支持2-5个模型同时验证
    - 一致性矩阵结合语义相似度和关键词重叠

    Usage:
        # 零依赖测试
        verifier = CrossModelVerifier()  # 默认使用Mock
        result = verifier.verify("地球是圆的")

        # 生产环境
        providers = [
            DeepSeekProvider(api_key="sk-xxx"),
            QwenProvider(api_key="sk-xxx"),
            GLMProvider(api_key="sk-xxx"),
        ]
        verifier = CrossModelVerifier(providers=providers)
        result = verifier.verify("碳排放权交易的原理是什么？")
    """

    DEFAULT_DISAGREEMENT_THRESHOLD = 0.3
    DEFAULT_MIN_MODELS = 2
    DEFAULT_MAX_MODELS = 5

    def __init__(
        self,
        providers: Optional[list[ModelProvider]] = None,
        disagreement_threshold: float = DEFAULT_DISAGREEMENT_THRESHOLD,
        min_models: int = DEFAULT_MIN_MODELS,
        max_models: int = DEFAULT_MAX_MODELS,
        embedding_provider: Optional["EmbeddingProvider"] = None,  # type: ignore[name-defined]
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ):
        """
        初始化交叉验证器

        Args:
            providers: 模型提供者列表，默认使用MockProvider
            disagreement_threshold: 分歧阈值（默认0.3），低于此值视为分歧
            min_models: 最少模型数量（默认2）
            max_models: 最多模型数量（默认5）
            embedding_provider: 嵌入提供者（用于语义相似度计算）
            semantic_weight: 语义相似度权重（默认0.7）
            keyword_weight: 关键词重叠权重（默认0.3）
        """
        if providers is None:
            # 默认使用MockProvider，确保零依赖可测试
            self._providers = [
                MockProvider(model_id="mock-model-1", response_mode="agree"),
                MockProvider(model_id="mock-model-2", response_mode="agree"),
                MockProvider(model_id="mock-model-3", response_mode="agree"),
            ]
        else:
            if len(providers) < min_models:
                raise ValueError(
                    f"至少需要 {min_models} 个模型提供者，当前只有 {len(providers)} 个"
                )
            if len(providers) > max_models:
                raise ValueError(f"最多支持 {max_models} 个模型提供者，当前有 {len(providers)} 个")
            self._providers = providers

        self._disagreement_threshold = disagreement_threshold
        self._min_models = min_models
        self._max_models = max_models
        self._embedding_provider = embedding_provider
        self._semantic_weight = semantic_weight
        self._keyword_weight = keyword_weight

    def verify(
        self,
        conclusion: str,
        context: Optional[str] = None,
        prompt_template: Optional[str] = None,
    ) -> CrossModelResult:
        """
        单条交叉验证

        使用多个模型验证同一结论，计算一致率并检测分歧。

        Args:
            conclusion: 待验证的结论
            context: 上下文信息（可选）
            prompt_template: 自定义提示模板，默认使用内部模板

        Returns:
            CrossModelResult: 交叉验证结果
        """
        if not conclusion or not conclusion.strip():
            return self._create_empty_result(conclusion)

        # 构建提示词
        prompt = self._build_prompt(conclusion, context, prompt_template)

        # 并行调用所有模型
        model_responses: dict[str, str] = {}
        for provider in self._providers:
            try:
                response = provider.generate(prompt)
                model_responses[provider.get_model_id()] = response
            except Exception as e:
                # 单个模型失败不影响整体
                model_responses[provider.get_model_id()] = f"[Error: {str(e)}]"

        # 计算一致性矩阵
        responses_list = list(model_responses.values())
        agreement_matrix = self.compute_agreement(responses_list)

        # 计算一致率
        agreement_rate = self._compute_agreement_rate(agreement_matrix)

        # 检测分歧
        result = CrossModelResult(
            conclusion=conclusion,
            model_responses=model_responses,
            agreement_matrix=agreement_matrix,
            agreement_rate=agreement_rate,
        )
        disagreement_flags = self.detect_disagreement(result)
        result.disagreement_flags = disagreement_flags

        # 判定
        result.verdict = self._compute_verdict(agreement_rate, len(disagreement_flags))
        result.confidence = self._compute_confidence(
            agreement_rate, len(disagreement_flags), len(model_responses)
        )

        return result

    def batch_verify(
        self,
        conclusions: list[str],
        context: Optional[str] = None,
        prompt_template: Optional[str] = None,
        max_concurrency: int = 3,
    ) -> list[CrossModelResult]:
        """
        批量交叉验证

        对多个结论进行批量交叉验证。

        Args:
            conclusions: 结论列表
            context: 共享上下文（可选）
            prompt_template: 自定义提示模板
            max_concurrency: 最大并发数（预留，当前串行）

        Returns:
            list[CrossModelResult]: 验证结果列表
        """
        results = []
        for conclusion in conclusions:
            result = self.verify(conclusion, context, prompt_template)
            results.append(result)
        return results

    def compute_agreement(self, responses: list[str]) -> np.ndarray:
        """
        计算N×N一致性矩阵

        基于语义相似度和关键词重叠计算模型回复之间的一致性。

        Args:
            responses: 模型回复列表

        Returns:
            np.ndarray: N×N一致性矩阵，matrix[i][j]表示第i个和第j个回复的一致性
        """
        n = len(responses)
        if n == 0:
            return np.array([])

        matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 1.0
                else:
                    matrix[i][j] = self._compute_pairwise_agreement(responses[i], responses[j])

        return matrix

    def detect_disagreement(self, result: CrossModelResult) -> list[str]:
        """
        检测具体分歧点

        分析模型回复，识别具体分歧内容和位置。

        Args:
            result: 交叉验证结果

        Returns:
            list[str]: 分歧标记列表，每项描述一个分歧点
        """
        flags = []

        if result.model_count < 2:
            return flags

        responses = list(result.model_responses.values())

        # 检测关键词不一致
        keywords_sets = [self._extract_keywords(r) for r in responses]
        if len(keywords_sets) >= 2:
            for i in range(len(keywords_sets)):
                for j in range(i + 1, len(keywords_sets)):
                    diff = keywords_sets[i] ^ keywords_sets[j]
                    if diff:
                        # 取前3个差异关键词
                        sample_diffs = list(diff)[:3]
                        flags.append(f"关键词不一致: {', '.join(sample_diffs)}")

        # 检测数值不一致
        numbers = re.findall(r"\d+(?:\.\d+)?%", " ".join(responses))
        if numbers:
            unique_numbers = set(numbers)
            if len(unique_numbers) > 1:
                flags.append(f"数值差异: 发现多个数值 {unique_numbers}")

        # 检测确定性程度不一致
        certainty_keywords = [
            ("确定", "不确定"),
            ("是", "否"),
            ("正确", "错误"),
            ("可以", "不可以"),
            ("必须", "不必"),
        ]
        for pos_kw, neg_kw in certainty_keywords:
            counts = [r.count(pos_kw) + r.count(neg_kw) for r in responses]
            if counts and max(counts) > 0:
                # 计算确定性差异
                pos_counts = [r.count(pos_kw) for r in responses]
                neg_counts = [r.count(neg_kw) for r in responses]
                if pos_counts and neg_counts:
                    total_pos = sum(pos_counts)
                    total_neg = sum(neg_counts)
                    if total_pos > 0 and total_neg > 0:
                        ratio = min(total_pos, total_neg) / max(total_pos, total_neg)
                        if ratio < 0.5:
                            flags.append(
                                f"确定性程度不一致: 肯定表述{total_pos}次 vs 否定表述{total_neg}次"
                            )

        # 检测来源引用不一致
        sources = [self._extract_sources(r) for r in responses]
        all_sources = set()
        for s in sources:
            all_sources.update(s)
        if len(all_sources) > 1:
            flags.append(f"来源引用差异: 发现多个来源 {all_sources}")

        # 去重
        seen = set()
        unique_flags = []
        for flag in flags:
            flag_key = flag.split(":")[0]  # 用类型作为去重键
            if flag_key not in seen:
                seen.add(flag_key)
                unique_flags.append(flag)

        return unique_flags

    def compute_cross_validation_score(self, results: list[CrossModelResult]) -> float:
        """
        计算交叉验证覆盖分数

        综合多个结论的验证结果，计算整体置信度。

        Args:
            results: 交叉验证结果列表

        Returns:
            float: 交叉验证覆盖分数（0-1）
        """
        if not results:
            return 0.0

        # 统计各类型判定数量
        verdict_counts = {
            CrossModelVerdict.AGREE: 0,
            CrossModelVerdict.DISAGREE: 0,
            CrossModelVerdict.PARTIAL: 0,
            CrossModelVerdict.INSUFFICIENT: 0,
        }

        for result in results:
            verdict_counts[result.verdict] += 1

        total = len(results)

        # 加权计算分数
        score = (
            verdict_counts[CrossModelVerdict.AGREE] * 1.0
            + verdict_counts[CrossModelVerdict.PARTIAL] * 0.5
            + verdict_counts[CrossModelVerdict.DISAGREE] * 0.0
            + verdict_counts[CrossModelVerdict.INSUFFICIENT] * 0.3
        ) / total

        return score

    def _build_prompt(
        self,
        conclusion: str,
        context: Optional[str],
        prompt_template: Optional[str],
    ) -> str:
        """构建验证提示词"""
        if prompt_template:
            return prompt_template.format(conclusion=conclusion, context=context or "")

        base_prompt = "请验证以下结论的准确性：\n\n"
        base_prompt += f"结论：{conclusion}\n\n"

        if context:
            base_prompt += f"上下文：{context}\n\n"

        base_prompt += "请判断该结论是否正确，并简要说明理由。"

        return base_prompt

    def _compute_pairwise_agreement(self, text1: str, text2: str) -> float:
        """
        计算两个回复之间的一致性

        综合语义相似度和关键词重叠。

        Args:
            text1: 第一个回复
            text2: 第二个回复

        Returns:
            float: 一致性分数（0-1）
        """
        # 语义相似度
        semantic_sim = self._compute_semantic_similarity(text1, text2)

        # 关键词重叠
        keyword_sim = self._compute_keyword_overlap(text1, text2)

        # 加权平均
        return self._semantic_weight * semantic_sim + self._keyword_weight * keyword_sim

    def _compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        计算语义相似度

        如果有嵌入提供者，使用向量余弦相似度；否则使用词重叠作为代理。
        """
        if self._embedding_provider:
            try:
                vec1 = self._embedding_provider.embed(text1)
                vec2 = self._embedding_provider.embed(text2)
                # 余弦相似度
                cos_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                return float(cos_sim)
            except Exception:
                pass

        # 降级：使用字符级Jaccard相似度
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def _compute_keyword_overlap(self, text1: str, text2: str) -> float:
        """
        计算关键词重叠度

        提取关键词并计算Jaccard重叠。
        """
        keywords1 = self._extract_keywords(text1)
        keywords2 = self._extract_keywords(text2)

        if not keywords1 or not keywords2:
            return 0.0

        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)

        return intersection / union if union > 0 else 0.0

    def _extract_keywords(self, text: str) -> set[str]:
        """
        提取关键词

        使用简单规则提取有意义的词汇。
        """
        # 提取连续的中文词（2-4字）
        chinese_words = re.findall(r"[\u4e00-\u9fa5]{2,4}", text)

        # 提取英文单词
        english_words = re.findall(r"[a-zA-Z]{3,}", text.lower())

        # 提取数字+单位
        # 合并去重
        keywords = set(chinese_words + english_words)

        return keywords

    def _extract_sources(self, text: str) -> set[str]:
        """
        提取来源引用

        识别法律条文、文献引用等来源。
        """
        sources = set()

        # 法律引用
        law_patterns = [
            r"《([^》]+)》",
            r"第(\d+)条",
            r"([\u4e00-\u9fa5]{2,}法)",
            r"([\u4e00-\u9fa5]{2,}条例)",
        ]
        for pattern in law_patterns:
            matches = re.findall(pattern, text)
            sources.update(matches)

        return sources

    def _compute_agreement_rate(self, matrix: np.ndarray) -> float:
        """
        从一致性矩阵计算整体一致率

        使用矩阵上三角的平均值作为一致率。
        """
        if matrix.size == 0:
            return 0.0

        n = matrix.shape[0]
        if n <= 1:
            return 1.0

        # 提取上三角（不含对角线）
        upper_triangle = matrix[np.triu_indices(n, k=1)]
        return float(np.mean(upper_triangle))

    def _compute_verdict(self, agreement_rate: float, disagreement_count: int) -> CrossModelVerdict:
        """
        根据一致率和分歧数量计算判定

        Args:
            agreement_rate: 一致率（0-1）
            disagreement_count: 分歧标记数量

        Returns:
            CrossModelVerdict: 判定结果
        """
        if agreement_rate >= 0.8 and disagreement_count == 0:
            return CrossModelVerdict.AGREE
        elif agreement_rate < self._disagreement_threshold:
            return CrossModelVerdict.DISAGREE
        elif agreement_rate >= 0.5 and disagreement_count > 0:
            return CrossModelVerdict.PARTIAL
        else:
            return CrossModelVerdict.PARTIAL

    def _compute_confidence(
        self, agreement_rate: float, disagreement_count: int, model_count: int
    ) -> float:
        """
        计算交叉验证置信度

        综合一致率、分歧数量和模型数量计算置信度。

        Args:
            agreement_rate: 一致率
            disagreement_count: 分歧数量
            model_count: 模型数量

        Returns:
            float: 置信度（0-1）
        """
        # 基础分数 = 一致率
        base_score = agreement_rate

        # 分歧惩罚
        disagreement_penalty = min(disagreement_count * 0.1, 0.3)

        # 模型数量加成（更多模型更可信）
        model_bonus = min((model_count - 2) * 0.05, 0.15)

        confidence = base_score - disagreement_penalty + model_bonus

        return max(0.0, min(1.0, confidence))

    def _create_empty_result(self, conclusion: str) -> CrossModelResult:
        """创建空结果"""
        return CrossModelResult(
            conclusion=conclusion,
            verdict=CrossModelVerdict.INSUFFICIENT,
            confidence=0.0,
        )

    @property
    def providers(self) -> list[ModelProvider]:
        """获取当前配置的模型提供者列表"""
        return self._providers.copy()

    @property
    def provider_count(self) -> int:
        """获取模型提供者数量"""
        return len(self._providers)
