
def bitscan_lsb(bits):
    # Find the index of the least significant set bit (LSB)
    return (bits & -bits).bit_length() - 1

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
        5: "K"
    }
    if piece in map.keys():
        return map.get(piece)

def combine_bitboard(bitboards: dict, color = None):
    result_bitboard = 0
    if color is None:
        for board in bitboards:
            result_bitboard |= board
    else:
        for i in range(6):
            result_bitboard |= bitboards[i][color]
    return result_bitboard