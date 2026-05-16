"""
Seven Step Chain Tests
"""

import pytest
from taiji_verify.reasoning.seven_step_chain import (
    SevenStepChain, StepInput, StepOutput, ChainConfig, ChainResult
)


class TestSevenStepChain:
    """七步推理链测试"""

    def test_chain_initialization(self):
        """测试链初始化"""
        chain = SevenStepChain()
        assert chain.current_step == 0
        assert len(chain.steps) == 7

    def test_step1_parse(self):
        """测试步骤1解析"""
        chain = SevenStepChain()
        input_data = StepInput(
            text="分析环境保护法的实施效果",
            goal="评估环境保护法的实施效果"
        )
        output = chain.execute_step(1, input_data)
        assert output.step_name == "Parse"
        assert output.result_data is not None

    def test_step2_compute_delta_s(self):
        """测试步骤2计算ΔS"""
        chain = SevenStepChain()
        input_data = StepInput(text="输出文本", goal="标准答案")
        prev_output = StepOutput(
            step_name="Parse",
            result_data={"parsed_input": {"entities": ["环保"]}, "parsed_goal": {"entities": ["环保"]}}
        )
        output = chain.execute_step(2, input_data, prev_output)
        assert output.step_name == "ComputeDeltaS"
        assert output.delta_s is not None
        assert output.gate_zone is not None

    def test_step3_memory_checkpoint(self):
        """测试步骤3记忆检查点"""
        chain = SevenStepChain()
        output = chain.execute_step(3, StepInput(text="", goal=""), prev_output=StepOutput(
            step_name="ComputeDeltaS",
            delta_s=0.5,
            gate_zone="RISK"
        ))
        assert output.checkpoint_saved is True

    def test_full_chain_execution(self):
        """测试完整链执行"""
        chain = SevenStepChain()
        input_data = StepInput(
            text="碳排放权交易平台应当建立",
            goal="碳排放权交易平台应当建立完善的监管机制"
        )
        result = chain.execute_full_chain(input_data)
        assert result.final_output is not None
        assert result.steps_completed == 7

    def test_chain_config(self):
        """测试链配置"""
        config = ChainConfig(max_retries=5, checkpoint_enabled=True)
        chain = SevenStepChain(config)
        assert chain.config.max_retries == 5
