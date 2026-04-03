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

# Precomputed knight attack table: for each square, a bitboard of attacked squares
KNIGHT_ATTACKS = [0] * 64
for _sq in range(64):
    _rank, _file = divmod(_sq, 8)
    for _dr, _df in ((2, 1), (2, -1), (-2, 1), (-2, -1),
                      (1, 2), (1, -2), (-1, 2), (-1, -2)):
        _nr, _nf = _rank + _dr, _file + _df
        if 0 <= _nr < 8 and 0 <= _nf < 8:
            KNIGHT_ATTACKS[_sq] |= 1 << (_nr * 8 + _nf)

# Castled king squares (g1=6, c1=2, g8=62, c8=58)
_CASTLED_SQUARES = frozenset((6, 2, 62, 58))

# Center files d(3) and e(4)
_CENTER_FILES = frozenset((3, 4))

# Mobility bonuses per piece type
_MOBILITY_KNIGHT = 4
_MOBILITY_BISHOP = 3
_MOBILITY_ROOK = 2
_MOBILITY_QUEEN = 1

# Ray directions for sliding pieces
_BISHOP_DIRS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
_ROOK_DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))

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
    """Evaluate king safety: pawn shield, open files, castled bonus, center penalty.

    All terms are scaled by game phase so they matter in the middlegame
    but fade to zero in the endgame.
    """
    if phase < 0.2:  # Skip in deep endgame
        return 0

    score = 0
    king_sq = tools.bitscan_lsb(board.bitboards[5 + color * 6])
    king_file = king_sq & 7
    king_rank = king_sq >> 3
    own_pawns = board.bitboards[0 + color * 6]
    enemy_pawns = board.bitboards[0 + (1 - color) * 6]

    # --- Pawn shield: +15 per friendly pawn on the rank directly in front ---
    shield_rank = king_rank + (1 if color == 0 else -1)
    shield_count = 0
    if 0 <= shield_rank < 8:
        for f in range(max(0, king_file - 1), min(8, king_file + 2)):
            shield_sq = shield_rank * 8 + f
            if own_pawns & (1 << shield_sq):
                score += 15
                shield_count += 1

    # --- Castled king bonus: +40 if king on a castled square with >= 2 shield pawns ---
    if king_sq in _CASTLED_SQUARES and shield_count >= 2:
        score += 40

    # --- Open and semi-open file penalties near king ---
    for f in range(max(0, king_file - 1), min(8, king_file + 2)):
        file_mask = FILE_MASKS[f]
        own_on_file = own_pawns & file_mask
        enemy_on_file = enemy_pawns & file_mask
        if not own_on_file:
            if not enemy_on_file:
                score -= 25  # Fully open file
            else:
                score -= 15  # Semi-open file (only enemy pawns)

    # --- Center file penalty: -30 if king sits on d or e file in middlegame ---
    if king_file in _CENTER_FILES:
        score -= 30

    return int(score * phase)


def _eval_mobility(board, color):
    """Evaluate piece mobility using inline ray casting (no MoveGenerator).

    Knights: precomputed attack table, +4 per non-friendly square.
    Bishops: diagonal ray cast, +3 per reachable square.
    Rooks:   orthogonal ray cast, +2 per reachable square.
    Queens:  combined rays, +1 per reachable square.
    """
    score = 0
    friendly = board.occupants[color]
    all_occ = board.occupants[2]

    # --- Knights ---
    knights = board.bitboards[1 + color * 6]
    while knights:
        sq = tools.bitscan_lsb(knights)
        # Use precomputed table; count squares not occupied by friendly pieces
        attacks = KNIGHT_ATTACKS[sq] & ~friendly
        # Popcount via Kernighan
        temp = attacks
        while temp:
            score += _MOBILITY_KNIGHT
            temp &= temp - 1
        knights &= knights - 1

    # --- Bishops (diagonal ray cast) ---
    bishops = board.bitboards[2 + color * 6]
    while bishops:
        sq = tools.bitscan_lsb(bishops)
        rank = sq >> 3
        file = sq & 7
        for dr, df in _BISHOP_DIRS:
            r, f = rank + dr, file + df
            while 0 <= r < 8 and 0 <= f < 8:
                target = r * 8 + f
                target_bit = 1 << target
                if friendly & target_bit:
                    break  # Blocked by own piece
                score += _MOBILITY_BISHOP
                if all_occ & target_bit:
                    break  # Captured enemy piece, can't go further
                r += dr
                f += df
        bishops &= bishops - 1

    # --- Rooks (orthogonal ray cast) ---
    rooks = board.bitboards[3 + color * 6]
    while rooks:
        sq = tools.bitscan_lsb(rooks)
        rank = sq >> 3
        file = sq & 7
        for dr, df in _ROOK_DIRS:
            r, f = rank + dr, file + df
            while 0 <= r < 8 and 0 <= f < 8:
                target = r * 8 + f
                target_bit = 1 << target
                if friendly & target_bit:
                    break
                score += _MOBILITY_ROOK
                if all_occ & target_bit:
                    break
                r += dr
                f += df
        rooks &= rooks - 1

    # --- Queens (combined bishop + rook rays, lower weight) ---
    queens = board.bitboards[4 + color * 6]
    while queens:
        sq = tools.bitscan_lsb(queens)
        rank = sq >> 3
        file = sq & 7
        # All 8 directions
        for dr, df in _BISHOP_DIRS + _ROOK_DIRS:
            r, f = rank + dr, file + df
            while 0 <= r < 8 and 0 <= f < 8:
                target = r * 8 + f
                target_bit = 1 << target
                if friendly & target_bit:
                    break
                score += _MOBILITY_QUEEN
                if all_occ & target_bit:
                    break
                r += dr
                f += df
        queens &= queens - 1

    return score


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

    # Piece mobility
    evaluation += _eval_mobility(board, 0)
    evaluation -= _eval_mobility(board, 1)

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
