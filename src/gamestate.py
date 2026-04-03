from board import Board
from search import Search
from zobristhash import ZobristHash
from transpositiontable import TranspositionTable
import evaluate
import tools

import sys
import time


class GameState:
    def __init__(self, board: Board=None):
        if board is None:
            self.board = Board()
        else:
            self.board = board
        self.tt = TranspositionTable()
        self.depth = 5
        self.phase = 0
        self.eval_func = evaluate.evaluate_board

    def newGameUCI(self, moves=None):
        self.turn = 0  # WHITE = 0; BLACK = 1
        self.move = 1  # Move number (Ply)
        self.move_history = []
        if moves:
            for move in moves:
                self.board.make_move(move)
                self.turn = 1 - self.turn
                self.move += 1
                self.move_history.append(tools.int_to_uci(move))

    def search(self, time_limit=None):
        start_time = time.time()
        searcher = Search(self.tt, self.depth)

        # Search with iterative deepening, reporting info per depth
        for d in range(1, self.depth + 1):
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

            # Time cutoff: don't start next depth if we've used > 50% of time
            if time_limit and elapsed > time_limit * 0.5:
                break

        return eval_score, move

    def make_move(self, move):
        commital = self.board.is_commital_move(move)

        self.board.make_move(move)
        self.turn = 1 - self.turn
        self.move += 1
        self.move_history.append(tools.int_to_uci(move))

        # Increase depth if endgame
        if self.move > 2:
            self.depth, self.phase = evaluate.update_depth(self)

        if commital:
            self.tt.evict_obsolete(self.board.commits)
