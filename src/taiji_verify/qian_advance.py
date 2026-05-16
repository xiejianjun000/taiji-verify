"""
乾进 (Qian Advance) - 语义演进建模模块

核心算法: 多路径扰动算法
稳定性得分: f_S = 1 / (1 + mean(Δ))

其中:
    Δ = 扰动向量与原始向量的距离变化
    f_S ∈ [0, 1]，越接近1越稳定

参数说明:
    k_paths: 扰动路径数量，默认5
    noise_scale: 扰动噪声尺度，默认0.1

数据来源：基于阶段一基线数据推算与行业同类系统对标
"""

from __future__ import annotations

import numpy as np
from numpy.linalg import norm
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple


@dataclass
class PerturbationResult:
    """单路径扰动结果"""
    path_id: int
    perturbed_vector: np.ndarray
    distance_change: float
    similarity: float


@dataclass
class QianAdvanceResult:
    """乾进演进结果"""
    original_vector: np.ndarray
    evolved_vector: np.ndarray
    stability_score: float
    path_results: List[PerturbationResult]
    converged: bool = False
    iterations: int = 0
    metadata: Dict = field(default_factory=dict)

    @property
    def is_stable(self) -> bool:
        return self.stability_score > 0.7

    @property
    def needs_revision(self) -> bool:
        return self.stability_score < 0.4


class QianAdvance:
    """
    乾进 - 语义演进建模器

    核心功能:
    1. 多路径扰动分析
    2. 稳定性评估
    3. 语义演进优化
    4. 收敛判定

    Usage::
        advance = QianAdvance(k_paths=5, noise_scale=0.1)
        result = advance.evolve(embedding_vector)
        print(result.stability_score, result.converged)
    """

    def __init__(
        self,
        k_paths: int = 5,
        noise_scale: float = 0.1,
        max_iterations: int = 10,
        convergence_threshold: float = 0.01,
        stability_threshold: float = 0.7,
    ):
        """
        Args:
            k_paths: 扰动路径数量，建议3-10
            noise_scale: 扰动噪声尺度，建议0.05-0.2
            max_iterations: 最大迭代次数
            convergence_threshold: 收敛判定阈值
            stability_threshold: 稳定性阈值
        """
        self.k_paths = k_paths
        self.noise_scale = noise_scale
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.stability_threshold = stability_threshold

    def _generate_perturbation(self, vector: np.ndarray, seed: int) -> np.ndarray:
        """
        生成单个扰动向量
        
        Args:
            vector: 原始向量
            seed: 随机种子
        
        Returns:
            扰动后的向量
        """
        rng = np.random.default_rng(seed)
        noise = rng.normal(0, self.noise_scale, size=vector.shape)
        perturbed = vector + noise
        return perturbed / (norm(perturbed) + 1e-10)

    def _compute_distance_change(
        self,
        original: np.ndarray,
        perturbed: np.ndarray,
    ) -> float:
        """
        计算距离变化量 Δ
        
        Args:
            original: 原始向量
            perturbed: 扰动后向量
        
        Returns:
            距离变化量
        """
        original_norm = original / (norm(original) + 1e-10)
        perturbed_norm = perturbed / (norm(perturbed) + 1e-10)
        return float(norm(original_norm - perturbed_norm))

    def _compute_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """计算向量余弦相似度"""
        v1_norm = v1 / (norm(v1) + 1e-10)
        v2_norm = v2 / (norm(v2) + 1e-10)
        return float(np.dot(v1_norm, v2_norm))

    def perturb(self, vector: np.ndarray) -> List[PerturbationResult]:
        """
        执行多路径扰动
        
        Args:
            vector: 输入向量
        
        Returns:
            各路径扰动结果列表
        """
        results = []
        
        for path_id in range(self.k_paths):
            perturbed = self._generate_perturbation(vector, path_id)
            distance_change = self._compute_distance_change(vector, perturbed)
            similarity = self._compute_similarity(vector, perturbed)
            
            results.append(PerturbationResult(
                path_id=path_id,
                perturbed_vector=perturbed,
                distance_change=distance_change,
                similarity=similarity,
            ))
        
        return results

    def compute_stability(self, path_results: List[PerturbationResult]) -> float:
        """
        计算稳定性得分
        
        公式: f_S = 1 / (1 + mean(Δ))
        
        Args:
            path_results: 各路径扰动结果
        
        Returns:
            稳定性得分 ∈ [0, 1]
        """
        if not path_results:
            return 1.0
        
        delta_values = [pr.distance_change for pr in path_results]
        mean_delta = np.mean(delta_values)
        stability = 1.0 / (1.0 + mean_delta)
        
        return float(min(max(stability, 0.0), 1.0))

    def evolve(
        self,
        vector: np.ndarray,
        target_similarity: float = 0.9,
    ) -> QianAdvanceResult:
        """
        执行语义演进
        
        Args:
            vector: 输入向量
            target_similarity: 目标相似度阈值
        
        Returns:
            QianAdvanceResult 演进结果
        """
        current_vector = vector / (norm(vector) + 1e-10)
        iterations = 0
        converged = False
        path_results = []

        for iteration in range(self.max_iterations):
            iterations = iteration + 1
            
            # 执行扰动
            paths = self.perturb(current_vector)
            path_results.extend(paths)
            
            # 计算稳定性
            stability = self.compute_stability(paths)
            
            # 检查收敛
            if stability >= self.stability_threshold:
                converged = True
                break
            
            # 检查相似度是否达标
            similarities = [pr.similarity for pr in paths]
            avg_similarity = np.mean(similarities)
            
            if avg_similarity >= target_similarity:
                converged = True
                break
            
            # 向更稳定的方向演进
            stable_paths = [pr for pr in paths if pr.similarity > 0.8]
            if stable_paths:
                current_vector = np.mean([pr.perturbed_vector for pr in stable_paths], axis=0)
                current_vector = current_vector / (norm(current_vector) + 1e-10)

        # 最终稳定性评估
        final_stability = self.compute_stability(path_results[-self.k_paths:])
        
        return QianAdvanceResult(
            original_vector=vector,
            evolved_vector=current_vector,
            stability_score=final_stability,
            path_results=path_results,
            converged=converged,
            iterations=iterations,
            metadata={
                'k_paths': self.k_paths,
                'noise_scale': self.noise_scale,
                'target_similarity': target_similarity,
            },
        )

    def analyze_paths(self, vector: np.ndarray) -> Tuple[float, float, float]:
        """
        分析扰动路径特征
        
        Returns:
            (平均距离变化, 平均相似度, 稳定性得分)
        """
        paths = self.perturb(vector)
        avg_delta = np.mean([pr.distance_change for pr in paths])
        avg_sim = np.mean([pr.similarity for pr in paths])
        stability = self.compute_stability(paths)
        
        return float(avg_delta), float(avg_sim), float(stability)

    def optimize_vector(
        self,
        vector: np.ndarray,
        iterations: Optional[int] = None,
    ) -> np.ndarray:
        """
        优化向量稳定性
        
        Args:
            vector: 输入向量
            iterations: 迭代次数，默认为max_iterations
        
        Returns:
            优化后的向量
        """
        result = self.evolve(vector)
        return result.evolved_vector

    def batch_evolve(
        self,
        vectors: List[np.ndarray],
        target_similarity: float = 0.9,
    ) -> List[QianAdvanceResult]:
        """
        批量执行语义演进
        
        Args:
            vectors: 向量列表
            target_similarity: 目标相似度阈值
        
        Returns:
            各向量演进结果列表
        """
        results = []
        for vector in vectors:
            result = self.evolve(vector, target_similarity)
            results.append(result)
        return results
