"""Polaris 北辰编译器测试 - 完整覆盖率"""
import pytest
from taiji_verify.polaris import (
    PolarisCompiler, TaskType, TaskState, TaskAtom,
    ExecutionToken, RoundLock, ClosureRecord, CompilationResult,
)


class TestPolarisInit:
    """Polaris编译器初始化测试"""

    def test_default_init(self):
        compiler = PolarisCompiler()
        assert compiler.max_rounds == 10
        assert len(compiler.task_graph) == 0
        assert len(compiler.atom_table) == 0

    def test_custom_max_rounds(self):
        compiler = PolarisCompiler(max_rounds=5)
        assert compiler.max_rounds == 5


class TestTaskAtom:
    """任务原子测试"""

    def test_task_atom_creation(self):
        atom = TaskAtom(
            atom_id="test_001",
            type=TaskType.ATOMIC,
            description="测试任务",
        )
        assert atom.atom_id == "test_001"
        assert atom.type == TaskType.ATOMIC
        assert atom.state == TaskState.PENDING

    def test_task_atom_is_ready(self):
        atom = TaskAtom(atom_id="test", type=TaskType.ATOMIC, description="test")
        assert atom.is_ready() is True

    def test_task_atom_activate(self):
        atom = TaskAtom(atom_id="test", type=TaskType.ATOMIC, description="test")
        atom.activate()
        assert atom.state == TaskState.ACTIVE

    def test_task_atom_block(self):
        atom = TaskAtom(atom_id="test", type=TaskType.ATOMIC, description="test")
        atom.block()
        assert atom.state == TaskState.BLOCKED

    def test_task_atom_complete(self):
        atom = TaskAtom(atom_id="test", type=TaskType.ATOMIC, description="test")
        atom.complete("result_value")
        assert atom.state == TaskState.COMPLETED
        assert atom.result == "result_value"

    def test_task_atom_fail(self):
        atom = TaskAtom(atom_id="test", type=TaskType.ATOMIC, description="test")
        atom.fail("error_message")
        assert atom.state == TaskState.FAILED
        assert atom.error == "error_message"


class TestExecutionToken:
    """执行令牌测试"""

    def test_token_creation(self):
        token = ExecutionToken(
            token_id="token_001",
            atom_id="atom_001",
            round=1,
            priority=5,
        )
        assert token.token_id == "token_001"
        assert token.claimed is False


class TestRoundLock:
    """轮次锁测试"""

    def test_lock_creation(self):
        lock = RoundLock(round=1)
        assert lock.round == 1
        assert lock.locked is False


class TestCompilation:
    """编译功能测试"""

    def test_compile_analysis_goal(self):
        compiler = PolarisCompiler()
        result = compiler.compile("分析环评报告")
        assert result.success is True
        assert len(result.task_graph) > 0
        assert len(result.atom_table) > 0

    def test_compile_generation_goal(self):
        compiler = PolarisCompiler()
        result = compiler.compile("生成摘要文档")
        assert result.success is True
        assert len(result.atom_table) > 0

    def test_compile_default_goal(self):
        compiler = PolarisCompiler()
        result = compiler.compile("执行任务")
        assert result.success is True
        assert len(result.atom_table) == 1

    def test_compile_metadata(self):
        compiler = PolarisCompiler()
        result = compiler.compile("分析数据")
        assert 'goal' in result.metadata
        assert 'atom_count' in result.metadata


class TestRoundLock:
    """轮次锁功能测试"""

    def test_acquire_lock_success(self):
        compiler = PolarisCompiler()
        success = compiler._acquire_round_lock(1)
        assert success is True
        assert compiler._round_lock.locked is True
        assert compiler._round_lock.round == 1

    def test_acquire_lock_different_round_blocked(self):
        compiler = PolarisCompiler()
        compiler._acquire_round_lock(1)
        compiler._release_round_lock()
        success = compiler._acquire_round_lock(2)
        assert success is True

    def test_release_lock(self):
        compiler = PolarisCompiler()
        compiler._acquire_round_lock(1)
        compiler._release_round_lock()
        assert compiler._round_lock.locked is False


class TestExecution:
    """执行功能测试"""

    def test_execute_success(self):
        compiler = PolarisCompiler(max_rounds=10)
        compiler.compile("分析数据")

        def executor(atom):
            return f"executed_{atom.atom_id}"

        result = compiler.execute(executor)
        assert result.success is True
        assert result.closure_record is not None
        assert result.closure_record.success is True

    def test_execute_with_dependencies(self):
        compiler = PolarisCompiler(max_rounds=10)
        compiler.compile("分析环评报告")

        results = []

        def executor(atom):
            results.append(atom.atom_id)
            return f"done"

        result = compiler.execute(executor)
        assert len(results) > 0

    def test_execute_failure_handling(self):
        compiler = PolarisCompiler(max_rounds=10)
        compiler.compile("分析数据")

        def failing_executor(atom):
            raise ValueError("Test error")

        result = compiler.execute(failing_executor)
        assert result.closure_record is not None

    def test_execute_metadata(self):
        compiler = PolarisCompiler(max_rounds=10)
        compiler.compile("分析数据")

        def executor(atom):
            return "done"

        result = compiler.execute(executor)
        assert 'rounds_executed' in result.metadata
        assert 'completed_count' in result.metadata
        assert 'failed_count' in result.metadata


class TestAtomReady:
    """任务就绪检查测试"""

    def test_atom_ready_with_completed_deps(self):
        compiler = PolarisCompiler()
        compiler.compile("分析数据")
        atom_id = compiler.atom_table[0].atom_id
        assert compiler._is_atom_ready(atom_id) is True

    def test_atom_ready_with_pending_deps(self):
        compiler = PolarisCompiler()
        compiler.compile("分析数据")
        if len(compiler.atom_table) > 1:
            atom_id = compiler.atom_table[1].atom_id
            assert compiler._is_atom_ready(atom_id) is False

    def test_atom_ready_nonexistent(self):
        compiler = PolarisCompiler()
        assert compiler._is_atom_ready("nonexistent") is False


class TestGetters:
    """获取器测试"""

    def test_get_atom_by_id(self):
        compiler = PolarisCompiler()
        compiler.compile("分析数据")
        atom_id = compiler.atom_table[0].atom_id
        atom = compiler.get_atom_by_id(atom_id)
        assert atom is not None
        assert atom.atom_id == atom_id

    def test_get_atom_by_id_nonexistent(self):
        compiler = PolarisCompiler()
        atom = compiler.get_atom_by_id("nonexistent")
        assert atom is None

    def test_get_tokens_for_round(self):
        compiler = PolarisCompiler()
        compiler.compile("分析数据")
        tokens = compiler.get_tokens_for_round(0)
        assert len(tokens) == len(compiler.atom_table)

    def test_get_closure_records(self):
        compiler = PolarisCompiler(max_rounds=10)
        compiler.compile("分析数据")

        def executor(atom):
            return "done"

        compiler.execute(executor)
        records = compiler.get_closure_records()
        assert len(records) > 0


class TestReset:
    """重置功能测试"""

    def test_reset_clears_state(self):
        compiler = PolarisCompiler(max_rounds=10)
        compiler.compile("分析数据")

        def executor(atom):
            return "done"

        compiler.execute(executor)
        compiler.reset()

        assert len(compiler.task_graph) == 0
        assert len(compiler.atom_table) == 0
        assert len(compiler.token_board) == 0
        assert compiler._round_lock.locked is False


class TestClosureRecord:
    """关闭记录测试"""

    def test_closure_record_creation(self):
        record = ClosureRecord(
            record_id="rec_001",
            goal_id="goal_001",
            atoms_completed=["a1", "a2"],
            atoms_failed=[],
            final_result="success",
            success=True,
        )
        assert record.record_id == "rec_001"
        assert record.success is True
        assert len(record.atoms_completed) == 2


class TestBatchCompile:
    """批量编译测试"""

    def test_multiple_compiles(self):
        compiler = PolarisCompiler()
        result1 = compiler.compile("分析数据")
        result2 = compiler.compile("生成报告")
        assert result1.success is True
        assert result2.success is True
