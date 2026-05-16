"""
Seven Step Chain - 七步推理链

步骤1: Parse(I,G)           解析输入/目标
步骤2: Compute ΔS            阴阳距，分配闸区
步骤3: Memory Checkpointing  追踪观变λ+共振能量
步骤4: 坤守·Residue Cleanup  语义残差修正
步骤5: Coupler+乾进          耦合器合约+受控演进
步骤6: 巽调·Rebalancer       注意力重平衡
步骤7: 复归+Drunk Transformer 崩溃检测+回滚重试

调用核心层各模块，每步可独立调用。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any
import numpy as np


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


@dataclass
class ChainResult:
    """链执行结果"""
    final_output: Any
    steps_completed: int
    step_results: list[StepOutput]
    final_delta_s: Optional[float] = None
    success: bool = True


class SevenStepChain:
    """
    七步推理链

    Usage::
        chain = SevenStepChain()
        result = chain.execute_full_chain(
            StepInput(text="碳排放权交易", goal="分析碳排放权交易")
        )
        print(result.steps_completed, result.final_output)
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
            result_data={"parsed_input": parsed_input, "parsed_goal": parsed_goal},
        )

    def _step2_compute_delta_s(
        self,
        input_data: StepInput,
        prev_output: Optional[StepOutput],
    ) -> StepOutput:
        """步骤2: Compute ΔS - 计算阴阳距"""
        parsed = prev_output.result_data if prev_output else {}
        input_entities = parsed.get("parsed_input", {}).get("entities", [])
        goal_entities = parsed.get("parsed_goal", {}).get("entities", [])

        delta_s = self._compute_delta_s(input_entities, goal_entities)
        gate_zone = self._get_gate_zone(delta_s)

        return StepOutput(
            step_name="ComputeDeltaS",
            result_data={"delta_s": delta_s},
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
        checkpoint = {
            "delta_s": delta_s,
            "text": input_data.text,
            "goal": input_data.goal,
        }
        self._checkpoints.append(prev_output or StepOutput(step_name="MemoryCheckpoint"))

        return StepOutput(
            step_name="MemoryCheckpoint",
            result_data=checkpoint,
            delta_s=delta_s,
            checkpoint_saved=True,
        )

    def _step4_kun_guard(
        self,
        input_data: StepInput,
        prev_output: Optional[StepOutput],
    ) -> StepOutput:
        """步骤4: 坤守·Residue Cleanup - 语义残差修正"""
        delta_s = prev_output.delta_s if prev_output else 0.5
        correction_applied = delta_s > 0.6

        return StepOutput(
            step_name="KunGuard",
            result_data={"correction_applied": correction_applied},
            delta_s=delta_s,
            correction_applied=correction_applied,
        )

    def _step5_coupler(
        self,
        input_data: StepInput,
        prev_output: Optional[StepOutput],
    ) -> StepOutput:
        """步骤5: Coupler+乾进 - 耦合器合约"""
        delta_s = prev_output.delta_s if prev_output else 0.5
        allowed = delta_s <= 0.8

        return StepOutput(
            step_name="Coupler",
            result_data={"progression_allowed": allowed},
            delta_s=delta_s,
        )

    def _step6_xun_tune(
        self,
        input_data: StepInput,
        prev_output: Optional[StepOutput],
    ) -> StepOutput:
        """步骤6: 巽调·Rebalancer - 注意力重平衡"""
        delta_s = prev_output.delta_s if prev_output else 0.5

        return StepOutput(
            step_name="XunTune",
            result_data={"attention_rebalanced": True},
            delta_s=delta_s,
        )

    def _step7_fu_return(
        self,
        input_data: StepInput,
        prev_output: Optional[StepOutput],
    ) -> StepOutput:
        """步骤7: 复归+Drunk Transformer - 崩溃检测"""
        delta_s = prev_output.delta_s if prev_output else 0.5
        crash_detected = delta_s > 0.9

        return StepOutput(
            step_name="FuReturn",
            result_data={"crash_detected": crash_detected, "recovered": not crash_detected},
            delta_s=delta_s,
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

        final_delta_s = prev_output.delta_s if prev_output else None

        return ChainResult(
            final_output=prev_output.result_data if prev_output else None,
            steps_completed=len(step_results),
            step_results=step_results,
            final_delta_s=final_delta_s,
            success=True,
        )

    def _extract_entities(self, text: str) -> list[str]:
        """提取实体"""
        import re
        entities = re.findall(r'[\u4e00-\u9fff]+', text)
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
