import tools
import random

class ZobristHash:
    def __init__(self) -> None:
        self.zobrist_table = self.initialize_zobrist_table()

    def initialize_zobrist_table(self):
        zobrist_table = [[random.getrandbits(64)] * 12 for i in range(64)]

        return zobrist_table
    
    def generate_hash(self, board, zobrist_table):
        hash = 0
        for piece in range(12):
            pieces = board.bitboards[piece]

            while pieces:
                piece_square = tools.bitscan_lsb(pieces)
                hash ^= zobrist_table[piece_square][piece]
                pieces &= pieces - 1

        return hash