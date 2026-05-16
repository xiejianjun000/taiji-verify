"""
北辰编译器 (Polaris Compiler) - 目标编译器模块

执行管道阶段:
1. GOAL_COMPILATION - 目标编译
2. TASK_GRAPH - 任务图构建
3. ATOM_TABLE - 原子表管理
4. EXECUTION_TOKEN_BOARD - 执行令牌板
5. ROUND_LOCK - 轮次锁
6. CLOSURE_RECORD - 关闭记录

数据来源：基于阶段一基线数据推算与行业同类系统对标
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any, Callable, Union
import uuid


class TaskState(str, Enum):
    """任务状态"""
    PENDING = "pending"       # 等待中
    ACTIVE = "active"         # 执行中
    BLOCKED = "blocked"       # 阻塞中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败


class TaskType(str, Enum):
    """任务类型"""
    ATOMIC = "atomic"         # 原子任务
    COMPOSITE = "composite"   # 复合任务
    CONDITIONAL = "conditional" # 条件任务


@dataclass
class TaskAtom:
    """任务原子"""
    atom_id: str
    type: TaskType
    description: str
    state: TaskState = TaskState.PENDING
    dependencies: List[str] = field(default_factory=list)
    result: Any = None
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def is_ready(self) -> bool:
        """检查任务是否就绪（所有依赖已完成）"""
        return self.state == TaskState.PENDING
    
    def activate(self):
        """激活任务"""
        self.state = TaskState.ACTIVE
    
    def block(self):
        """阻塞任务"""
        self.state = TaskState.BLOCKED
    
    def complete(self, result: Any):
        """完成任务"""
        self.state = TaskState.COMPLETED
        self.result = result
    
    def fail(self, error: str):
        """任务失败"""
        self.state = TaskState.FAILED
        self.error = error


@dataclass
class ExecutionToken:
    """执行令牌"""
    token_id: str
    atom_id: str
    round: int
    priority: int = 0
    timestamp: float = 0.0
    claimed: bool = False


@dataclass
class RoundLock:
    """轮次锁"""
    round: int
    locked: bool = False
    owner: Optional[str] = None
    timestamp: float = 0.0


@dataclass
class ClosureRecord:
    """关闭记录"""
    record_id: str
    goal_id: str
    atoms_completed: List[str]
    atoms_failed: List[str]
    final_result: Any
    success: bool
    timestamp: float = 0.0


@dataclass
class CompilationResult:
    """编译结果"""
    success: bool
    task_graph: Dict[str, TaskAtom]
    atom_table: List[TaskAtom]
    closure_record: Optional[ClosureRecord] = None
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class PolarisCompiler:
    """
    北辰编译器 - 目标编译器
    
    核心功能:
    1. 目标编译 - 将自然语言目标转换为任务图
    2. 任务原子化 - 将复杂任务分解为原子任务
    3. 执行令牌管理 - 控制任务执行顺序
    4. 轮次锁 - 确保轮次执行的原子性
    5. 关闭记录 - 记录执行结果
    
    Usage::
        compiler = PolarisCompiler()
        result = compiler.compile("分析环评报告并生成摘要")
        if result.success:
            atoms = result.atom_table
    """

    def __init__(self, max_rounds: int = 10):
        """
        Args:
            max_rounds: 最大执行轮次
        """
        self.max_rounds = max_rounds
        self._task_graph: Dict[str, TaskAtom] = {}
        self._atom_table: List[TaskAtom] = []
        self._token_board: List[ExecutionToken] = []
        self._round_lock = RoundLock(round=0)
        self._closure_records: List[ClosureRecord] = []

    def _generate_id(self) -> str:
        """生成唯一ID"""
        return str(uuid.uuid4())[:8]

    def compile(self, goal: str) -> CompilationResult:
        """
        GOAL_COMPILATION - 目标编译
        
        将自然语言目标转换为结构化任务图
        
        Args:
            goal: 自然语言目标描述
        
        Returns:
            CompilationResult 编译结果
        """
        self._task_graph.clear()
        self._atom_table.clear()
        self._token_board.clear()
        
        # 解析目标并生成任务原子
        atoms = self._parse_goal(goal)
        
        # 构建任务图
        self._build_task_graph(atoms)
        
        # 创建执行令牌
        self._create_tokens()
        
        return CompilationResult(
            success=True,
            task_graph=self._task_graph,
            atom_table=self._atom_table,
            metadata={
                'goal': goal,
                'atom_count': len(atoms),
            },
        )

    def _parse_goal(self, goal: str) -> List[TaskAtom]:
        """
        解析目标生成任务原子
        
        Args:
            goal: 目标描述
        
        Returns:
            任务原子列表
        """
        atoms = []
        
        # 简单的规则引擎示例
        if "分析" in goal or "解读" in goal:
            atoms.append(TaskAtom(
                atom_id=self._generate_id(),
                type=TaskType.ATOMIC,
                description="理解目标需求",
            ))
            
            atoms.append(TaskAtom(
                atom_id=self._generate_id(),
                type=TaskType.ATOMIC,
                description="收集相关信息",
                dependencies=[atoms[0].atom_id],
            ))
            
            atoms.append(TaskAtom(
                atom_id=self._generate_id(),
                type=TaskType.ATOMIC,
                description="分析信息内容",
                dependencies=[atoms[1].atom_id],
            ))
            
            atoms.append(TaskAtom(
                atom_id=self._generate_id(),
                type=TaskType.ATOMIC,
                description="生成分析结果",
                dependencies=[atoms[2].atom_id],
            ))
        
        elif "生成" in goal or "创建" in goal:
            atoms.append(TaskAtom(
                atom_id=self._generate_id(),
                type=TaskType.ATOMIC,
                description="理解生成目标",
            ))
            
            atoms.append(TaskAtom(
                atom_id=self._generate_id(),
                type=TaskType.ATOMIC,
                description="收集生成素材",
                dependencies=[atoms[0].atom_id],
            ))
            
            atoms.append(TaskAtom(
                atom_id=self._generate_id(),
                type=TaskType.COMPOSITE,
                description="执行生成任务",
                dependencies=[atoms[1].atom_id],
            ))
            
            atoms.append(TaskAtom(
                atom_id=self._generate_id(),
                type=TaskType.ATOMIC,
                description="验证生成结果",
                dependencies=[atoms[2].atom_id],
            ))
        
        else:
            # 默认任务分解
            atoms.append(TaskAtom(
                atom_id=self._generate_id(),
                type=TaskType.ATOMIC,
                description=f"执行目标: {goal}",
            ))
        
        self._atom_table = atoms
        return atoms

    def _build_task_graph(self, atoms: List[TaskAtom]):
        """
        TASK_GRAPH - 构建任务图
        
        Args:
            atoms: 任务原子列表
        """
        for atom in atoms:
            self._task_graph[atom.atom_id] = atom

    def _create_tokens(self):
        """
        EXECUTION_TOKEN_BOARD - 创建执行令牌
        
        为每个任务原子创建执行令牌
        """
        for priority, atom in enumerate(self._atom_table):
            token = ExecutionToken(
                token_id=self._generate_id(),
                atom_id=atom.atom_id,
                round=0,
                priority=priority,
                timestamp=0.0,
                claimed=False,
            )
            self._token_board.append(token)

    def _acquire_round_lock(self, round_number: int) -> bool:
        """
        ROUND_LOCK - 获取轮次锁
        
        Args:
            round_number: 轮次编号
        
        Returns:
            是否获取成功
        """
        if self._round_lock.locked and self._round_lock.round != round_number:
            return False
        
        self._round_lock.round = round_number
        self._round_lock.locked = True
        self._round_lock.owner = f"round_{round_number}"
        
        return True

    def _release_round_lock(self):
        """释放轮次锁"""
        self._round_lock.locked = False
        self._round_lock.owner = None

    def execute(self, executor: Callable[[TaskAtom], Any]) -> CompilationResult:
        """
        执行编译后的任务图
        
        Args:
            executor: 任务执行器函数
        
        Returns:
            CompilationResult 执行结果
        """
        completed_atoms = []
        failed_atoms = []
        final_result = None
        
        for round_num in range(self.max_rounds):
            if not self._acquire_round_lock(round_num):
                continue
            
            try:
                # 获取当前轮次可执行的任务
                available_tokens = [
                    t for t in self._token_board
                    if not t.claimed and self._is_atom_ready(t.atom_id)
                ]
                
                if not available_tokens:
                    # 检查是否所有任务都已完成
                    if all(atom.state in (TaskState.COMPLETED, TaskState.FAILED) 
                           for atom in self._atom_table):
                        break
                    self._release_round_lock()
                    continue
                
                # 按优先级排序
                available_tokens.sort(key=lambda t: t.priority)
                
                # 执行任务
                for token in available_tokens:
                    token.claimed = True
                    atom = self._task_graph[token.atom_id]
                    
                    try:
                        atom.activate()
                        result = executor(atom)
                        atom.complete(result)
                        completed_atoms.append(token.atom_id)
                        
                        if token.atom_id == self._atom_table[-1].atom_id:
                            final_result = result
                    except Exception as e:
                        atom.fail(str(e))
                        failed_atoms.append(token.atom_id)
            
            finally:
                self._release_round_lock()
        
        # 创建关闭记录
        success = len(failed_atoms) == 0
        closure_record = ClosureRecord(
            record_id=self._generate_id(),
            goal_id=self._generate_id(),
            atoms_completed=completed_atoms,
            atoms_failed=failed_atoms,
            final_result=final_result,
            success=success,
        )
        self._closure_records.append(closure_record)
        
        return CompilationResult(
            success=success,
            task_graph=self._task_graph,
            atom_table=self._atom_table,
            closure_record=closure_record,
            metadata={
                'rounds_executed': round_num + 1,
                'completed_count': len(completed_atoms),
                'failed_count': len(failed_atoms),
            },
        )

    def _is_atom_ready(self, atom_id: str) -> bool:
        """
        检查任务原子是否就绪
        
        Args:
            atom_id: 任务原子ID
        
        Returns:
            是否就绪
        """
        atom = self._task_graph.get(atom_id)
        if not atom or atom.state != TaskState.PENDING:
            return False
        
        # 检查所有依赖是否已完成
        for dep_id in atom.dependencies:
            dep_atom = self._task_graph.get(dep_id)
            if not dep_atom or dep_atom.state != TaskState.COMPLETED:
                return False
        
        return True

    def get_atom_by_id(self, atom_id: str) -> Optional[TaskAtom]:
        """获取指定ID的任务原子"""
        return self._task_graph.get(atom_id)

    def get_tokens_for_round(self, round_number: int) -> List[ExecutionToken]:
        """获取指定轮次的执行令牌"""
        return [t for t in self._token_board if t.round == round_number]

    def get_closure_records(self) -> List[ClosureRecord]:
        """获取所有关闭记录"""
        return self._closure_records.copy()

    def reset(self):
        """重置编译器状态"""
        self._task_graph.clear()
        self._atom_table.clear()
        self._token_board.clear()
        self._round_lock = RoundLock(round=0)
        self._closure_records.clear()

    @property
    def task_graph(self) -> Dict[str, TaskAtom]:
        """获取任务图"""
        return self._task_graph

    @property
    def atom_table(self) -> List[TaskAtom]:
        """获取原子表"""
        return self._atom_table

    @property
    def token_board(self) -> List[ExecutionToken]:
        """获取执行令牌板"""
        return self._token_board
