"""
观变 (Guan Observe) - 状态追踪模块

核心功能:
1. 状态向量时序追踪
2. 变化趋势分析
3. 异常检测
4. 状态快照与回放

数据来源：基于阶段一基线数据推算与行业同类系统对标
"""

from __future__ import annotations

import numpy as np
from numpy.linalg import norm
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from collections import deque


class ChangeType(str, Enum):
    """变化类型"""
    STABLE = "stable"           # 稳定
    GRADUAL = "gradual"         # 渐变
    ABRUPT = "abrupt"           # 突变
    ANOMALY = "anomaly"         # 异常


@dataclass
class StateSnapshot:
    """状态快照"""
    timestamp: float
    vector: np.ndarray
    similarity: float
    change_type: ChangeType
    metadata: Dict = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """趋势分析结果"""
    trend_direction: float      # 趋势方向，正数表示增加，负数表示减少
    volatility: float          # 波动率
    anomaly_score: float        # 异常分数
    change_type: ChangeType
    recent_snapshots: List[StateSnapshot]
    metadata: Dict = field(default_factory=dict)


@dataclass
class AnomalyEvent:
    """异常事件"""
    event_id: str
    timestamp: float
    snapshot: StateSnapshot
    severity: str               # low/middle/high/critical
    description: str
    metadata: Dict = field(default_factory=dict)


class GuanObserve:
    """
    观变 - 状态追踪器

    核心功能:
    1. 实时状态向量追踪
    2. 变化趋势分析
    3. 异常检测与告警
    4. 状态快照管理

    Usage::
        observer = GuanObserve(window_size=10)
        observer.track(vector1)
        observer.track(vector2)
        trend = observer.analyze_trend()
        print(trend.change_type)
    """

    def __init__(
        self,
        window_size: int = 10,
        abrupt_threshold: float = 0.3,
        anomaly_threshold: float = 0.8,
        similarity_threshold: float = 0.7,
    ):
        """
        Args:
            window_size: 滑动窗口大小
            abrupt_threshold: 突变检测阈值
            anomaly_threshold: 异常检测阈值
            similarity_threshold: 相似度阈值
        """
        self.window_size = window_size
        self.abrupt_threshold = abrupt_threshold
        self.anomaly_threshold = anomaly_threshold
        self.similarity_threshold = similarity_threshold
        
        self._history: deque[StateSnapshot] = deque(maxlen=window_size)
        self._anomaly_events: List[AnomalyEvent] = []
        self._callbacks: List[Callable[[AnomalyEvent], None]] = []
        self._reference_vector: Optional[np.ndarray] = None

    def set_reference(self, vector: np.ndarray):
        """设置参考向量"""
        self._reference_vector = vector / (norm(vector) + 1e-10)

    def _compute_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """计算余弦相似度"""
        v1_norm = v1 / (norm(v1) + 1e-10)
        v2_norm = v2 / (norm(v2) + 1e-10)
        return float(np.dot(v1_norm, v2_norm))

    def _detect_change_type(self, similarity: float, prev_similarity: float) -> ChangeType:
        """
        根据相似度变化检测变化类型
        
        Args:
            similarity: 当前相似度
            prev_similarity: 上一次相似度
        
        Returns:
            ChangeType 变化类型
        """
        diff = abs(similarity - prev_similarity)
        
        if similarity < self.similarity_threshold:
            return ChangeType.ANOMALY
        elif diff > self.abrupt_threshold:
            return ChangeType.ABRUPT
        elif diff > 0.05:
            return ChangeType.GRADUAL
        else:
            return ChangeType.STABLE

    def track(
        self,
        vector: np.ndarray,
        metadata: Optional[Dict] = None,
    ) -> StateSnapshot:
        """
        追踪状态向量
        
        Args:
            vector: 状态向量
            metadata: 附加元数据
        
        Returns:
            StateSnapshot 状态快照
        """
        # 计算与参考向量的相似度
        if self._reference_vector is not None:
            similarity = self._compute_similarity(vector, self._reference_vector)
        else:
            similarity = 1.0
        
        # 检测变化类型
        if self._history:
            prev_similarity = self._history[-1].similarity
            change_type = self._detect_change_type(similarity, prev_similarity)
        else:
            change_type = ChangeType.STABLE
        
        # 创建快照
        snapshot = StateSnapshot(
            timestamp=np.datetime64('now').astype(float),
            vector=vector.copy(),
            similarity=similarity,
            change_type=change_type,
            metadata=metadata or {},
        )
        
        # 添加到历史
        self._history.append(snapshot)
        
        # 检测异常并触发回调
        if change_type == ChangeType.ANOMALY:
            self._trigger_anomaly(snapshot)
        
        return snapshot

    def _trigger_anomaly(self, snapshot: StateSnapshot):
        """触发异常事件"""
        severity = self._determine_severity(snapshot.similarity)
        event = AnomalyEvent(
            event_id=f"anomaly_{len(self._anomaly_events) + 1}",
            timestamp=snapshot.timestamp,
            snapshot=snapshot,
            severity=severity,
            description=f"状态异常: 相似度={snapshot.similarity:.4f}",
            metadata=snapshot.metadata,
        )
        
        self._anomaly_events.append(event)
        
        # 触发所有回调
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception:
                pass

    def _determine_severity(self, similarity: float) -> str:
        """根据相似度确定异常严重程度"""
        if similarity < 0.3:
            return "critical"
        elif similarity < 0.5:
            return "high"
        elif similarity < 0.7:
            return "middle"
        else:
            return "low"

    def analyze_trend(self) -> TrendAnalysis:
        """
        分析状态变化趋势
        
        Returns:
            TrendAnalysis 趋势分析结果
        """
        if len(self._history) < 2:
            return TrendAnalysis(
                trend_direction=0.0,
                volatility=0.0,
                anomaly_score=0.0,
                change_type=ChangeType.STABLE,
                recent_snapshots=[],
                metadata={'error': 'insufficient_data'},
            )
        
        # 计算趋势方向
        similarities = [s.similarity for s in self._history]
        trend_direction = np.polyfit(range(len(similarities)), similarities, 1)[0]
        
        # 计算波动率
        volatility = float(np.std(similarities))
        
        # 计算异常分数
        anomaly_score = float(np.mean([1 - s.similarity for s in self._history]))
        
        # 确定变化类型
        latest_change = self._history[-1].change_type
        
        return TrendAnalysis(
            trend_direction=trend_direction,
            volatility=volatility,
            anomaly_score=anomaly_score,
            change_type=latest_change,
            recent_snapshots=list(self._history)[-5:],
            metadata={
                'window_size': len(self._history),
            },
        )

    def detect_anomalies(self, threshold: Optional[float] = None) -> List[AnomalyEvent]:
        """
        检测异常事件
        
        Args:
            threshold: 异常阈值，默认使用 anomaly_threshold
        
        Returns:
            异常事件列表
        """
        effective_threshold = threshold or self.anomaly_threshold
        return [
            event for event in self._anomaly_events
            if 1 - event.snapshot.similarity >= effective_threshold
        ]

    def get_snapshot_at(self, index: int) -> Optional[StateSnapshot]:
        """获取指定位置的快照"""
        if index < 0 or index >= len(self._history):
            return None
        return list(self._history)[index]

    def get_recent_snapshots(self, count: int = 5) -> List[StateSnapshot]:
        """获取最近的快照"""
        return list(self._history)[-count:]

    def replay(self) -> List[StateSnapshot]:
        """回放所有历史快照"""
        return list(self._history)

    def add_callback(self, callback: Callable[[AnomalyEvent], None]):
        """添加异常回调函数"""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[AnomalyEvent], None]):
        """移除异常回调函数"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def reset(self):
        """重置追踪器"""
        self._history.clear()
        self._anomaly_events.clear()

    @property
    def history_length(self) -> int:
        """获取历史记录长度"""
        return len(self._history)

    @property
    def anomaly_count(self) -> int:
        """获取异常事件数量"""
        return len(self._anomaly_events)

    @property
    def current_snapshot(self) -> Optional[StateSnapshot]:
        """获取当前快照"""
        return self._history[-1] if self._history else None
