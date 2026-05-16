"""
Execution Token Board - 执行令牌板

每轮只执行一个解锁原子，完成后释放解锁下游。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class ExecutionToken:
    """执行令牌"""

    token_id: str
    atom_id: str
    round: int
    priority: int = 0
    timestamp: float = 0.0
    claimed: bool = False


class ExecutionTokenBoard:
    """
    执行令牌板

    Usage::
        board = ExecutionTokenBoard()
        token = board.acquire_token("atom_1")
        board.release_token(token.token_id)
    """

    def __init__(self):
        self._tokens: dict[str, ExecutionToken] = {}
        self._current_round = 0

    def acquire_token(
        self,
        atom_id: str,
        priority: int = 0,
    ) -> Optional[ExecutionToken]:
        """获取令牌"""
        for token in self._tokens.values():
            if token.atom_id == atom_id and not token.claimed:
                token.claimed = True
                token.round = self._current_round
                token.timestamp = time.time()
                return token

        token_id = f"token_{len(self._tokens)}"
        token = ExecutionToken(
            token_id=token_id,
            atom_id=atom_id,
            round=self._current_round,
            priority=priority,
            timestamp=time.time(),
            claimed=True,
        )
        self._tokens[token_id] = token
        return token

    def release_token(self, token_id: str) -> bool:
        """释放令牌"""
        if token_id in self._tokens:
            self._tokens[token_id].claimed = False
            return True
        return False

    def get_tokens_for_round(self, round_num: int) -> list[ExecutionToken]:
        """获取指定轮次的令牌"""
        return [t for t in self._tokens.values() if t.round == round_num]

    def advance_round(self) -> None:
        """推进轮次"""
        self._current_round += 1

    def get_active_tokens(self) -> list[ExecutionToken]:
        """获取活跃令牌"""
        return [t for t in self._tokens.values() if t.claimed]
