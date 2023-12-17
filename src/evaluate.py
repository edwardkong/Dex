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

KING_TABLE_END = [

]

def evaluate_board(board):
    evaluation = 0

    # Piece values

    for piece in range(12):
        piece_type = piece % 6
        color = piece // 6
        pieces = board.bitboards[piece]

        while pieces:
            # Find the index of the least significant set bit (LSB)
            square = tools.bitscan_lsb(pieces) 
            if not color:
                square = (63 - square)
            sign = -1 if color else 1
            if piece_type == 0:
                evaluation += ((sign * PAWN_VALUE)
                               + (sign * PAWN_TABLE[square]))

            elif piece_type == 1:
                evaluation += ((sign * KNIGHT_VALUE)
                               + (sign * KNIGHT_TABLE[square]))

            elif piece_type == 2:
                evaluation += ((sign * BISHOP_VALUE)
                               + (sign * BISHOP_TABLE[square]))

            elif piece_type == 3:
                evaluation += ((sign * ROOK_VALUE)
                               + (sign * ROOK_TABLE[square]))

            elif piece_type == 4:
                evaluation += ((sign * QUEEN_VALUE)
                               + (sign * QUEEN_TABLE[square]))

            elif piece_type == 5:
                evaluation += ((sign * KING_VALUE)
                               + (sign * KING_TABLE[square]))

            # Clear the LSB to move to the next piece
            pieces &= pieces - 1
        
    if board.castling_rights & (0b11 << (board.color * 2)):
        evaluation += (5 if color else -5)

    return evaluation

def update_depth(gamestate):
    color = gamestate.turn

    pieces_remaining_score = 0

    for piece_type in range(5):
        # int.popbits (?) population bits - only 3.10 +
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
        return 4
    
    else:
        return 3
    
def is_position_quiet(board):
    DIRECTIONS = [
            (1, 1), (1, -1), (-1, 1), (-1, -1),
            (1, 0), (-1, 0), (0, 1), (0, -1)
            ]
    KNIGHT_JUMPS = [
        (2, 1), (1, 2), (-2, 1), (-1, 2),
        (2, -1), (1, -2), (-2, -1), (-1, -2)
    ]

    color = board.color
    pieces = board.occupants[color]
    while pieces:
        piece_square = tools.bitscan_lsb(pieces)
        rank, file = divmod(piece_square, 8)

        for k in KNIGHT_JUMPS:
            new_rank, new_file = rank + k[0], file + k[1]
            while (0 <= new_rank < 8 and 0 <= new_file < 8):
                new_square = 8 * new_rank + new_file
                if board.bitboards[1 + (1 - color) * 6] & (1 << new_square):
                    return False
                new_rank += k[0]
                new_file += k[1]
                
        if color:
            if board.bitboards[0] & (1 << (piece_square - 9)):
                if file != 7:
                    return False
            if board.bitboards[0] & (1 << (piece_square - 7)):
                if file != 0:
                    return False
        else:
            if board.bitboards[6] & (1 << (piece_square + 7)):
                if file != 7:
                    return False
            if board.bitboards[6] & (1 << (piece_square + 9)):
                if file != 0:
                    return False
                    
        for d in DIRECTIONS:
            new_rank, new_file = rank + d[0], file + d[1]
            while (0 <= new_rank < 8 and 0 <= new_file < 8):
                new_square = 8 * new_rank + new_file
                if board.occupants[color] & (1 << new_square):
                    break
                if board.occupants[1 - color] & (1 << new_square):
                    if (board.bitboards[4 + (1 - color) * 6] & (1 << new_square)):
                        return False
                    if ((board.bitboards[2 + (1 - color) * 6] & (1 << new_square)) and
                        abs(d[0]) == abs(d[1])):
                        return False
                    if ((board.bitboards[3 + (1 - color) * 6] & (1 << new_square)) and
                        (not d[0] or not d[1])):
                        return False
                    else:
                        break
                new_rank += d[0]
                new_file += d[1]
        pieces &= pieces - 1
    return True
    