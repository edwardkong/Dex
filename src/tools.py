
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