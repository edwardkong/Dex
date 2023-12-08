
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

def combine_bitboard(board, color=None):
    result_bitboard = 0
    if color is None:
        for piece in range(12):
            result_bitboard |= board.bitboards[piece]
    else:
        for piece in range(6):
            result_bitboard |= board.bitboards[piece + color*6]

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

def print_board(board) -> list:
    text_board = ["-"] * 64  # 8x8
    for piece in range(12):
        pieces = board.bitboards[piece]
        while pieces:
            piece_found = bitscan_lsb(pieces)
            text_board[piece_found] = int_to_char_piece(piece)
            pieces &= pieces - 1
    return text_board

def print_bitboards(bitboards) -> list:
    text_board = ["-"] * 64  # 8x8
    for piece in range(12):
        pieces = bitboards[piece]
        while pieces:
            piece_found = bitscan_lsb(pieces)
            text_board[piece_found] = int_to_char_piece(piece)
            pieces &= pieces - 1
    for rank in range(7, -1, -1):
        for file in range(8):
            square = rank * 8 + file
            print(text_board[square], end=" ")
        print()
    
    return text_board

def print_bitboard(bb_int):
    i = 56
    bits = bin(bb_int)
    bits = '0' * (66 - len(bits)) + bits[2:]
    for x in range(8):
        print(bits[i:i+7])
        i -= 8

# Standard UCI move notation includes 4 characters, source square and destination square. 
# Castling is specified by king position (i.e. e1g1).
# Promotions are specified with 5 characters, to disambiguate promting pieces (i.e. g7g8q)

def uci_to_int(lan_move, bitboards):
    # Basic error checking
    if not lan_move or not bitboards:
        print("Invalid input.")
        return None

    # Convert UCI LAN to coordinates
    from_square, to_square, promotion = lan_move[:2], lan_move[2:4], lan_move[4:]

    # Map coordinates to bitboard indices
    from_index = 8 * (int(from_square[1]) - 1) + ord(from_square[0]) - ord('a')
    to_index = 8 * (int(to_square[1]) - 1) + ord(to_square[0]) - ord('a')

    # Determine the piece type & color
    for piece_color in range(12):
        color = piece_color & 1
        piece_type = piece_color >> 1

        if (bitboards[piece_type + color*6] & (1 << from_index)):
            break
    else:
        print("Invalid move: No piece found on the source square.")
        return None

    # Consider if the move is a promotion
    if promotion:
        promotion_mapping = {'n': 1, 'b': 2, 'r': 3, 'q': 4}
        piece_type = promotion_mapping.get(promotion.lower(), 0)
    
    # Generate the move as a 32-bit integer
    return from_index | (to_index << 6) | (piece_type << 12) | (color << 15)

def int_to_uci(move):
    from_square = move & 0x3F  # Source square
    to_square = (move >> 6) & 0x3F  # Destination square
    piece_type = (move >> 12) & 0x7  # Piece type (0-5)
    color = (move >> 15) & 0x1  # Color (0 for white, 1 for black)
    promotion_flag = (move >> 16) & 0x1 # 1 if promotion

    f_file = from_square % 8
    f_rank = from_square // 8
    f_s = chr(ord('a') + f_file) + str(f_rank + 1)

    t_file = to_square % 8
    t_rank = to_square // 8
    t_s = chr(ord('a') + t_file) + str(t_rank + 1)
    
    piece_char = int_to_char_piece(piece_type).lower()

    return f"{f_s}{t_s}{piece_char if promotion_flag else ''}"