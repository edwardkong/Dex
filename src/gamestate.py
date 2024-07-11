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
        print(sys.getsizeof(self.board))
        print(sys.getsizeof(self))
        # Monitor transposition table size
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
            self.depth, self.phase = evaluate.update_depth(self)

        if commital:
            self.tt.evict_obsolete(self.board.commits)