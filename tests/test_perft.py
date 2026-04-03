"""Perft (performance test) suite for move generation correctness.

Counts leaf nodes at given depths from known positions and compares
against established correct values. Any mismatch indicates a bug
in move generation, make/unmake, or board state management.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from board import Board
from movegenerator import MoveGenerator
import tools


def perft(board: Board, depth: int) -> int:
    """Count leaf nodes at the given depth from the current position."""
    if depth == 0:
        return 1

    mg = MoveGenerator(board)
    moves = mg.generate_moves()
    nodes = 0

    for move in moves:
        board_copy = board.sim_move(move)
        nodes += perft(board_copy, depth - 1)

    return nodes


def setup_position(moves_uci: list[str]) -> Board:
    """Set up a board by playing a sequence of UCI moves from startpos."""
    board = Board()
    for move_str in moves_uci:
        move = tools.uci_to_int(move_str, board.bitboards)
        board.make_move(move)
    return board


# Starting position perft values (well-established)
# Source: https://www.chessprogramming.org/Perft_Results
class TestPerftStartingPosition:
    def setup_method(self):
        self.board = Board()

    def test_perft_1(self):
        assert perft(self.board, 1) == 20

    def test_perft_2(self):
        assert perft(self.board, 2) == 400

    def test_perft_3(self):
        assert perft(self.board, 3) == 8902

    def test_perft_4(self):
        assert perft(self.board, 4) == 197281


# Kiwipete — exercises castling, en passant, pins, promotions
class TestPerftKiwipete:
    def setup_method(self):
        self.board = Board.from_fen(
            "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -"
        )

    def test_perft_1(self):
        assert perft(self.board, 1) == 48

    def test_perft_2(self):
        assert perft(self.board, 2) == 2039

    def test_perft_3(self):
        assert perft(self.board, 3) == 97862


# Position 3 — en passant discovery, pins
class TestPerftPosition3:
    def setup_method(self):
        self.board = Board.from_fen(
            "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - -"
        )

    def test_perft_1(self):
        assert perft(self.board, 1) == 14

    def test_perft_2(self):
        assert perft(self.board, 2) == 191

    def test_perft_3(self):
        assert perft(self.board, 3) == 2812
