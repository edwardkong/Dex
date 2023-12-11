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
        self.depth = 4
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

    # Minimax search
    def search(self, movetime=None):
        if movetime:
            start_time = time.time()
            elapsed_time_ms = (time.time() - start_time) * 1000
            
            searcher = Search(self.tt)
            eval, move = searcher.minimax_ab(self.board, self.depth, self.turn)

            if elapsed_time_ms < float(movetime):
                time.sleep((float(movetime) - elapsed_time_ms) / 1000)
        else:
            searcher = Search(self.tt)
            eval, move = searcher.minimax_ab(self.board, self.depth, self.turn)

        print(len(self.tt.entries))
        print(sys.getsizeof(self.tt.entries))
        print(sys.getsizeof(self.tt))

        return eval, move

    def make_move(self, move):
        self.board.make_move(move)
        self.turn = 1 - self.turn
        self.move += 1
        self.move_history.append(tools.int_to_uci(move))
        # Increase depth if endgame
        if self.move > 20:
            self.depth = evaluate.update_depth()
        