import tools

# Piece values
PAWN_VALUE = 101
KNIGHT_VALUE = 316
BISHOP_VALUE = 329
ROOK_VALUE = 494
QUEEN_VALUE = 903
KING_VALUE = 20000

PIECE_VALUES = [PAWN_VALUE, KNIGHT_VALUE, BISHOP_VALUE, ROOK_VALUE, QUEEN_VALUE, KING_VALUE]

# Piece square tables
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     50, 50, 50, 50, 50, 50, 50, 50,
     10, 10, 20, 35, 35, 20, 10, 10,
     5,  5, 10, 27, 27, 10,  5,  5,
     0,  0,  0, 23, 23,  0,  0,  0,
     7, -4,-10,  0,  0,-10, -4,  7,
     6, 11, 13,-23,-23, 13, 11,  6,
     0,  0,  0,  0,  0,  0,  0,  0
]

PAWN_TABLE_END = [
    0,   0,   0,   0,   0,   0,   0,   0,
    80,  80,  80,  80,  80,  80,  80,  80,
    50,  50,  50,  50,  50,  50,  50,  50,
    30,  30,  30,  30,  30,  30,  30,  30,
    20,  20,  20,  20,  20,  20,  20,  20,
    10,  10,  10,  10,  10,  10,  10,  10,
    10,  10,  10,  10,  10,  10,  10,  10,
    0,   0,   0,   0,   0,   0,   0,   0
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
    -10, 11,  0,  0,  0,  0, 11,-10,
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
    -5,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  5,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
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
]

KING_TABLE_END = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -5,   0,   5,   5,   5,   5,   0,  -5,
    -10, -5,   20,  30,  30,  20,  -5, -10,
    -15, -10,  35,  45,  45,  35, -10, -15,
    -20, -15,  30,  40,  40,  30, -15, -20,
    -25, -20,  20,  25,  25,  20, -20, -25,
    -30, -25,   0,   0,   0,   0, -25, -30,
    -50, -30, -30, -30, -30, -30, -30, -50
]

PIECE_TABLES = [PAWN_TABLE, KNIGHT_TABLE, BISHOP_TABLE, ROOK_TABLE, QUEEN_TABLE, KING_TABLE]
PIECE_TABLES_END = [PAWN_TABLE_END, KNIGHT_TABLE, BISHOP_TABLE, ROOK_TABLE, QUEEN_TABLE, KING_TABLE_END]

# File masks for pawn structure evaluation
FILE_MASKS = [0x0101010101010101 << f for f in range(8)]
ADJACENT_FILE_MASKS = [0] * 8
for f in range(8):
    if f > 0:
        ADJACENT_FILE_MASKS[f] |= FILE_MASKS[f - 1]
    if f < 7:
        ADJACENT_FILE_MASKS[f] |= FILE_MASKS[f + 1]

# Passed pawn bonus by rank (from white's perspective, index = rank 0-7)
PASSED_PAWN_BONUS = [0, 10, 10, 20, 40, 60, 80, 0]

GAME_PHASE = 0

# Total non-pawn material at game start (for tapered eval phase calculation)
STARTING_MATERIAL = 2 * (KNIGHT_VALUE + BISHOP_VALUE + ROOK_VALUE + QUEEN_VALUE)


def _compute_phase(board):
    """Compute game phase from 0.0 (endgame) to 1.0 (opening)."""
    material = 0
    for piece_type in range(1, 5):  # N, B, R, Q only
        for color in range(2):
            pieces = board.bitboards[piece_type + color * 6]
            while pieces:
                material += PIECE_VALUES[piece_type]
                pieces &= pieces - 1
    return min(material / STARTING_MATERIAL, 1.0)


def _eval_pawn_structure(board, color):
    """Evaluate pawn structure: doubled, isolated, passed pawns."""
    score = 0
    pawns = board.bitboards[0 + color * 6]
    enemy_pawns = board.bitboards[0 + (1 - color) * 6]

    for f in range(8):
        file_pawns = pawns & FILE_MASKS[f]
        if not file_pawns:
            continue

        # Doubled pawns: more than one pawn on same file
        count = 0
        temp = file_pawns
        while temp:
            count += 1
            temp &= temp - 1
        if count > 1:
            score -= 15 * (count - 1)

        # Isolated pawns: no friendly pawns on adjacent files
        if not (pawns & ADJACENT_FILE_MASKS[f]):
            score -= 20

    # Passed pawns
    temp_pawns = pawns
    while temp_pawns:
        sq = tools.bitscan_lsb(temp_pawns)
        rank = sq >> 3
        file = sq & 7

        # A pawn is passed if no enemy pawns on same or adjacent files ahead
        is_passed = True
        if color == 0:  # White
            for r in range(rank + 1, 7):
                check_sq_mask = 0
                if file > 0:
                    check_sq_mask |= 1 << (r * 8 + file - 1)
                check_sq_mask |= 1 << (r * 8 + file)
                if file < 7:
                    check_sq_mask |= 1 << (r * 8 + file + 1)
                if enemy_pawns & check_sq_mask:
                    is_passed = False
                    break
            if is_passed:
                score += PASSED_PAWN_BONUS[rank]
        else:  # Black
            for r in range(rank - 1, 0, -1):
                check_sq_mask = 0
                if file > 0:
                    check_sq_mask |= 1 << (r * 8 + file - 1)
                check_sq_mask |= 1 << (r * 8 + file)
                if file < 7:
                    check_sq_mask |= 1 << (r * 8 + file + 1)
                if enemy_pawns & check_sq_mask:
                    is_passed = False
                    break
            if is_passed:
                score += PASSED_PAWN_BONUS[7 - rank]

        temp_pawns &= temp_pawns - 1

    return score


def _eval_king_safety(board, color, phase):
    """Evaluate king safety: pawn shield bonus (scaled by phase)."""
    if phase < 0.3:  # Skip in endgame
        return 0

    score = 0
    king_sq = tools.bitscan_lsb(board.bitboards[5 + color * 6])
    king_file = king_sq & 7
    king_rank = king_sq >> 3
    pawns = board.bitboards[0 + color * 6]

    # Check pawn shield (pawns on 2nd/3rd rank in front of king)
    shield_rank = king_rank + (1 if color == 0 else -1)
    if 0 <= shield_rank < 8:
        for f in range(max(0, king_file - 1), min(8, king_file + 2)):
            shield_sq = shield_rank * 8 + f
            if pawns & (1 << shield_sq):
                score += 10

    # Penalty for open files near king
    for f in range(max(0, king_file - 1), min(8, king_file + 2)):
        if not (pawns & FILE_MASKS[f]):
            score -= 15

    return int(score * phase)


def _eval_pieces(board, color):
    """Evaluate piece-specific bonuses: bishop pair, rook on open file."""
    score = 0
    pawns_w = board.bitboards[0]
    pawns_b = board.bitboards[6]

    # Bishop pair
    bishops = board.bitboards[2 + color * 6]
    if bishops and (bishops & (bishops - 1)):  # More than one bishop
        score += 30

    # Rook on open/semi-open file
    rooks = board.bitboards[3 + color * 6]
    own_pawns = board.bitboards[0 + color * 6]
    enemy_pawns = board.bitboards[0 + (1 - color) * 6]
    while rooks:
        sq = tools.bitscan_lsb(rooks)
        f = sq & 7
        if not (own_pawns & FILE_MASKS[f]):
            if not (enemy_pawns & FILE_MASKS[f]):
                score += 25  # Open file
            else:
                score += 15  # Semi-open file
        rooks &= rooks - 1

    return score


def is_insufficient_material(board):
    """Check if neither side can checkmate: K vs K, K+B vs K, K+N vs K."""
    # Any pawns, rooks, or queens means sufficient material
    for color in range(2):
        if board.bitboards[0 + color * 6]:  # Pawns
            return False
        if board.bitboards[3 + color * 6]:  # Rooks
            return False
        if board.bitboards[4 + color * 6]:  # Queens
            return False

    # Count minor pieces (knights + bishops)
    total_minors = 0
    for color in range(2):
        knights = board.bitboards[1 + color * 6]
        bishops = board.bitboards[2 + color * 6]
        while knights:
            total_minors += 1
            knights &= knights - 1
        while bishops:
            total_minors += 1
            bishops &= bishops - 1

    # K vs K, or K+minor vs K
    return total_minors <= 1


def push_king(board):
    enemy_king_square = tools.bitscan_lsb(board.bitboards[5 + (1 - board.color) * 6])
    e_rank = enemy_king_square >> 3
    e_file = enemy_king_square & 7
    rank_score = abs(e_rank * 2 - 7)
    file_score = abs(e_file * 2 - 7)
    return rank_score + file_score


def evaluate_board(board):
    evaluation = 0

    # Compute game phase for tapered eval
    phase = _compute_phase(board)

    # Select piece-square tables based on phase
    if phase > 0.5:
        pst = PIECE_TABLES
    else:
        pst = PIECE_TABLES_END

    # Endgame king push
    if phase < 0.15:
        evaluation += push_king(board) * 15

    # Material + PST
    for piece in range(12):
        piece_type = piece % 6
        color = piece // 6
        pieces = board.bitboards[piece]
        sign = -1 if color else 1

        while pieces:
            square = tools.bitscan_lsb(pieces)
            table_sq = (63 - square) if not color else square
            evaluation += sign * (PIECE_VALUES[piece_type] + pst[piece_type][table_sq])
            pieces &= pieces - 1

    # Pawn structure
    evaluation += _eval_pawn_structure(board, 0)
    evaluation -= _eval_pawn_structure(board, 1)

    # King safety
    evaluation += _eval_king_safety(board, 0, phase)
    evaluation -= _eval_king_safety(board, 1, phase)

    # Piece bonuses (bishop pair, rook on open file)
    evaluation += _eval_pieces(board, 0)
    evaluation -= _eval_pieces(board, 1)

    # Return relative to side to move
    return evaluation if board.color == 0 else -evaluation


def update_depth(gamestate):
    global GAME_PHASE
    depth = gamestate.depth
    pieces_remaining_score = 0

    piece_values = [PAWN_VALUE, KNIGHT_VALUE, BISHOP_VALUE, ROOK_VALUE, QUEEN_VALUE]

    for color in range(2):
        for piece_type in range(5):
            num_pieces = bin(gamestate.board.bitboards[piece_type + color * 6]).count('1')
            pieces_remaining_score += num_pieces * piece_values[piece_type]

    if pieces_remaining_score <= 600:
        depth = 6
        phase = 3
    elif pieces_remaining_score <= 2000:
        depth = 5
        phase = 2
    elif pieces_remaining_score <= 4000:
        depth = 5
        phase = 1
    else:
        depth = 5
        phase = 0

    GAME_PHASE = phase
    return depth, phase
