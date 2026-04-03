from board import Board
from search import Search
from zobristhash import ZobristHash
from transpositiontable import TranspositionTable
import evaluate
import tools

import sys
import time

MAX_DEPTH = 20


class GameState:
    def __init__(self, board: Board=None):
        if board is None:
            self.board = Board()
        else:
            self.board = board
        self.tt = TranspositionTable()
        self.phase = 0
        self.eval_func = evaluate.evaluate_board
        self.position_history = []
        self.halfmove_clock = 0

    def newGameUCI(self, moves=None):
        self.turn = 0
        self.move = 1
        self.move_history = []
        self.position_history = [self.board.zobrist_key]
        self.halfmove_clock = 0
        if moves:
            for move in moves:
                self.board.make_move(move)
                self.turn = 1 - self.turn
                self.move += 1
                self.move_history.append(tools.int_to_uci(move))
                self.position_history.append(self.board.zobrist_key)

    def search(self, time_limit=None):
        start_time = time.time()
        max_depth = MAX_DEPTH if time_limit else 6
        searcher = Search(self.tt, max_depth,
                          position_history=self.position_history,
                          halfmove_clock=self.halfmove_clock)

        eval_score = 0
        move = None

        for d in range(1, max_depth + 1):
            searcher.max_depth = d
            searcher.nodes = 0
            searcher.iterative_deepening(self.board)
            eval_score, move = searcher.best_moves[d]

            elapsed = time.time() - start_time
            elapsed_ms = int(elapsed * 1000)
            nps = int(searcher.nodes / elapsed) if elapsed > 0 else 0
            print(f"info depth {d} score cp {int(eval_score)} "
                  f"nodes {searcher.nodes} nps {nps} time {elapsed_ms}")
            sys.stdout.flush()

            # Time management: stop if next depth would likely exceed time
            if time_limit:
                # Estimate next depth will take ~3-5x longer
                if elapsed > time_limit * 0.4:
                    break
            else:
                # No time limit: use fixed depth
                if d >= 6:
                    break

        return eval_score, move

    def make_move(self, move):
        commital = self.board.is_commital_move(move)

        self.board.make_move(move)
        self.turn = 1 - self.turn
        self.move += 1
        self.move_history.append(tools.int_to_uci(move))
        self.position_history.append(self.board.zobrist_key)

        from_square = move & 0x3F
        piece_type = (move >> 12) & 0x7
        capture_flag = (move >> 17) & 0x1
        if piece_type == 0 or capture_flag or commital:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if commital:
            self.tt.evict_obsolete(self.board.commits)
