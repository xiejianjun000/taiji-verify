"""
坤守 (Kun Guard) - 语义残差修正模块

数学公式: B = I - G + m * c²

其中:
    I = 输入向量 (Input)
    G = 知识向量 (Ground truth / Knowledge)
    m = 残差修正系数 (默认 0.5)
    c = 知识库置信度向量 (Confidence)

残差阈值体系:
- LOW (<0.3): 低风险，无需修正
- MEDIUM (0.3-0.6): 中等风险，建议修正
- HIGH (0.6-0.9): 高风险，需要修正
- CRITICAL (>=0.9): 严重风险，必须拦截

数据来源：基于阶段一基线数据推算与行业同类系统对标
"""

from __future__ import annotations

import numpy as np
from numpy.linalg import norm
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict


class HazardLevel(str, Enum):
    """危害等级"""
    LOW = "low"           # < 0.3
    MEDIUM = "medium"     # 0.3 - 0.6
    HIGH = "high"         # 0.6 - 0.9
    CRITICAL = "critical" # >= 0.9

    @classmethod
    def from_residual(cls, residual: float) -> HazardLevel:
        """根据残差值返回对应危害等级"""
        if residual < 0.3:
            return cls.LOW
        elif residual < 0.6:
            return cls.MEDIUM
        elif residual < 0.9:
            return cls.HIGH
        else:
            return cls.CRITICAL


@dataclass
class KnowledgeAnchor:
    """知识锚点"""
    anchor_id: str
    content: str
    vector: np.ndarray
    confidence: float = 1.0
    source: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class KunGuardResult:
    """坤守修正结果"""
    corrected_vector: np.ndarray
    residual: float
    hazard_level: HazardLevel
    anchor_used: Optional[str] = None
    correction_applied: bool = False
    metadata: Dict = field(default_factory=dict)

    @property
    def needs_correction(self) -> bool:
        return self.hazard_level in (HazardLevel.HIGH, HazardLevel.CRITICAL)

    @property
    def should_block(self) -> bool:
        return self.hazard_level == HazardLevel.CRITICAL


class KunGuard:
    """
    坤守 - 语义残差修正器

    核心功能:
    1. 计算输入与知识库的语义残差
    2. 根据残差等级进行修正
    3. 支持知识锚点投影
    4. 危害等级判定

    Usage::
        guard = KunGuard()
        guard.add_knowledge_anchor("环保法规定", vector=law_vector)
        result = guard.correct(input_vector, ground_vector)
        print(result.residual, result.hazard_level)
    """

    def __init__(
        self,
        correction_factor: float = 0.5,
        low_threshold: float = 0.3,
        medium_threshold: float = 0.6,
        high_threshold: float = 0.9,
    ):
        """
        Args:
            correction_factor: 残差修正系数 m，默认 0.5
            low_threshold: 低风险阈值
            medium_threshold: 中风险阈值
            high_threshold: 高风险阈值
        """
        self.m = correction_factor
        self._thresholds = {
            'low': low_threshold,
            'medium': medium_threshold,
            'high': high_threshold,
        }
        self._anchors: Dict[str, KnowledgeAnchor] = {}

    def add_knowledge_anchor(
        self,
        content: str,
        vector: np.ndarray,
        confidence: float = 1.0,
        source: str = "",
        tags: Optional[List[str]] = None,
    ) -> str:
        """添加知识锚点"""
        anchor_id = f"anchor_{len(self._anchors) + 1}"
        self._anchors[anchor_id] = KnowledgeAnchor(
            anchor_id=anchor_id,
            content=content,
            vector=vector / (norm(vector) + 1e-10),
            confidence=confidence,
            source=source,
            tags=tags or [],
        )
        return anchor_id

    def remove_knowledge_anchor(self, anchor_id: str) -> bool:
        """移除知识锚点"""
        if anchor_id in self._anchors:
            del self._anchors[anchor_id]
            return True
        return False

    def clear_anchors(self):
        """清除所有锚点"""
        self._anchors.clear()

    def compute_residual(self, input_vector: np.ndarray, ground_vector: np.ndarray) -> float:
        """
        计算语义残差: ||I - G||
        
        Args:
            input_vector: 输入向量
            ground_vector: 知识向量（ground truth）
        
        Returns:
            残差值 ∈ [0, 1]
        """
        diff = input_vector - ground_vector
        residual = float(norm(diff))
        return min(residual, 1.0)

    def check_hazard(self, residual: float) -> tuple[HazardLevel, bool]:
        """
        检查危害等级
        
        Returns:
            (危害等级, 是否需要修正)
        """
        level = HazardLevel.from_residual(residual)
        needs_correction = level in (HazardLevel.HIGH, HazardLevel.CRITICAL)
        return level, needs_correction

    def correct(
        self,
        input_vector: np.ndarray,
        ground_vector: np.ndarray,
        confidence_vector: Optional[np.ndarray] = None,
    ) -> KunGuardResult:
        """
        执行语义残差修正
        
        核心公式: B = I - G + m * c²
        
        Args:
            input_vector: 输入向量 I
            ground_vector: 知识向量 G
            confidence_vector: 置信度向量 c（可选）
        
        Returns:
            KunGuardResult 修正结果
        """
        # 归一化向量
        input_vec = input_vector / (norm(input_vector) + 1e-10)
        ground_vec = ground_vector / (norm(ground_vector) + 1e-10)
        
        # 计算残差
        residual = self.compute_residual(input_vec, ground_vec)
        hazard_level = HazardLevel.from_residual(residual)
        
        # 如果需要修正，应用残差修正公式
        corrected = input_vec.copy()
        correction_applied = False
        anchor_used = None
        
        if hazard_level in (HazardLevel.HIGH, HazardLevel.CRITICAL):
            # 使用公式: B = I - G + m * c²
            
            # 如果有置信度向量，使用它；否则使用默认值
            if confidence_vector is not None:
                c_squared = np.square(confidence_vector)
            else:
                c_squared = np.ones_like(input_vec) * 0.5
            
            # 残差修正
            corrected = input_vec - ground_vec + self.m * c_squared
            corrected = corrected / (norm(corrected) + 1e-10)
            correction_applied = True
            
            # 尝试投影到最近的知识锚点
            if self._anchors:
                anchor_used = self._project_to_nearest_anchor(corrected)
        
        return KunGuardResult(
            corrected_vector=corrected,
            residual=residual,
            hazard_level=hazard_level,
            anchor_used=anchor_used,
            correction_applied=correction_applied,
            metadata={
                'correction_factor': self.m,
                'anchors_count': len(self._anchors),
            },
        )

    def _project_to_nearest_anchor(self, vector: np.ndarray) -> str:
        """投影到最近的知识锚点"""
        best_anchor = None
        best_sim = -1.0
        
        for aid, anchor in self._anchors.items():
            sim = float(np.dot(vector, anchor.vector))
            if sim > best_sim:
                best_sim = sim
                best_anchor = aid
        
        return best_anchor or ""

    def correct_with_projection(
        self,
        input_vector: np.ndarray,
        ground_vector: np.ndarray,
    ) -> KunGuardResult:
        """
        带知识锚点投影的修正
        
        当残差超过阈值时，将输出投影到知识库中最相关的锚点方向
        """
        result = self.correct(input_vector, ground_vector)
        
        if result.needs_correction and self._anchors:
            # 找到最相关的锚点
            similarities = []
            for aid, anchor in self._anchors.items():
                sim = float(np.dot(result.corrected_vector, anchor.vector))
                similarities.append((aid, sim, anchor))
            
            # 选择相似度最高的锚点进行投影
            similarities.sort(key=lambda x: x[1], reverse=True)
            best_aid, best_sim, best_anchor = similarities[0]
            
            # 投影：将修正向量向锚点方向移动
            projected = (1 - best_sim) * result.corrected_vector + best_sim * best_anchor.vector
            projected = projected / (norm(projected) + 1e-10)
            
            return KunGuardResult(
                corrected_vector=projected,
                residual=result.residual * (1 - best_sim * 0.5),
                hazard_level=HazardLevel.MEDIUM if best_sim > 0.5 else result.hazard_level,
                anchor_used=best_aid,
                correction_applied=True,
                metadata={
                    'projection_anchor': best_aid,
                    'projection_similarity': best_sim,
                },
            )
        
        return result

    @property
    def anchors_count(self) -> int:
        """获取锚点数量"""
        return len(self._anchors)
