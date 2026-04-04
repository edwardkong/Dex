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

# Endgame-specific tables for pieces (centralization matters more)
KNIGHT_TABLE_END = [
    -50,-30,-30,-30,-30,-30,-30,-50,
    -30,-20,  0,  0,  0,  0,-20,-30,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 25, 25, 15,  5,-30,
    -30,  5, 15, 25, 25, 15,  5,-30,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,-20,  0,  0,  0,  0,-20,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]

BISHOP_TABLE_END = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  0, 10, 15, 15, 10,  0,-10,
    -10,  0, 10, 15, 15, 10,  0,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE_END = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE_END = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -5,  5, 10, 15, 15, 10,  5, -5,
    -5,  5, 10, 15, 15, 10,  5, -5,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

PIECE_TABLES_MG = [PAWN_TABLE, KNIGHT_TABLE, BISHOP_TABLE, ROOK_TABLE, QUEEN_TABLE, KING_TABLE]
PIECE_TABLES_EG = [PAWN_TABLE_END, KNIGHT_TABLE_END, BISHOP_TABLE_END, ROOK_TABLE_END, QUEEN_TABLE_END, KING_TABLE_END]

# Keep old names for compatibility
PIECE_TABLES = PIECE_TABLES_MG
PIECE_TABLES_END = PIECE_TABLES_EG

# File and edge masks
FILE_A = 0x0101010101010101
FILE_H = 0x8080808080808080

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

# Mobility bonuses per piece type (kept small to avoid overriding material)
_MOBILITY_KNIGHT = 2
_MOBILITY_BISHOP = 2
_MOBILITY_ROOK = 1
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


def _compute_pawn_attacks(board, color):
    """Compute the set of squares attacked by pawns of the given color.

    White pawns attack NE (+9) and NW (+7); black pawns attack SE (-7) and SW (-9).
    Edge files are masked out to prevent wrap-around.
    """
    pawns = board.bitboards[0 + color * 6]
    if color == 0:  # White
        return ((pawns << 7) & ~FILE_H) | ((pawns << 9) & ~FILE_A)
    else:  # Black
        return ((pawns >> 9) & ~FILE_H) | ((pawns >> 7) & ~FILE_A)


def _compute_minor_attacks(board, color):
    """Compute the set of squares attacked by knights and bishops of the given color."""
    attacks = 0
    all_occ = board.occupants[2]

    # Knight attacks
    knights = board.bitboards[1 + color * 6]
    while knights:
        sq = tools.bitscan_lsb(knights)
        attacks |= KNIGHT_ATTACKS[sq]
        knights &= knights - 1

    # Bishop attacks (ray cast)
    bishops = board.bitboards[2 + color * 6]
    while bishops:
        sq = tools.bitscan_lsb(bishops)
        rank = sq >> 3
        file = sq & 7
        for dr, df in _BISHOP_DIRS:
            r, f = rank + dr, file + df
            while 0 <= r < 8 and 0 <= f < 8:
                target_bit = 1 << (r * 8 + f)
                attacks |= target_bit
                if all_occ & target_bit:
                    break
                r += dr
                f += df
        bishops &= bishops - 1

    return attacks


def _count_mobility(board, color, piece_type_idx, unsafe_mask=0):
    """Count available squares for a piece type using ray casting.

    Squares in unsafe_mask are excluded -- these are squares attacked by
    lower-value enemy pieces where the piece would be liable to be chased away.
    """
    friendly = board.occupants[color]
    all_occ = board.occupants[2]
    total_squares = 0

    if piece_type_idx == 1:  # Knights
        pieces = board.bitboards[1 + color * 6]
        while pieces:
            sq = tools.bitscan_lsb(pieces)
            # Exclude friendly pieces and unsafe squares
            safe_attacks = KNIGHT_ATTACKS[sq] & ~friendly & ~unsafe_mask
            temp = safe_attacks
            while temp:
                total_squares += 1
                temp &= temp - 1
            pieces &= pieces - 1
    elif piece_type_idx in (2, 3, 4):  # Bishops, Rooks, Queens
        pieces = board.bitboards[piece_type_idx + color * 6]
        if piece_type_idx == 2:
            dirs = _BISHOP_DIRS
        elif piece_type_idx == 3:
            dirs = _ROOK_DIRS
        else:
            dirs = _BISHOP_DIRS + _ROOK_DIRS
        while pieces:
            sq = tools.bitscan_lsb(pieces)
            rank = sq >> 3
            file = sq & 7
            for dr, df in dirs:
                r, f = rank + dr, file + df
                while 0 <= r < 8 and 0 <= f < 8:
                    target_bit = 1 << (r * 8 + f)
                    if friendly & target_bit:
                        break
                    # Only count squares not attacked by lower-value pieces
                    if not (unsafe_mask & target_bit):
                        total_squares += 1
                    if all_occ & target_bit:
                        break
                    r += dr
                    f += df
            pieces &= pieces - 1

    return total_squares


# Average safe mobility for each piece type (baseline for scaling).
# These are slightly lower than raw mobility averages because unsafe
# squares are now excluded from the count.
_AVG_MOBILITY = {1: 4, 2: 6, 3: 6, 4: 9}


def _eval_mobility(board, color):
    """Evaluate safe mobility as a scaling factor on piece value.

    Only squares NOT attacked by lower-value enemy pieces count toward
    a piece's mobility.  This naturally penalizes pieces that venture
    into territory controlled by enemy pawns or minors (e.g. an early
    queen sortie) and rewards pieces on safe, stable squares.

    Scaling: 2% of piece value per square above/below average.
    """
    enemy = 1 - color

    # Compute enemy pawn attack mask (squares attacked by enemy pawns)
    enemy_pawn_attacks = _compute_pawn_attacks(board, enemy)

    # Compute enemy minor attack mask (squares attacked by enemy knights/bishops)
    enemy_minor_attacks = _compute_minor_attacks(board, enemy)

    # Combined mask of squares attacked by enemy pawns OR minors
    enemy_pawn_and_minor_attacks = enemy_pawn_attacks | enemy_minor_attacks

    score = 0
    for piece_type_idx in (1, 2, 3, 4):
        pieces = board.bitboards[piece_type_idx + color * 6]
        if not pieces:
            continue

        # Determine which squares are unsafe for this piece type:
        # - Knights/Bishops: exclude squares attacked by enemy pawns
        # - Rooks: exclude squares attacked by enemy pawns
        # - Queens: exclude squares attacked by enemy pawns OR minors
        if piece_type_idx in (1, 2, 3):
            unsafe = enemy_pawn_attacks
        else:  # Queen
            unsafe = enemy_pawn_and_minor_attacks

        squares = _count_mobility(board, color, piece_type_idx, unsafe)

        # Count pieces of this type
        count = 0
        temp = pieces
        while temp:
            count += 1
            temp &= temp - 1
        avg = _AVG_MOBILITY[piece_type_idx] * count
        diff = squares - avg
        # Scale mobility bonus by piece type:
        # Knights/bishops: 3% of value (~10cp/sq) — development matters most
        # Rooks: 2% of value (~10cp/sq)
        # Queens: 0.5% of value (~4.5cp/sq) — queens are naturally mobile,
        #   don't over-reward; let minor piece underdevelopment dominate
        divisor = {1: 33, 2: 33, 3: 50, 4: 200}[piece_type_idx]
        score += diff * PIECE_VALUES[piece_type_idx] // divisor
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

    # Rook bonuses
    rooks = board.bitboards[3 + color * 6]
    own_pawns = board.bitboards[0 + color * 6]
    enemy_pawns = board.bitboards[0 + (1 - color) * 6]
    seventh_rank = 6 if color == 0 else 1
    while rooks:
        sq = tools.bitscan_lsb(rooks)
        f = sq & 7
        r = sq >> 3
        # Rook on open/semi-open file
        if not (own_pawns & FILE_MASKS[f]):
            if not (enemy_pawns & FILE_MASKS[f]):
                score += 25  # Open file
            else:
                score += 15  # Semi-open file
        # Rook on 7th rank
        if r == seventh_rank:
            score += 25
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
    # Compute game phase for tapered eval (0.0 = endgame, 1.0 = opening)
    phase = _compute_phase(board)
    phase_int = int(phase * 256)

    # Tapered material + PST: interpolate between MG and EG scores
    mg_score = 0
    eg_score = 0

    for piece in range(12):
        piece_type = piece % 6
        color = piece // 6
        pieces = board.bitboards[piece]
        sign = -1 if color else 1

        while pieces:
            square = tools.bitscan_lsb(pieces)
            table_sq = (63 - square) if not color else square
            mat = sign * PIECE_VALUES[piece_type]
            mg_score += mat + sign * PIECE_TABLES_MG[piece_type][table_sq]
            eg_score += mat + sign * PIECE_TABLES_EG[piece_type][table_sq]
            pieces &= pieces - 1

    # Interpolate between middlegame and endgame
    evaluation = (mg_score * phase_int + eg_score * (256 - phase_int)) // 256

    # Endgame king push (mating with advantage)
    if phase < 0.15:
        evaluation += push_king(board) * 15

    # Pawn structure
    evaluation += _eval_pawn_structure(board, 0)
    evaluation -= _eval_pawn_structure(board, 1)

    # King safety (phase-scaled internally)
    evaluation += _eval_king_safety(board, 0, phase)
    evaluation -= _eval_king_safety(board, 1, phase)

    # Piece bonuses (bishop pair, rook on open file, rook on 7th)
    evaluation += _eval_pieces(board, 0)
    evaluation -= _eval_pieces(board, 1)

    # Piece mobility
    evaluation += _eval_mobility(board, 0)
    evaluation -= _eval_mobility(board, 1)

    # Tempo bonus: small advantage for having the move
    evaluation += 12

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
