import tools

def generate_pawn_scope(from_square, color):
        """Returns pawn's scope given a square."""
        candidate = []

        file = from_square % 8
        direction = [-7, -9] if color else [9, 7]

        if file == 0:
            candidate.append(from_square + direction[0])
        elif file == 7:
            candidate.append(from_square + direction[1])
        else:
            candidate.extend([from_square + d for d in direction])
        
        return candidate

def generate_knight_scope(from_square):
    """Returns knight's scope given a square."""
    candidate = []
    rank, file = divmod(from_square, 8)

    # Possible relative moves for a knight
    direction = [
        (2, 1), (1, 2),
        (-2, 1), (-1, 2),
        (2, -1), (1, -2),
        (-2, -1), (-1, -2)
    ]

    for d in direction:
        new_rank, new_file = rank + d[0], file + d[1]

        # Check if the new square is within the board boundaries
        if 0 <= new_rank < 8 and 0 <= new_file < 8:
            candidate.append(8 * new_rank + new_file)
    return candidate

def can_castle(board, color) -> bool:
    bitboards = board.bitboards
    occupants = board.occupants
    castling_rights = board.castling_rights

    kingside, queenside = False, False
    # King cannot castle while in check
    #if is_in_check(bitboards, color):
    #    return False, False
    if color == 0:
        if castling_rights & (1 << 0):
            # We only check if the castle through square is in check, because the resulting position will be illegal if the destination square is in check
            if not occupants[2] & (0b11 << 5):
                if not is_square_attacked(board, 5, color) and not is_square_attacked(board, 6, color):
                    kingside = True
        if castling_rights & (1 << 1):
            if not occupants[2] & (0b111 << 1):
                if not is_square_attacked(board, 3, color) and not is_square_attacked(board, 2, color):
                    queenside = True
    elif color == 1:
        if castling_rights & (1 << 2):
            if not occupants[2] & (0b11 << 61):
                if not is_square_attacked(board, 61, color) and not is_square_attacked(board, 62, color):
                    kingside = True
        
        if castling_rights & (1 << 3):
            if not occupants[2] & (0b111 << 57):
                if not is_square_attacked(board, 59, color) and not is_square_attacked(board, 58, color):
                    queenside = True

    return kingside, queenside

def is_square_attacked(board, square, color):
    for piece_type in range(6):
        pieces = board.bitboards[piece_type + (1 - color)*6]
        while pieces:
            from_square = tools.bitscan_lsb(pieces)
            if piece_type == 0:
                if color == 0:
                    if square + 10 <= tools.bitscan_lsb(pieces):
                        pieces = 0
                        continue
                elif color == 1:
                    if square - 10 >= tools.bitscan_msb(pieces):
                        pieces = 0
                        continue
                if is_in_pawn_scope(from_square, square, 1 - color):
                    return True
            elif piece_type == 1 and is_in_knight_scope(from_square, square):
                return True
            elif piece_type == 2 and is_in_bishop_scope(board, from_square, square):
                return True
            elif piece_type == 3 and is_in_rook_scope(board, from_square, square):
                return True
            elif piece_type == 4 and is_in_queen_scope(board, from_square, square):
                return True
            elif piece_type == 5 and is_in_king_scope(from_square, square):
                return True
            pieces &= pieces - 1
    return False


def is_in_bishop_scope(board, attacker_square, target_square) -> bool:
    attacker_rank, attacker_file = divmod(attacker_square, 8)
    target_rank, target_file = divmod(target_square, 8)

    if abs(attacker_rank - target_rank) != abs(attacker_file - target_file):
        return False

    rank_increment = 1 if target_rank > attacker_rank else -1
    file_increment = 1 if target_file > attacker_file else -1

    current_rank, current_file = attacker_rank + rank_increment, attacker_file + file_increment
    while current_rank != target_rank:
        if current_rank >= 8 or current_rank < 0 or current_file >= 8 or current_file < 0:
            return False
        current_square = 8 * current_rank + current_file
        if (board.occupants[2] & (1 << current_square)):
            return False
        current_rank += rank_increment
        current_file += file_increment

    return True

def is_in_rook_scope(board, attacker_square, target_square) -> bool:
    attacker_rank, attacker_file = divmod(attacker_square, 8)
    target_rank, target_file = divmod(target_square, 8)

    # Must be same rank or same file
    if attacker_rank != target_rank and attacker_file != target_file:
        return False

    if attacker_rank == target_rank:  # Moving horizontally
        file_increment = 1 if target_file > attacker_file else -1
        current_file = attacker_file + file_increment
        while current_file != target_file:
            current_square = 8 * attacker_rank + current_file
            if (board.occupants[2] & (1 << current_square)):
                # There is a piece in the path of the rook
                return False
            current_file += file_increment
    else:  # Moving vertically
        rank_increment = 1 if target_rank > attacker_rank else -1
        current_rank = attacker_rank + rank_increment
        while current_rank != target_rank:
            current_square = 8 * current_rank + attacker_file
            if (board.occupants[2] & (1 << current_square)):
                # There is a piece in the path of the rook
                return False
            current_rank += rank_increment

    return True

def is_in_queen_scope(bitboards, attacker_square, target_square) -> bool:
    return is_in_bishop_scope(bitboards, attacker_square, target_square) or is_in_rook_scope(bitboards, attacker_square, target_square)

def is_in_king_scope(attacker_square, target_square) -> bool:
    attacker_rank, attacker_file = divmod(attacker_square, 8)
    target_rank, target_file = divmod(target_square, 8)

    return (abs(target_file - attacker_file) <= 1) and (abs(target_rank - attacker_rank) <= 1)

def generate_king_scope(from_square):
    """Returns king's scope given a square."""
    candidate = []
    rank, file = divmod(from_square, 8)

    # Possible relative moves for a king
    direction = [
        (1, 1), (1, 0), (1, -1),
        (0, 1), (0, -1),
        (-1, 1), (-1, 0), (-1, -1)
    ]

    for d in direction:
        new_rank, new_file = rank + d[0], file + d[1]

        # Check if the new square is within the board boundaries
        if 0 <= new_rank < 8 and 0 <= new_file < 8:
            candidate.append(8 * new_rank + new_file)
    return candidate

def is_in_pawn_scope(attacker_square, target_square, color) -> bool:

    attacker_rank, attacker_file = divmod(attacker_square, 8)
    target_rank, target_file = divmod(target_square, 8)

    return (abs(target_file - attacker_file) == 1) and ((target_rank - attacker_rank) == (1 if color == 0 else -1))

def is_in_knight_scope(attacker_square, target_square) -> bool:
    rank_diff = abs((attacker_square // 8) - (target_square // 8))
    file_diff = abs((attacker_square % 8) - (target_square % 8))

    return (rank_diff == 1 and file_diff == 2) or (rank_diff == 2 and file_diff == 1)