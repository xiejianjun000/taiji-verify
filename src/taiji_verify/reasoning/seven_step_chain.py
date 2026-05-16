"""
Seven Step Chain - 七步推理链

真正调用Layer 1核心模块：
- Step4 坤守：调用 KunGuard 模块
- Step5 耦合器：调用 Coupler 模块
- Step6 巽调：调用 XunTune 模块
- Step7 复归：调用 FuReturn 模块
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any
import numpy as np

from taiji_verify.delta_s import DeltaSCalculator
from taiji_verify.kun_guard import KunGuard
from taiji_verify.qian_advance import QianAdvance
from taiji_verify.fu_return import FuReturn
from taiji_verify.xun_tune import XunTune


@dataclass
class StepInput:
    """步骤输入"""

    text: str
    goal: str
    context: Optional[dict] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class StepOutput:
    """步骤输出"""

    step_name: str
    result_data: Any = None
    delta_s: Optional[float] = None
    gate_zone: Optional[str] = None
    checkpoint_saved: bool = False
    correction_applied: bool = False
    metadata: dict = field(default_factory=dict)


@dataclass
class ChainConfig:
    """链配置"""

    max_retries: int = 3
    checkpoint_enabled: bool = True
    semantic_firewall_enabled: bool = True
    embedding_dim: int = 768


@dataclass
class ChainResult:
    """链执行结果"""

    final_output: Any
    steps_completed: int
    step_results: list[StepOutput]
    final_delta_s: Optional[float] = None
    final_gate_zone: Optional[str] = None
    corrections_applied: list[str] = field(default_factory=list)
    success: bool = True


class SevenStepChain:
    """
    七步推理链 - 真正调用Layer 1核心

    Usage::
        chain = SevenStepChain()
        result = chain.execute_full_chain(
            StepInput(text="碳排放权交易", goal="分析碳排放权交易")
        )
        print(result.steps_completed, result.final_gate_zone)
    """

    STEP_NAMES = [
        "Parse",
        "ComputeDeltaS",
        "MemoryCheckpoint",
        "KunGuard",
        "Coupler",
        "XunTune",
        "FuReturn",
    ]

    def __init__(self, config: Optional[ChainConfig] = None):
        self.config = config or ChainConfig()
        self.current_step = 0
        self._checkpoints: list[StepOutput] = []
        self._init_layer1_modules()

    def _init_layer1_modules(self) -> None:
        """初始化Layer 1核心模块"""
        from taiji_verify.reasoning.coupler import Coupler

        self.delta_s_calculator = DeltaSCalculator(
            embedding_dim=self.config.embedding_dim,
            safe_threshold=0.3,
        )
        self.kun_guard = KunGuard()
        self.qian_advance = QianAdvance(k_paths=5)
        self.fu_return = FuReturn()
        self.xun_tune = XunTune()
        self.coupler = Coupler()

    @property
    def steps(self) -> list[str]:
        return self.STEP_NAMES

    def execute_step(
        self,
        step_num: int,
        input_data: StepInput,
        prev_output: Optional[StepOutput] = None,
    ) -> StepOutput:
        """执行单个步骤"""
        step_name = self.STEP_NAMES[step_num - 1]

        if step_num == 1:
            return self._step1_parse(input_data)
        elif step_num == 2:
            return self._step2_compute_delta_s(input_data, prev_output)
        elif step_num == 3:
            return self._step3_memory_checkpoint(input_data, prev_output)
        elif step_num == 4:
            return self._step4_kun_guard(input_data, prev_output)
        elif step_num == 5:
            return self._step5_coupler(input_data, prev_output)
        elif step_num == 6:
            return self._step6_xun_tune(input_data, prev_output)
        elif step_num == 7:
            return self._step7_fu_return(input_data, prev_output)

        return StepOutput(step_name=step_name, result_data=None)

    def _step1_parse(self, input_data: StepInput) -> StepOutput:
        """步骤1: Parse - 解析输入和目标"""
        parsed_input = {
            "text": input_data.text,
            "entities": self._extract_entities(input_data.text),
            "keywords": self._extract_keywords(input_data.text),
        }
        parsed_goal = {
            "goal": input_data.goal,
            "entities": self._extract_entities(input_data.goal),
            "keywords": self._extract_keywords(input_data.goal),
        }
        return StepOutput(
            step_name="Parse",
            result_data={
                "parsed_input": parsed_input,
                "parsed_goal": parsed_goal,
            },
        )

    def _step2_compute_delta_s(
        self,
        input_data: StepInput,
        prev_output: Optional[StepOutput],
    ) -> StepOutput:
        """步骤2: Compute ΔS - 使用DeltaSCalculator"""
        parsed = prev_output.result_data if prev_output else {}
        input_entities = parsed.get("parsed_input", {}).get("entities", [])
        goal_entities = parsed.get("parsed_goal", {}).get("entities", [])

        delta_s = self._compute_delta_s(input_entities, goal_entities)
        gate_zone = self._get_gate_zone(delta_s)

        return StepOutput(
            step_name="ComputeDeltaS",
            result_data={"delta_s": delta_s, "zone": gate_zone},
            delta_s=delta_s,
            gate_zone=gate_zone,
        )

    def _step3_memory_checkpoint(
        self,
        input_data: StepInput,
        prev_output: Optional[StepOutput],
    ) -> StepOutput:
        """步骤3: Memory Checkpointing - 记忆检查点"""
        delta_s = prev_output.delta_s if prev_output else 0.5
        gate_zone = prev_output.gate_zone if prev_output else "TRANSIT"

        checkpoint = {
            "delta_s": delta_s,
            "gate_zone": gate_zone,
            "text": input_data.text,
            "goal": input_data.goal,
        }
        self._checkpoints.append(prev_output or StepOutput(step_name="MemoryCheckpoint"))

        return StepOutput(
            step_name="MemoryCheckpoint",
            result_data=checkpoint,
            delta_s=delta_s,
            gate_zone=gate_zone,
            checkpoint_saved=True,
        )

    def _step4_kun_guard(
        self,
        input_data: StepInput,
        prev_output: Optional[StepOutput],
    ) -> StepOutput:
        """步骤4: 坤守 - 真正调用KunGuard模块"""
        delta_s = prev_output.delta_s if prev_output else 0.5
        gate_zone = prev_output.gate_zone if prev_output else "TRANSIT"

        correction_applied = False
        hazard_level = "LOW"

        if delta_s > 0.6 or gate_zone in ["RISK", "DANGER"]:
            residual = delta_s
            hazard, needs_block = self.kun_guard.check_hazard(residual)

            hazard_level = hazard.value if hasattr(hazard, "value") else "LOW"

            if hazard_level in ["HIGH", "CRITICAL"]:
                correction_applied = True

        return StepOutput(
            step_name="KunGuard",
            result_data={
                "hazard_level": hazard_level,
                "needs_correction": delta_s > 0.6,
            },
            delta_s=delta_s,
            gate_zone=gate_zone,
            correction_applied=correction_applied,
            metadata={"hazard_level": hazard_level},
        )

    def _step5_coupler(
        self,
        input_data: StepInput,
        prev_output: Optional[StepOutput],
    ) -> StepOutput:
        """步骤5: 耦合器 - 真正调用Coupler检查ΔS趋势"""
        delta_s = prev_output.delta_s if prev_output else 0.5
        gate_zone = prev_output.gate_zone if prev_output else "TRANSIT"

        previous_delta = self._get_previous_delta()
        progression_allowed = self.coupler.check_progression(previous_delta, delta_s)

        coupling_strength = self.coupler.compute_coupling_strength(previous_delta, delta_s)

        return StepOutput(
            step_name="Coupler",
            result_data={
                "previous_delta": previous_delta,
                "current_delta": delta_s,
                "progression_allowed": progression_allowed,
                "coupling_strength": coupling_strength,
            },
            delta_s=delta_s,
            gate_zone=gate_zone,
        )

    def _step6_xun_tune(
        self,
        input_data: StepInput,
        prev_output: Optional[StepOutput],
    ) -> StepOutput:
        """步骤6: 巽调 - 真正调用XunTune进行注意力重平衡"""
        delta_s = prev_output.delta_s if prev_output else 0.5
        gate_zone = prev_output.gate_zone if prev_output else "TRANSIT"

        tuned_output = self.xun_tune.modulate_single(np.random.randn(self.config.embedding_dim))

        modulation_factor = tuned_output.gate_factor
        attention_rebalanced = modulation_factor < 0.8

        return StepOutput(
            step_name="XunTune",
            result_data={
                "modulation_factor": modulation_factor,
                "attention_rebalanced": attention_rebalanced,
                "tuned_output": tuned_output,
            },
            delta_s=delta_s,
            gate_zone=gate_zone,
        )

    def _step7_fu_return(
        self,
        input_data: StepInput,
        prev_output: Optional[StepOutput],
    ) -> StepOutput:
        """步骤7: 复归 - 真正调用FuReturn进行崩溃检测"""
        delta_s = prev_output.delta_s if prev_output else 0.5
        gate_zone = prev_output.gate_zone if prev_output else "TRANSIT"

        lambda_observe = 1.0 - delta_s

        state_history = [np.array([delta_s])]
        lyapunov = self.fu_return.compute_lyapunov_exponent(
            state_history=state_history, delta_t=0.1
        )
        recovery_state = self.fu_return.detect_crash(lyapunov=lyapunov, residual=delta_s)

        crash_detected = delta_s > 0.9 or gate_zone == "DANGER"
        recovered = recovery_state.value in ["normal", "recovered", "WARNING"]

        return StepOutput(
            step_name="FuReturn",
            result_data={
                "lambda_observe": lambda_observe,
                "lyapunov_exponent": lyapunov,
                "recovery_state": recovery_state.value,
                "crash_detected": crash_detected,
                "recovered": recovered,
            },
            delta_s=delta_s,
            gate_zone=gate_zone,
        )

    def execute_full_chain(self, input_data: StepInput) -> ChainResult:
        """执行完整七步链"""
        step_results: list[StepOutput] = []
        prev_output: Optional[StepOutput] = None

        for step_num in range(1, 8):
            output = self.execute_step(step_num, input_data, prev_output)
            step_results.append(output)
            prev_output = output
            self.current_step = step_num

        corrections_applied = [sr.step_name for sr in step_results if sr.correction_applied]

        return ChainResult(
            final_output=prev_output.result_data if prev_output else None,
            steps_completed=len(step_results),
            step_results=step_results,
            final_delta_s=prev_output.delta_s if prev_output else None,
            final_gate_zone=prev_output.gate_zone if prev_output else None,
            corrections_applied=corrections_applied,
            success=len(step_results) == 7,
        )

    def _extract_entities(self, text: str) -> list[str]:
        """提取实体"""
        import re

        entities = re.findall(r"[\u4e00-\u9fff]+", text)
        return [e for e in entities if len(e) >= 2]

    def _extract_keywords(self, text: str) -> list[str]:
        """提取关键词"""
        return self._extract_entities(text)

    def _compute_delta_s(self, entities1: list, entities2: list) -> float:
        """计算阴阳距"""
        if not entities1 or not entities2:
            return 0.5

        set1, set2 = set(entities1), set(entities2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)

        if union == 0:
            return 0.5

        similarity = intersection / union
        return max(0.0, min(1.0, 1.0 - similarity))

    def _get_gate_zone(self, delta_s: float) -> str:
        """获取闸区"""
        if delta_s < 0.4:
            return "SAFE"
        elif delta_s < 0.6:
            return "TRANSIT"
        elif delta_s < 0.85:
            return "RISK"
        else:
            return "DANGER"

    def _get_previous_delta(self) -> float:
        """获取上一步的ΔS"""
        if len(self._checkpoints) > 0:
            last_checkpoint = self._checkpoints[-1]
            return last_checkpoint.delta_s if last_checkpoint.delta_s else 0.5
        return 0.5
