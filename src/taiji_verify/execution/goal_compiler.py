"""
Goal Compiler - 目标编译器

扩展polaris.py：create_truth_objects / create_claim_ceilings / create_verification_gates
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from taiji_verify.polaris import PolarisCompiler, TaskAtom, TaskState


@dataclass
class TruthObject:
    """真理对象"""
    id: str
    content: str
    verification_criteria: str
    confidence: float


@dataclass
class ClaimCeiling:
    """声明上限"""
    id: str
    claim: str
    max_confidence: float
    required_sources: list[str] = field(default_factory=list)


@dataclass
class VerificationGate:
    """验证门"""
    id: str
    criteria: str
    threshold: float
    passed: bool = False


@dataclass
class ExtendedCompilationResult:
    """扩展编译结果"""
    truth_objects: list[TruthObject]
    claim_ceilings: list[ClaimCeiling]
    verification_gates: list[VerificationGate]
    base_result: Optional[dict] = None


class GoalCompiler(PolarisCompiler):
    """
    目标编译器

    Usage::
        compiler = GoalCompiler()
        result = compiler.compile_extended("分析碳排放权交易政策")
        print(result.truth_objects)
    """

    def create_truth_objects(self, goal: str) -> list[TruthObject]:
        """创建真理对象"""
        objects = []
        keywords = self._extract_keywords(goal)

        for i, kw in enumerate(keywords[:3]):
            objects.append(TruthObject(
                id=f"TO_{i+1}",
                content=kw,
                verification_criteria=f"验证{kw}的正确性",
                confidence=0.9,
            ))

        return objects

    def create_claim_ceilings(self, goal: str) -> list[ClaimCeiling]:
        """创建声明上限"""
        ceilings = []
        keywords = self._extract_keywords(goal)

        for i, kw in enumerate(keywords[:2]):
            ceilings.append(ClaimCeiling(
                id=f"CC_{i+1}",
                claim=f"关于{kw}的声明",
                max_confidence=0.8,
                required_sources=[],
            ))

        return ceilings

    def create_verification_gates(self, goal: str) -> list[VerificationGate]:
        """创建验证门"""
        gates = [
            VerificationGate(
                id="VG_1",
                criteria="问题构成",
                threshold=0.7,
            ),
            VerificationGate(
                id="VG_2",
                criteria="世界对齐",
                threshold=0.8,
            ),
        ]
        return gates

    def compile_extended(self, goal: str) -> ExtendedCompilationResult:
        """扩展编译"""
        truth_objects = self.create_truth_objects(goal)
        claim_ceilings = self.create_claim_ceilings(goal)
        verification_gates = self.create_verification_gates(goal)

        return ExtendedCompilationResult(
            truth_objects=truth_objects,
            claim_ceilings=claim_ceilings,
            verification_gates=verification_gates,
        )

    def _extract_keywords(self, text: str) -> list[str]:
        """提取关键词"""
        import re
        words = re.findall(r'[\u4e00-\u9fff]+', text)
        return [w for w in words if len(w) >= 2]
