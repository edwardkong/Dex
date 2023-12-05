import tools

# Piece values
PAWN_VALUE = 100
KNIGHT_VALUE = 320
BISHOP_VALUE = 330
ROOK_VALUE = 500
QUEEN_VALUE = 900
KING_VALUE = 20000

# Piece square tables (these are simple tables and not optimized for real use)
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     50, 50, 50, 50, 50, 50, 50, 50,
     10, 10, 20, 35, 35, 20, 10, 10,
     5,  5, 10, 30, 30, 10,  5,  5,
     0,  0,  0, 25, 25,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-25,-25, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
    -50,-30,-30,-30,-30,-30,-30,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-30,-30,-30,-30,-30,-30,-50
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

KING_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20
] # Middle / Early Game, need implementation for end game

def evaluate_board(board):
    evaluation = 0

    # Piece values

    for piece in range(12):
        piece_type = piece % 6
        color = piece // 6
        pieces = board.bitboards[piece]

        while pieces:
            # Find the index of the least significant set bit (LSB)
            square = tools.bitscan_lsb(pieces) if color else (63 - tools.bitscan_lsb(pieces))

            sign = -1 if color else 1

            if piece_type == 0:
                evaluation += ((sign * PAWN_VALUE) + (sign * PAWN_TABLE[square]))
            elif piece_type == 1:
                evaluation += ((sign * KNIGHT_VALUE) + (sign * KNIGHT_TABLE[square]))
            elif piece_type == 2:
                evaluation += ((sign * BISHOP_VALUE) + (sign * BISHOP_TABLE[square]))
            elif piece_type == 3:
                evaluation += ((sign * ROOK_VALUE) + (sign * ROOK_TABLE[square]))
            elif piece_type == 4:
                evaluation += ((sign * QUEEN_VALUE) + (sign * QUEEN_TABLE[square]))
            elif piece_type == 5:
                evaluation += ((sign * KING_VALUE) + (sign * KING_TABLE[square]))

            # Clear the LSB to move to the next piece
            pieces &= pieces - 1


    return evaluation

def update_depth(gamestate):
    color = gamestate.turn

    pieces_remaining_score = 0

    for piece_type in range(5):
        num_pieces = bin(gamestate.board.bitboards[piece_type + color * 6]).count('1')
        if piece_type == 0:
            pieces_remaining_score += num_pieces * PAWN_VALUE
        elif piece_type == 1:
            pieces_remaining_score += num_pieces * KNIGHT_VALUE
        elif piece_type == 2:
            pieces_remaining_score += num_pieces * BISHOP_VALUE
        elif piece_type == 3:
            pieces_remaining_score += num_pieces * ROOK_VALUE
        elif piece_type == 4:
            pieces_remaining_score += num_pieces * QUEEN_VALUE
    
    if pieces_remaining_score <= 1200:
        return 6
    else:
        return 4
