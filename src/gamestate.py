from board import Board
import search
import time

class GameState:
    def __init__(self, board: Board=None):
        if board is None:
            self.board = Board()

        else:
            self.board = board

    def newGameUCI(self, moves=None):
        self.turn = 0  # WHITE = 0; BLACK = 1
        self.move = 1  # Move number (Ply)
        self.move_history = []

        if moves:
            for move in moves:
                self.board.make_move(move)
                self.turn = 1 - self.turn
                self.move += 1
                self.move_history.append(move)

    # Minimax search
    def search(self, depth, color, evaluate_func):
        alpha = float("-inf")
        beta = float("inf")
        eval, move = search.minimax_alpha_beta(self.board, depth, alpha, beta, color, evaluate_func)
        
        return eval, move

    def startSearchTimed(self, movetime, depth, evaluate_func):
        start_time = time.time()
        eval, best_move = self.search(depth, self.turn, evaluate_func)
        elapsed_time_ms = (time.time() - start_time) * 1000

        if elapsed_time_ms < float(movetime):
            time.sleep((float(movetime) - elapsed_time_ms) / 1000)

        return eval, best_move

    def make_move(self, move):
        self.board.make_move(move)
        self.turn = 1 - self.turn
        self.move += 1
        self.move_history.append(move)