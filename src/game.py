import position, makemove, movegen, tools, game, search, evaluate
import random, sys, time, datetime
import cProfile

class Board:
    # Board representing position of pieces
    def __init__(self, bitboard = None, board_fen = None):
        if board_fen:
            self.initialize_from_fen(self, board_fen)
        elif bitboard:
            self.newBoard(bitboard)
        else:
            self.newBoard()
        #self.castling_rights = {'WK': 1, 'WQ': 1, 'BK': 1, 'BQ': 1}
        self.castling_rights = {'WK': 0, 'WQ': 0, 'BK': 0, 'BQ': 0}


    def newBoard(self, bitboard: dict = None) -> None:
        if bitboard:
            self.bitboards = bitboard
        else:
            self.bitboards = position.initialize_bitboard()


    def initialize_from_fen(self, fen) -> None:
        bitboard = None
        return bitboard

    def reset_board(self) -> None:
        self.bitboards = position.initialize_bitboard()

    def getBB(self):
        return self.bitboards

    def get_last_move(self) -> str:
        return self.move_history[-1]

    def print_board(self) -> list:
        text_board = ['-'] * 64 # 8x8
        for piece in range(12):
            pieces = self.bitboards[piece]
            while pieces:
                piece_found = tools.bitscan_lsb(pieces)
                text_board[piece_found] = tools.int_to_char_piece(piece)
                pieces &= pieces - 1
        return text_board

class GameState:
    def __init__(self, board: Board = None):
        if board is None:
            self.board = Board()
            self.newGameUCI()
        else:
            self.board = board
            self.newGame(board)

    def newGameUCI(self, moves = None):
        #self.castling_rights = {'WK': 1, 'WQ': 1, 'BK': 1, 'BQ': 1}
        self.turn = 0 # WHITE = 0; BLACK = 1
        self.move = 1 # Move #
        self.move_history = []

        if moves:
            for move in moves:
                self.board.bitboards = position.update_board(self.board.bitboards, move)
                self.board.bitboards = position.refresh_occupant_bitboards(self.board.bitboards)
                self.turn = 1 - self.turn
                self.move += 1
                self.move_history.append(move)


    # Random eval
    def search(self):
        moves = movegen.generate_moves(self.board, self.turn)
        int_move = random.choice(moves)
        best_move = makemove.int_to_uci(int_move)
        return int_move, best_move

    def startSearchTimed(self, movetime):
        start_time = time.time()
        int_move, best_move = self.search()
        elapsed_time_ms = (time.time() - start_time) * 1000
        if elapsed_time_ms < float(movetime):
            time.sleep((float(movetime) - elapsed_time_ms) / 1000)
        return int_move, best_move

    # Minimax search
    def searchMM(self, depth, color, evaluate_func):
        #eval, move = search.minimax(self.board.bitboards, depth, color, evaluate_func)
        alpha = float('-inf')
        beta = float('inf')
        eval, move = search.minimax_alpha_beta(self.board.bitboards, depth, alpha, beta, color, evaluate_func)
        return eval, move
    
    def startSearchTimedMM(self, movetime, depth, evaluate_func):
        start_time = time.time()
        eval, best_move = self.searchMM(depth, self.turn, evaluate_func)
        elapsed_time_ms = (time.time() - start_time) * 1000
        if elapsed_time_ms < float(movetime):
            time.sleep((float(movetime) - elapsed_time_ms) / 1000)
        return eval, best_move
    
    def makemove(self, move):
        self.board.bitboards = position.update_board(self.board.bitboards, move)
        self.board.bitboards = position.refresh_occupant_bitboards(self.board.bitboards)
        self.turn = 1 - self.turn
        self.move += 1
        self.move_history.append(move)
        
    def manualNewGame(self, b = None):
        if b is None: self.board.newBoard()
        else: self.board = b
        #self.castling_rights = {'WK': 1, 'WQ': 1, 'BK': 1, 'BQ': 1}
        self.turn = 0 # WHITE = 0; BLACK = 1
        self.move = 1 # Move #
        self.move_history = []
        evaluate_func = evaluate.evaluate_board
        
        m = ['d2d4', 'd7d5', 'c1f4', 'c8f4', 'g1f3', 'g8f6', 'e2e3', 'e7e6', 'c2c3', 'c7c6']

        #for i in m:
            #self.makemove(makemove.uci_to_int(i, self.board.bitboards))

        #i = 4
        while True:
            #i-=1
            print ("----------------------------------")
            text_board = self.board.print_board()

            for rank in range(7, -1, -1):
                for file in range(8):
                    square = rank * 8 + file
                    print(text_board[square],end = ' ')
                print()
            
            print ("----------------------------------")

            print(f"'Move: ' {self.move}")
            if self.turn == 0: print("White to play")
            elif self.turn == 1: print("Black to play")

            if self.turn == 0:
                move = input("Your turn: ")
                if move == "BB":
                    print(self.board.bitboards)
                selection = makemove.uci_to_int(move, self.board.bitboards)
            elif evaluate_func == "random":
                moves = movegen.generate_moves(self.board, self.turn)
                selection = random.choice(moves)
                print("Moves considered: ")
                for move in moves: print(makemove.int_to_uci(move))
                print(makemove.int_to_uci(selection))
            elif evaluate_func == evaluate.evaluate_board:
                depth = float(input("Search depth: "))
                start_time = time.time()
                eval, best_move = self.searchMM(depth, self.turn, evaluate_func)
                elapsed_time_ms = (time.time() - start_time) * 1000
                print(elapsed_time_ms)
                print(f"eval: {eval} bestmove: {makemove.int_to_uci(best_move)}")
                selection = best_move

            self.board.bitboards = position.update_board(self.board.bitboards, selection)
            self.board.bitboards = position.refresh_occupant_bitboards(self.board.bitboards)
            self.turn = 1 - self.turn
            self.move += 1
            self.move_history.append(selection)

    def is_checkmate(bitboards, color):
        # Can check all possible moves, if there are no resulting legal positions, is checkmate
        # No legal moves, and in check
        return True

    def is_stalemate(bitboards, color):
        # No legal moves, but not in check
        return True

if __name__ == "__main__":
    ng = game.GameState()
    #ng.manualNewGame()
    cProfile.run('ng.manualNewGame()')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    