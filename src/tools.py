
def bitscan_lsb(bits):
    # Find the index of the least significant set bit (LSB)
    return (bits & -bits).bit_length() - 1

def bitscan_msb(bits):
    if bits == 0:
        return None  # No set bit in the number

    position = 0
    while bits:
        bits >>= 1
        position += 1

    return position

def char_to_int_piece(piece):
    map = {
        "PAWN": 0,
        "KNIGHT": 1,
        "BISHOP": 2,
        "ROOK": 3,
        "QUEEN": 4,
        "KING": 5,
        "P": 0,
        "N": 1,
        "B": 2,
        "R": 3,
        "Q": 4,
        "K": 5
    }
    if piece.upper() in map.keys():
        return map.get(piece.upper())

def int_to_char_piece(piece):
    map = {
        0: "P",
        1: "N",
        2: "B",
        3: "R",
        4: "Q",
        5: "K",
        6: "p",
        7: "n",
        8: "b",
        9: "r",
        10: "q",
        11: "k",
    }
    if piece in map.keys():
        return map.get(piece)

def combine_bitboard(bitboards: list, color = None):
    result_bitboard = 0
    if color is None:
        for piece in range(12):
            result_bitboard |= bitboards[piece]
    else:
        for piece in range(6):
            result_bitboard |= bitboards[piece + color*6]

    return result_bitboard

def print_bitboard(bitboard):
    for rank in range(7, -1, -1):
        row = []
        for file in range(0, 7):
            square = rank * 8 + file
            if (bitboard & (1 << square)) != 0:
                row.append('1')
            else:
                row.append('0')
        print(' '.join(row))

def parse_move(move):
    from_square = move & 0x3F  # Source square
    to_square = (move >> 6) & 0x3F  # Destination square
    piece_type = (move >> 12) & 0x7  # Piece type (0-5)
    color = (move >> 15) & 0x1

    return from_square, to_square, piece_type, color

def encode_move(from_square, to_square, piece_type, color):
    move = from_square | (to_square << 6) | (piece_type << 12) | (color << 15)
    return move

    def print_board(self) -> list:
        text_board = ["-"] * 64  # 8x8
        for piece in range(12):
            pieces = self.bitboards[piece]
            while pieces:
                piece_found = tools.bitscan_lsb(pieces)
                text_board[piece_found] = tools.int_to_char_piece(piece)
                pieces &= pieces - 1
        return text_board