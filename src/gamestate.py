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
        self.depth = 3
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
            
            searcher = Search(self.tt, self.depth)
            eval, move = searcher.start_search(self.board)

            if elapsed_time_ms < float(movetime):
                time.sleep((float(movetime) - elapsed_time_ms) / 1000)
        else:
            searcher = Search(self.tt, self.depth)
            eval, move = searcher.start_search(self.board)

        return eval, move
        """
        print(len(self.tt.entries))
        #print(self.tt.entries)
        print(sys.getsizeof(self.tt.entries))
        print(sys.getsizeof(self.tt))
        """

    def make_move(self, move):
        commital = self.board.is_commital_move(move)

        self.board.make_move(move)
        self.turn = 1 - self.turn
        self.move += 1
        self.move_history.append(tools.int_to_uci(move))

        # Increase depth if endgame
        if self.move > 2:
            self.depth = evaluate.update_depth(self)

        if commital:
            self.tt.evict_obsolete(self.board.commits)
        

        # position startpos moves d2d4 d7d5 c1g5 g8f6 h2h4 c8g4 c2c4 d5c4 g5f6 e7f6 b1c3 b8c6 d1b3 c4b3    
        # position startpos moves d2d4 a7a6 c1f4 d7d6 g1f3 b8c6 e2e3 e7e6 c2c4 d8d7 f1d3 b7b6 e1g1 a6a5 b1c3 f7f6 a1c1 e8d8 a2a3 d8e7 c3b5 e7d8 d4d5
        # position startpos moves d2d4 b8c6 c1f4 d7d5 e2e3 c8f5 g1f3 g8f6 c2c4 d5c4 f1c4 e7e6 b1c3 f8b4 e1g1 b4c3 b2c3 e8g8 d1b3 a8b8 f1d1 f6e4 c4d3 g8h8 b3c2