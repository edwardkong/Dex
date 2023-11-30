from board import Board
from movegenerator import MoveGenerator

import tools, search, evaluate, moveorder
import random, time, datetime
import cProfile

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

    def manualNewGame(self):
        self.turn = 0  # WHITE = 0; BLACK = 1
        self.move = 1  # Move #
        self.move_history = []
        evaluate_func = evaluate.evaluate_board
        #evaluate_func = random.choice

        i = 3
        while i:
            print("----------------------------------")
            text_board = tools.print_board(self.board)

            for rank in range(7, -1, -1):
                for file in range(8):
                    square = rank * 8 + file
                    print(text_board[square], end=" ")
                print()

            print("----------------------------------")

            print(f"'Move: ' {self.move}")
            if self.turn == 0:
                print("White to play")
            elif self.turn == 1:
                print("Black to play")

            if self.turn == 0:
                move = input("Your turn: ")
                if move == "BB":
                    print(self.board.bitboards)
                selection = tools.uci_to_int(move, self.board.bitboards)
            elif evaluate_func == "random":
                moves = movegenerator.generate_moves()
                selection = random.choice(moves)
                print("Moves considered: ")
                for move in moves:
                    print(tools.int_to_uci(move))
                print(tools.int_to_uci(selection))
            elif evaluate_func == evaluate.evaluate_board:
                depth = float(input("Search depth: "))
                start_time = time.time()
                eval, best_move = self.search(depth, self.turn, evaluate_func)
                elapsed_time_ms = (time.time() - start_time) * 1000
                print(elapsed_time_ms)
                print(f"eval: {eval} bestmove: {tools.int_to_uci(best_move)}")
                selection = best_move

            self.board.make_move(selection)
            self.turn = 1 - self.turn
            self.move += 1
            self.move_history.append(selection)
        
            i -= 1


if __name__ == "__main__":
    ng = GameState()
    # ng.manualNewGame()
    cProfile.run("ng.manualNewGame()")
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
