"""
模型指纹识别器

识别文本可能来自哪个AI模型

支持的模型：
- GPT系列 (OpenAI)
- Claude系列 (Anthropic)
- 文心一言 (百度)
- 通义千问 (阿里)
- 智谱GLM (清华)
- Kimi/Moonshot (月之暗面)
- 混元 (腾讯)
- 豆包 (字节)
- DeepSeek (深度求索)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ModelType(str, Enum):
    """AI模型类型"""
    GPT4 = "gpt4"
    GPT35 = "gpt3.5"
    CLAUDE = "claude"
    WENXIN = "wenxin"
    TONGYI = "tongyi"
    ZHIPU = "zhipu"
    KIMI = "kimi"
    HUNYUAN = "hunyuan"
    DOUBAO = "doubao"
    DEEPSEEK = "deepseek"
    ERNIE = "ernie"
    SPARK = "spark"
    UNKNOWN = "unknown"


@dataclass
class ModelFingerprint:
    """模型指纹"""
    model_type: ModelType
    confidence: float
    evidence: list[str]
    model_name: Optional[str] = None


class ModelFingerprintDetector:
    """
    模型指纹检测器

    通过分析文本特征识别可能的模型来源。

    Usage:
        detector = ModelFingerprintDetector()
        result = detector.detect("待检测文本")
        print(f"模型: {result.model_type.value}")
        print(f"置信度: {result.confidence:.2%}")
    """

    def __init__(self):
        self._patterns = self._build_patterns()

    def _build_patterns(self) -> dict[ModelType, list[tuple[str, float]]]:
        """构建模型特征模式"""
        return {
            ModelType.GPT4: [
                (r"\bCertainly! Here's\b", 0.7),
                (r"\bI'd be happy to help\b", 0.6),
                (r"\bAs an AI language model\b", 0.8),
                (r"\bI cannot .* because I don't have\b", 0.7),
                (r"\bI'm sorry, but I can't\b", 0.6),
                (r"\bI should note that\b", 0.5),
                (r"\bIt's important to\b", 0.5),
                (r"\bHere's a breakdown\b", 0.6),
                (r"\bStep-by-step\b", 0.5),
            ],
            ModelType.CLAUDE: [
                (r"\bI think this is a great question\b", 0.7),
                (r"\b[Ii]s there anything else\b", 0.6),
                (r"\bLet me help you with that\b", 0.5),
                (r"\bHere's what I found\b", 0.5),
                (r"\bI'd be glad to\b", 0.6),
                (r"\bThinking carefully\b", 0.5),
                (r"\bThe key considerations are\b", 0.6),
            ],
            ModelType.WENXIN: [
                (r"\b您好，我是百度文心一言\b", 0.9),
                (r"\b作为一个人工智能模型\b", 0.8),
                (r"\b我无法.*因为我没有\b", 0.7),
                (r"\b根据我的训练数据\b", 0.6),
                (r"\b让我来帮您分析\b", 0.5),
                (r"\b以下是.*的建议\b", 0.5),
                (r"文心一言", 0.9),
            ],
            ModelType.TONGYI: [
                (r"\b您好，我是通义千问\b", 0.9),
                (r"\b作为一个AI助手\b", 0.7),
                (r"\b让我为您解答\b", 0.6),
                (r"\b根据您的描述\b", 0.5),
                (r"\b以下是相关建议\b", 0.5),
                (r"通义千问", 0.9),
            ],
            ModelType.ZHIPU: [
                (r"\b我是智谱AI\b", 0.9),
                (r"\b基于GLM.*模型\b", 0.8),
                (r"\b作为认知智能模型\b", 0.8),
                (r"\b根据我的理解\b", 0.5),
                (r"\b以下是.*的回答\b", 0.5),
                (r"智谱|GLM", 0.8),
            ],
            ModelType.KIMI: [
                (r"\b我来帮你分析一下\b", 0.7),
                (r"\b让我仔细看一下\b", 0.6),
                (r"\b好的，我来\b", 0.5),
                (r"\b好的，我理解\b", 0.5),
                (r"\b这个问题可以从.*角度分析\b", 0.6),
                (r"Kimi|Moonshot|moonshot", 0.9),
            ],
            ModelType.HUNYUAN: [
                (r"\b我是腾讯混元助手\b", 0.9),
                (r"\b基于腾讯混元大模型\b", 0.8),
                (r"\b作为腾讯AI助手\b", 0.7),
                (r"混元|Tencent Hunyuan", 0.9),
            ],
            ModelType.DOUBAO: [
                (r"\b我是字节豆包\b", 0.9),
                (r"\b基于豆包大模型\b", 0.8),
                (r"\b作为字节的AI助手\b", 0.7),
                (r"豆包|Doubao", 0.9),
            ],
            ModelType.DEEPSEEK: [
                (r"\bDeepSeek[是一个]*\b", 0.9),
                (r"\b我是由DeepSeek开发的\b", 0.9),
                (r"\b深度求索\b", 0.8),
                (r"\bLet me think step by step\b", 0.7),
                (r"\bFirst,.*Second,.*Third,\b", 0.6),
            ],
            ModelType.ERNIE: [
                (r"\b我是百度文心大模型\b", 0.9),
                (r"\b基于文心大模型\b", 0.8),
                (r"\b作为ERNIE Bot\b", 0.8),
                (r"文心大模型|ERNIE", 0.9),
            ],
            ModelType.SPARK: [
                (r"\b我是讯飞星火大模型\b", 0.9),
                (r"\b基于星火认知大模型\b", 0.8),
                (r"\b讯飞|Spark\b", 0.9),
            ],
        }

    def detect(self, text: str) -> ModelFingerprint:
        """
        检测文本可能的模型来源

        Args:
            text: 待检测文本

        Returns:
            ModelFingerprint: 模型指纹
        """
        scores: dict[ModelType, float] = {}

        for model_type, patterns in self._patterns.items():
            total_score = 0.0
            evidence: list[str] = []

            for pattern, weight in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    total_score += weight
                    evidence.append(pattern)

            if evidence:
                scores[model_type] = total_score

        if not scores:
            return ModelFingerprint(
                model_type=ModelType.UNKNOWN,
                confidence=0.0,
                evidence=[],
            )

        best_model = max(scores.items(), key=lambda x: x[1])
        model_type, score = best_model

        confidence = min(score / 3.0, 1.0)

        return ModelFingerprint(
            model_type=model_type,
            confidence=confidence,
            evidence=evidence,
        )

    def detect_all(self, text: str) -> list[ModelFingerprint]:
        """
        检测所有可能的模型来源

        Returns:
            按置信度排序的模型列表
        """
        scores: dict[ModelType, float] = {}

        for model_type, patterns in self._patterns.items():
            total_score = 0.0

            for pattern, weight in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    total_score += weight

            if total_score > 0:
                scores[model_type] = min(total_score / 3.0, 1.0)

        results = [
            ModelFingerprint(
                model_type=m,
                confidence=c,
                evidence=[],
            )
            for m, c in sorted(scores.items(), key=lambda x: x[1], reverse=True)
        ]

        return results


def create_default_detector() -> ModelFingerprintDetector:
    """创建默认检测器"""
    return ModelFingerprintDetector()
