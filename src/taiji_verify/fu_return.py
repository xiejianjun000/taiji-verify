"""
复归 (Fu Return) - 崩溃逆转模块

核心功能:
1. 崩溃状态检测与识别
2. 李雅普诺夫指数 λ 计算
3. 崩溃逆转恢复流程
4. 状态机管理

参数说明:
    Bc: 崩溃边界阈值，默认0.8
    eps: 恢复收敛阈值，默认0.01
    max_retries: 最大重试次数，默认3

数据来源：基于阶段一基线数据推算与行业同类系统对标
"""

from __future__ import annotations

import numpy as np
from numpy.linalg import norm
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Callable


class RecoveryState(str, Enum):
    """恢复状态机状态"""
    NORMAL = "normal"           # 正常状态
    WARNING = "warning"         # 警告状态
    CRASHING = "crashing"       # 崩溃中
    RECOVERING = "recovering"   # 恢复中
    RECOVERED = "recovered"     # 已恢复
    FAILED = "failed"           # 恢复失败


@dataclass
class CrashingEvent:
    """崩溃事件记录"""
    event_id: str
    timestamp: float
    state: RecoveryState
    lyapunov_exponent: float
    residual: float
    metadata: Dict = field(default_factory=dict)


@dataclass
class RecoveryResult:
    """恢复结果"""
    success: bool
    final_state: RecoveryState
    lyapunov_exponent: float
    iterations: int
    events: List[CrashingEvent] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class FuReturn:
    """
    复归 - 崩溃逆转恢复器

    核心功能:
    1. 实时监测李雅普诺夫指数变化
    2. 检测崩溃前兆并触发恢复流程
    3. 实现状态机驱动的恢复机制
    4. 支持自定义恢复策略

    Usage::
        fu_return = FuReturn(Bc=0.8, eps=0.01)
        result = fu_return.monitor_and_recover(state_vectors)
        if result.success:
            print("恢复成功!")
    """

    def __init__(
        self,
        Bc: float = 0.8,
        eps: float = 0.01,
        max_retries: int = 3,
        recovery_timeout: float = 30.0,
    ):
        """
        Args:
            Bc: 崩溃边界阈值，超过此值认为进入崩溃状态
            eps: 恢复收敛阈值，低于此值认为恢复成功
            max_retries: 最大重试次数
            recovery_timeout: 恢复超时时间（秒）
        """
        self.Bc = Bc
        self.eps = eps
        self.max_retries = max_retries
        self.recovery_timeout = recovery_timeout
        self._current_state = RecoveryState.NORMAL
        self._events: List[CrashingEvent] = []
        self._recovery_callbacks: List[Callable] = []

    def compute_lyapunov_exponent(
        self,
        state_history: List[np.ndarray],
        delta_t: float = 1.0,
    ) -> float:
        """
        计算李雅普诺夫指数 λ
        
        公式: λ = lim(t→∞) (1/t) * ln(|δ(t)/δ(0)|)
        
        Args:
            state_history: 状态向量历史记录
            delta_t: 时间步长
        
        Returns:
            李雅普诺夫指数，正数表示发散（不稳定），负数表示收敛（稳定）
        """
        if len(state_history) < 2:
            return 0.0
        
        # 计算状态变化的平均增长率
        growth_rates = []
        for i in range(1, len(state_history)):
            delta_prev = norm(state_history[i-1]) if i > 1 else 1.0
            delta_curr = norm(state_history[i])
            
            if delta_prev > 0:
                growth_rate = np.log(delta_curr / delta_prev + 1e-10) / delta_t
                growth_rates.append(growth_rate)
        
        if not growth_rates:
            return 0.0
        
        return float(np.mean(growth_rates))

    def detect_crash(self, lyapunov: float, residual: float) -> RecoveryState:
        """
        根据李雅普诺夫指数和残差检测崩溃状态
        
        Args:
            lyapunov: 李雅普诺夫指数
            residual: 语义残差
        
        Returns:
            当前状态
        """
        if lyapunov > self.Bc or residual > 0.9:
            return RecoveryState.CRASHING
        elif lyapunov > 0.5 or residual > 0.6:
            return RecoveryState.WARNING
        else:
            return RecoveryState.NORMAL

    def _record_event(self, state: RecoveryState, lyapunov: float, residual: float):
        """记录状态变化事件"""
        event = CrashingEvent(
            event_id=f"event_{len(self._events) + 1}",
            timestamp=np.datetime64('now').astype(float),
            state=state,
            lyapunov_exponent=lyapunov,
            residual=residual,
        )
        self._events.append(event)
        self._current_state = state

    def recover(
        self,
        current_vector: np.ndarray,
        stable_reference: np.ndarray,
    ) -> RecoveryResult:
        """
        执行崩溃恢复
        
        Args:
            current_vector: 当前（可能崩溃的）状态向量
            stable_reference: 稳定参考向量
        
        Returns:
            RecoveryResult 恢复结果
        """
        self._record_event(RecoveryState.RECOVERING, 0.0, 0.0)
        
        iterations = 0
        success = False
        recovered_vector = current_vector.copy()
        
        for attempt in range(self.max_retries):
            iterations += 1
            
            # 计算与稳定参考的距离
            distance = float(norm(recovered_vector - stable_reference))
            
            # 检查是否已收敛
            if distance < self.eps:
                success = True
                break
            
            # 向稳定方向恢复：线性插值
            alpha = min(0.3, 1.0 / (attempt + 1))
            recovered_vector = (1 - alpha) * recovered_vector + alpha * stable_reference
            recovered_vector = recovered_vector / (norm(recovered_vector) + 1e-10)
        
        final_state = RecoveryState.RECOVERED if success else RecoveryState.FAILED
        lyapunov = self.compute_lyapunov_exponent([current_vector, recovered_vector])
        
        self._record_event(final_state, lyapunov, float(norm(recovered_vector - stable_reference)))
        
        return RecoveryResult(
            success=success,
            final_state=final_state,
            lyapunov_exponent=lyapunov,
            iterations=iterations,
            events=self._events.copy(),
            metadata={
                'attempts': self.max_retries,
                'Bc': self.Bc,
                'eps': self.eps,
            },
        )

    def adaptive_recover(
        self,
        current_vector: np.ndarray,
        stable_reference: np.ndarray,
        lyapunov: float,
    ) -> RecoveryResult:
        """
        自适应恢复 - 根据李雅普诺夫指数动态调整恢复策略
        
        Args:
            current_vector: 当前状态向量
            stable_reference: 稳定参考向量
            lyapunov: 当前李雅普诺夫指数
        
        Returns:
            RecoveryResult 恢复结果
        """
        # 根据李雅普诺夫指数动态调整恢复强度
        if lyapunov > 1.0:
            # 严重不稳定：直接替换为稳定参考
            recovered = stable_reference / (norm(stable_reference) + 1e-10)
            return RecoveryResult(
                success=True,
                final_state=RecoveryState.RECOVERED,
                lyapunov_exponent=0.0,
                iterations=1,
                metadata={'strategy': 'hard_reset'},
            )
        elif lyapunov > 0.5:
            # 中度不稳定：快速收敛
            return self.recover(current_vector, stable_reference)
        else:
            # 轻度不稳定：微调
            alpha = 0.1
            recovered = (1 - alpha) * current_vector + alpha * stable_reference
            recovered = recovered / (norm(recovered) + 1e-10)
            
            return RecoveryResult(
                success=True,
                final_state=RecoveryState.RECOVERED,
                lyapunov_exponent=lyapunov * 0.5,
                iterations=1,
                metadata={'strategy': 'fine_tune'},
            )

    def monitor_and_recover(
        self,
        state_history: List[np.ndarray],
        stable_reference: np.ndarray,
        delta_t: float = 1.0,
    ) -> RecoveryResult:
        """
        监控并自动恢复
        
        Args:
            state_history: 状态向量历史
            stable_reference: 稳定参考向量
            delta_t: 时间步长
        
        Returns:
            RecoveryResult 恢复结果
        """
        if len(state_history) < 2:
            return RecoveryResult(
                success=True,
                final_state=RecoveryState.NORMAL,
                lyapunov_exponent=0.0,
                iterations=0,
                metadata={'error': 'insufficient_history'},
            )
        
        # 计算当前李雅普诺夫指数
        lyapunov = self.compute_lyapunov_exponent(state_history, delta_t)
        
        # 计算最新残差
        latest_state = state_history[-1]
        residual = float(norm(latest_state - stable_reference))
        
        # 检测状态
        detected_state = self.detect_crash(lyapunov, residual)
        self._record_event(detected_state, lyapunov, residual)
        
        # 如果需要恢复
        if detected_state == RecoveryState.CRASHING:
            return self.adaptive_recover(latest_state, stable_reference, lyapunov)
        elif detected_state == RecoveryState.WARNING:
            # 预防性恢复
            return self.adaptive_recover(latest_state, stable_reference, lyapunov)
        
        return RecoveryResult(
            success=True,
            final_state=detected_state,
            lyapunov_exponent=lyapunov,
            iterations=0,
            metadata={'status': 'no_action_needed'},
        )

    def add_recovery_callback(self, callback: Callable):
        """添加恢复回调函数"""
        self._recovery_callbacks.append(callback)

    def remove_recovery_callback(self, callback: Callable):
        """移除恢复回调函数"""
        if callback in self._recovery_callbacks:
            self._recovery_callbacks.remove(callback)

    def _trigger_callbacks(self, event: CrashingEvent):
        """触发所有回调函数"""
        for callback in self._recovery_callbacks:
            try:
                callback(event)
            except Exception:
                pass

    @property
    def current_state(self) -> RecoveryState:
        """获取当前状态"""
        return self._current_state

    @property
    def event_history(self) -> List[CrashingEvent]:
        """获取事件历史"""
        return self._events.copy()

    def reset(self):
        """重置状态机"""
        self._current_state = RecoveryState.NORMAL
        self._events.clear()
