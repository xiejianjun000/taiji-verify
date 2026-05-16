"""Execution Token Board Tests"""
import pytest
from taiji_verify.execution.execution_token import (
    ExecutionToken,
    ExecutionTokenBoard,
)


class TestExecutionToken:
    def test_token_creation(self):
        token = ExecutionToken(
            token_id="t1",
            atom_id="a1",
            round=1,
            priority=0,
        )
        assert token.token_id == "t1"
        assert token.atom_id == "a1"
        assert token.round == 1
        assert token.priority == 0
        assert token.claimed is False

    def test_token_default_values(self):
        token = ExecutionToken(token_id="t1", atom_id="a1", round=0)
        assert token.priority == 0
        assert token.timestamp == 0.0
        assert token.claimed is False


class TestExecutionTokenBoard:
    def test_init(self):
        board = ExecutionTokenBoard()
        assert board._current_round == 0
        assert len(board._tokens) == 0

    def test_acquire_new_token(self):
        board = ExecutionTokenBoard()
        token = board.acquire_token("atom_1")
        assert token is not None
        assert token.atom_id == "atom_1"
        assert token.claimed is True
        assert token.token_id.startswith("token_")

    def test_acquire_existing_unclaimed_token(self):
        board = ExecutionTokenBoard()
        token1 = board.acquire_token("atom_1")
        board.release_token(token1.token_id)
        token2 = board.acquire_token("atom_1")
        assert token2 is not None
        assert token2.token_id == token1.token_id

    def test_acquire_same_atom_twice_creates_new_token(self):
        board = ExecutionTokenBoard()
        token1 = board.acquire_token("atom_1")
        token2 = board.acquire_token("atom_1")
        assert token2 is not None
        assert token1.token_id != token2.token_id
        assert token1.claimed is True
        assert token2.claimed is True

    def test_release_token(self):
        board = ExecutionTokenBoard()
        token = board.acquire_token("atom_1")
        assert token.claimed is True
        result = board.release_token(token.token_id)
        assert result is True
        assert board._tokens[token.token_id].claimed is False

    def test_release_nonexistent_token(self):
        board = ExecutionTokenBoard()
        result = board.release_token("nonexistent")
        assert result is False

    def test_get_tokens_for_round(self):
        board = ExecutionTokenBoard()
        token1 = board.acquire_token("atom_1")
        board.advance_round()
        token2 = board.acquire_token("atom_2")
        tokens_round_0 = board.get_tokens_for_round(0)
        tokens_round_1 = board.get_tokens_for_round(1)
        assert len(tokens_round_0) == 1
        assert len(tokens_round_1) == 1
        assert tokens_round_0[0].atom_id == "atom_1"
        assert tokens_round_1[0].atom_id == "atom_2"

    def test_advance_round(self):
        board = ExecutionTokenBoard()
        assert board._current_round == 0
        board.advance_round()
        assert board._current_round == 1
        board.advance_round()
        assert board._current_round == 2

    def test_get_active_tokens(self):
        board = ExecutionTokenBoard()
        token1 = board.acquire_token("atom_1")
        board.acquire_token("atom_2")
        token3 = board.acquire_token("atom_3")
        board.release_token(token1.token_id)
        board.release_token(token3.token_id)
        active = board.get_active_tokens()
        assert len(active) == 1
        assert active[0].atom_id == "atom_2"

    def test_multiple_tokens_different_atoms(self):
        board = ExecutionTokenBoard()
        tokens = []
        for i in range(5):
            token = board.acquire_token(f"atom_{i}")
            assert token is not None
            tokens.append(token)
        assert len(tokens) == 5
        assert len(board._tokens) == 5

    def test_acquire_token_with_priority(self):
        board = ExecutionTokenBoard()
        token = board.acquire_token("atom_1", priority=5)
        assert token.priority == 5

    def test_token_round_increments(self):
        board = ExecutionTokenBoard()
        token1 = board.acquire_token("atom_1")
        round1 = token1.round
        board.advance_round()
        token2 = board.acquire_token("atom_2")
        round2 = token2.round
        assert round2 > round1

    def test_empty_board_get_tokens_for_round(self):
        board = ExecutionTokenBoard()
        tokens = board.get_tokens_for_round(0)
        assert len(tokens) == 0

    def test_empty_board_get_active_tokens(self):
        board = ExecutionTokenBoard()
        active = board.get_active_tokens()
        assert len(active) == 0
