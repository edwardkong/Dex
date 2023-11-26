import position, makemove, movegen, tools, game
import random, sys, time

class Board:
    # Board representing position of pieces
    def __init__(self, bitboard = None, board_fen = None):
        if board_fen:
            self.initialize_from_fen(self, board_fen)
        elif bitboard:
            self.newBoard(bitboard)
        else:
            self.newBoard()

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
            color = piece & 1
            piece_type = piece >> 1
            pieces = self.bitboards[piece_type][color]
            while pieces:
                piece_found = tools.bitscan_lsb(pieces)
                text_board[piece_found] = tools.int_to_char_piece(piece_type).lower() if color == 1 else tools.int_to_char_piece(piece_type)
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
        self.castling_rights = {'WK': 0, 'WQ': 0, 'BK': 0, 'BQ': 0}
        self.turn = 0 # WHITE = 0; BLACK = 1
        self.move = 1 # Move #
        self.move_history = []

        if moves:
            for move in moves:
                self.board.bitboards = position.update_board(self.board.bitboards, move)
                self.turn = 1 - self.turn
                self.move += 1
                self.move_history.append(move)

    def startSearchTimed(self, movetime):
        start_time = time.time()
        int_move, best_move = self.search()
        elapsed_time_ms = (time.time() - start_time) * 1000
        if elapsed_time_ms < float(movetime):
            time.sleep((float(movetime) - elapsed_time_ms) / 1000)
        return int_move, best_move

    def search(self):
        moves = movegen.generate_moves(self.board, self.turn)
        int_move = random.choice(moves)
        best_move = makemove.int_to_uci(int_move)
        return int_move, best_move
    
    def makemove(self, move):
        self.board.bitboards = position.update_board(self.board.bitboards, move)
        self.turn = 1 - self.turn
        self.move += 1
        self.move_history.append(move)

    def manualNewGame(self, b = None):
        if b is None: self.board.newBoard()
        else: self.board = b
        self.castling_rights = {'WK': 1, 'WQ': 1, 'BK': 1, 'BQ': 1}
        self.turn = 0 # WHITE = 0; BLACK = 1
        self.move = 1 # Move #
        self.move_history = []
        
        while True:
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
            else:
                moves = movegen.generate_moves(self.board, self.turn)
                selection = random.choice(moves)
                print("Moves considered: ")
                for move in moves: print(makemove.int_to_uci(move))
                print(makemove.int_to_uci(selection))

            self.board.bitboards = position.update_board(self.board.bitboards, selection)
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

def testing():
    mode = input("bb or ng: ")
    if mode == "ng":
        game = GameState()
    else:
        bb = {0: {0: 268496640, 1: 62205978442989568}, 1: {0: 66, 1: 39582418599936}, 2: {0: 36, 1: 2594073385365405696}, 3: {0: 129, 1: 9295429630892703744}, 4: {0: 9007199254740992, 1: 576460752303423488}, 5: {0: 16, 1: 1152921504606846976}}
        game = GameState(Board(bb))

if __name__ == "__main__":
    ng = game.GameState()
    while True:
        command = input()
        if command == "uci":
            id = "id name Dex 0.0\nid author EK\n"
            sys.stdout.write("uciok") 
            sys.stdout.write(id)
            
        elif command == "option":
            sys.stdout.write()
        elif command == "debug":
            pass
        elif command == "isready":
            # Set tablebases
            sys.stdout.write("readyok")
        elif command == "ucinewgame":
            # New game
            sys.stdout.write("readyok")
        elif command[:23] == "position startpos moves":
            moves = command[23:].split()
            for move in moves:
                ng.makemove(move)
            
        elif command[:2] == "go":
            move = ng.search()
            sys.stdout.write(f"bestmove {move}")
            ng.makemove(move)
        elif command == quit:
            quit()

