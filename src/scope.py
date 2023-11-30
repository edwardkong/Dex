import board, tools

def get_scope_from_square(board, from_square, color, piece_type):
    if piece_type == 0:
        return generate_pawn_scope(from_square, color)
    elif piece_type == 1:
        return generate_knight_scope(from_square)
    elif piece_type in (2, 3, 4):
        return generate_sliding_scope(board.occupants, from_square, color, piece_type)
    elif piece_type == 5:
        return generate_king_scope(from_square)

def generate_moves(bitboards, color):
    moves = []
    
    # Iterate through all pieces of the given color
    for piece_type in range(6):
        pieces = bitboards[piece_type + color*6]
        while pieces:
            # Find the index of the least significant set bit (LSB)
            from_square = tools.bitscan_lsb(pieces)
            
            # Generate moves for the current piece
            piece_moves = generate_piece_moves(bitboards, piece_type, from_square, color)
            
            # Add the moves to the list
            moves.extend(piece_moves)

            # Clear the LSB to move to the next piece
            pieces &= pieces - 1
    
    return moves

def generate_psuedo_moves(board, piece_type, from_square, color):
    moves = []
    bitboards = board.bitboards

    # Implement move generation logic for each piece type
    if piece_type == 0:  # Pawn
        for candidate in generate_pawn_moves(bitboards, from_square, color):
            if type(candidate) == str:
                promo_piece = tools.char_to_int_piece(candidate[-1])
                move = from_square | (int(candidate[:-1]) << 6) | (promo_piece << 12) | (color << 15)
            else:
                move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
    elif piece_type == 1:  # Knight
        for candidate in generate_knight_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            
    elif piece_type == 2:  # Bishop
        for candidate in generate_bishop_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            
    elif piece_type == 3:  # Rook
        for candidate in generate_rook_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
    elif piece_type == 4:  # Queen
        for candidate in generate_queen_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            moves.append(move)
    elif piece_type == 5: # King
        for candidate in generate_king_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            moves.append(move)
    return moves


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

def generate_sliding_scope(occupants, from_square, color, piece_type):
        """
        Takes a board's occupants.
        Returns sliding piece's scope given a square. piece_type -> {2: Bishop, 3: Rook, 4: Queen}
        """
        candidate = []
        rank, file = divmod(from_square, 8)

        # Possible relative moves for a sliding piece
        sliding_moves = [
            (1, 1), (1, -1), (-1, 1), (-1, -1),
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]
        if piece_type == 2:
            directions = sliding_moves[:4]
        elif piece_type == 3:
            directions = sliding_moves[4:]
        elif piece_type == 4:
            directions = sliding_moves

        for d in directions:
            new_rank, new_file = rank + move[0], file + move[1]
            while 0 <= new_rank < 8 and 0 <= new_file < 8:
                new_square = 8 * new_rank + new_file
                # Square occupied
                if (occupants[2] & (1 << new_square)):
                    candidate.append(new_square)
                else:
                    candidate.append(new_square)
                    rank, file = new_rank + move[0], new_file + move[1]
        return candidate

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

# If color = white, checks if attacked by black
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


def can_castle(board, color) -> bool:
    bitboards = board.bitboards
    occupants = board.occupants
    castling_rights = board.castling_rights

    kingside, queenside = False, False
    # King cannot castle while in check
    #if is_in_check(bitboards, color):
    #    return False, False
    if color == 0:
        if castling_rights & (1 << 3):
            # We only check if the castle through square is in check, because the resulting position will be illegal if the destination square is in check
            if not occupants[1] & (0b11 << 5):
                if is_square_attacked(board, 5, color) or is_square_attacked(board, 6, color):
                    kingside = False
                else:
                    kingside = True
        
        if castling_rights & (1 << 2):
            if not occupants[1] & (0b11 << 1):
                if is_square_attacked(board, 3, color) or is_square_attacked(board, 2, color):
                    queenside = False
                else:
                    queenside = True
    elif color == 1:
        if castling_rights & (1 << 1):
            if not occupants[0] & (0b11 << 61):
                if is_square_attacked(board, 61, color) or is_square_attacked(board, 62, color):
                    kingside = False
                else:
                    kingside = True
        
        if castling_rights & (1 << 0):
            if not occupants[0] & (0b11 << 57):
                if is_square_attacked(board, 59, color) or is_square_attacked(board, 58, color):
                    queenside = False
                else:
                    queenside = True
    
    return kingside, queenside
