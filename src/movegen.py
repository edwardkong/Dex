import game, position, tools, makemove

def generate_moves(board, color):
    moves = []
    
    if type(board) is list:
        bitboards = board
        castling_rights = {'WK': 0, 'WQ': 0, 'BK': 0, 'BQ': 0}
    else:
        bitboards = board.bitboards
        castling_rights = board.castling_rights
    

    # Iterate through all pieces of the given color
    for piece_type in range(6):
        pieces = bitboards[piece_type + color*6]
        while pieces:
            # Find the index of the least significant set bit (LSB)
            from_square = tools.bitscan_lsb(pieces)
            
            # Generate moves for the current piece
            piece_moves = generate_piece_moves(bitboards, piece_type, from_square, color, castling_rights)
            
            # Add the moves to the list
            moves.extend(piece_moves)

            # Clear the LSB to move to the next piece
            pieces &= pieces - 1
    
    return moves

def generate_all_moves(bitboards, piece_type, from_square, color, castling_rights, last_move = None):
    moves = []

    if piece_type == 0:  # Pawn
        for candidate in generate_pawn_moves(bitboards, from_square, color, last_move):
            if type(candidate) == str:
                promo_piece = tools.char_to_int_piece(candidate[-1])
                move = from_square | (int(candidate[:-1]) << 6) | (promo_piece << 12) | (color << 15)
            else:
                move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            moves.append(move)
    elif piece_type == 1:  # Knight
        for candidate in generate_knight_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            moves.append(move)
                    
    elif piece_type == 2:  # Bishop
        for candidate in generate_bishop_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            moves.append(move)
    elif piece_type == 3:  # Rook
        for candidate in generate_rook_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            moves.append(move)
    elif piece_type == 4:  # Queen
        for candidate in generate_queen_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            moves.append(move)
    elif piece_type == 5: # King
        for candidate in generate_king_moves(bitboards, from_square, color, castling_rights):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            moves.append(move)
    return moves


def generate_piece_moves(bitboards, piece_type, from_square, color, castling_rights, last_move = None):
    moves = []

    in_los = position.in_los(bitboards, color)
    in_check = position.is_in_check(bitboards, color)
    los_or_check = position.in_los(bitboards, color) or position.is_in_check(bitboards, color)

    # Implement move generation logic for each piece type
    # Verify if each move will put the king in check
    if piece_type == 0:  # Pawn
        for candidate in generate_pawn_moves(bitboards, from_square, color, last_move):
            if type(candidate) == str:
                promo_piece = tools.char_to_int_piece(candidate[-1])
                move = from_square | (int(candidate[:-1]) << 6) | (promo_piece << 12) | (color << 15)
            else:
                move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            if los_or_check:
                if position.is_legal_position(position.simulate_move(bitboards, move), 1 - color):
                    moves.append(move)
            else:
                moves.append(move)
    elif piece_type == 1:  # Knight
        for candidate in generate_knight_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            if los_or_check:
                if position.is_legal_position(position.simulate_move(bitboards, move), 1 - color):
                    moves.append(move)
            else:
                moves.append(move)
                    
    elif piece_type == 2:  # Bishop
        for candidate in generate_bishop_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            if los_or_check:
                if position.is_legal_position(position.simulate_move(bitboards, move), 1 - color):
                    moves.append(move)
            else:
                moves.append(move)
    elif piece_type == 3:  # Rook
        for candidate in generate_rook_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            if los_or_check:
                if position.is_legal_position(position.simulate_move(bitboards, move), 1 - color):
                    moves.append(move)
            else:
                moves.append(move)
    elif piece_type == 4:  # Queen
        for candidate in generate_queen_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            if los_or_check:
                if position.is_legal_position(position.simulate_move(bitboards, move), 1 - color):
                    moves.append(move)
            else:
                moves.append(move)
    elif piece_type == 5: # King
        for candidate in generate_king_moves(bitboards, from_square, color, castling_rights):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            if position.is_legal_position(position.simulate_move(bitboards, move), 1 - color):
                moves.append(move)
    return moves

def generate_pawn_moves(bitboards, from_square, color, last_move = None):
    candidate = []
    rank, file = divmod(from_square, 8)
    
    # Single step forward
    if 1 <= rank < 7:
        step_square = from_square + 8 if color == 0 else from_square - 8
        if not (bitboards[14] & (1 << step_square)):
            # Single step promotion
            if (color == 0 and rank == 6) or (color == 1 and rank == 1):
                for promo in "nbrq":
                    candidate.append(f"{step_square}{promo}")
            else:
                candidate.append(step_square)
            # Double step forward
            if (color == 0 and rank == 1) or (color == 1 and rank == 6):
                to_square = from_square + 16 if color == 0 else from_square - 16
                if not (bitboards[14] & (1 << to_square)):
                    candidate.append(to_square)

    # Capture moves
    if color == 0:
        if file == 0:
            to_square = [from_square + 9]
        elif file == 7:
            to_square = [from_square + 7]
        else:
            to_square = [from_square + 7, from_square + 9]
    elif color == 1:
        if file == 0:
            to_square = [from_square - 7]
        elif file == 7:
            to_square = [from_square - 9]
        else:
            to_square = [from_square - 7, from_square - 9]

    for square in to_square:
        if (8 <= square < 56) and (bitboards[12 + (1 - color)] & (1 << square)):
            candidate.append(square)
        # Promo captures
        elif (56 <= square < 64) or (0 <= square < 8):
            for prom in "nbrq":
                candidate.append(f"{square}{prom}")

    ### En Passant
    # ! Implement try catch in case no last_move
    en_passant_legal = False
    try:
        if last_move is not None:
            last_move_from = ord(last_move[0]) - ord('a') + (int(last_move[1]) - 1) * 8
            last_move_to = ord(last_move[2]) - ord('a') + (int(last_move[3]) - 1) * 8
            if 24 <= from_square < 40:
                if abs(last_move_from - last_move_to) == 16:            
                    if bitboards[0 + (1 - color)*6] & (1 << last_move_to):
                        if last_move_to >=32 and from_square >= 32 and abs(last_move_to - from_square) == 1:
                            en_passant_legal = True
                        elif last_move_to < 32 and from_square < 32 and abs(last_move_to - from_square) == 1:
                            en_passant_legal = True
    except KeyError:
        pass

    if en_passant_legal:
        if color == 0:
            candidate.append(last_move_to + 8)
        else:
            candidate.append(last_move_to - 8)

    return candidate

def generate_knight_moves(bitboards, from_square, color):
    candidate = []
    current_rank, current_file = divmod(from_square, 8)

    # Possible relative moves for a knight
    knight_moves = [
        (2, 1), (1, 2),
        (-2, 1), (-1, 2),
        (2, -1), (1, -2),
        (-2, -1), (-1, -2)
    ]

    for move in knight_moves:
        new_rank, new_file = current_rank + move[0], current_file + move[1]
        new_square = 8 * new_rank + new_file

        # Check if the new square is within the board boundaries
        if 0 <= new_rank < 8 and 0 <= new_file < 8 and 0 <= new_square < 64:
            if not (bitboards[12 + color] & (1 << new_square)):
                candidate.append(new_square)
    return candidate

def generate_sliding_moves(bitboards, piece_type, from_square, color):
    # Implement generalized function for sliding pieces
    return

def generate_bishop_moves(bitboards, from_square, color):
    candidate = []
    current_rank, current_file = divmod(from_square, 8)

    # Possible relative moves for a bishop (diagonal)
    bishop_moves = [
        (1, 1), (1, -1),
        (-1, 1), (-1, -1)
    ]

    for move in bishop_moves:
        new_rank, new_file = current_rank + move[0], current_file + move[1]
        while 0 <= new_rank < 8 and 0 <= new_file < 8:
            new_square = 8 * new_rank + new_file
            # Square occupied
            if (bitboards[14] & (1 << new_square)):
                # Occupied by opponent piece
                if (bitboards[12 + (1 - color)] & (1 << new_square)):
                    candidate.append(new_square)
                break
            else:
                candidate.append(new_square)
                new_rank, new_file = new_rank + move[0], new_file + move[1]

    return candidate

def generate_rook_moves(bitboards, from_square, color):
    candidate = []
    current_rank, current_file = divmod(from_square, 8)

    # Possible relative moves for a bishop (diagonal)
    rook_moves = [
        (1, 0), (-1, 0),
        (0, 1), (0, -1)
    ]

    for move in rook_moves:
        new_rank, new_file = current_rank + move[0], current_file + move[1]
        while 0 <= new_rank < 8 and 0 <= new_file < 8:
            new_square = 8 * new_rank + new_file
            # Square occupied
            if (bitboards[14] & (1 << new_square)):
                # Occupied by opponent piece
                if (bitboards[12 + (1 - color)] & (1 << new_square)):
                    candidate.append(new_square)
                break
            else:
                candidate.append(new_square)
                new_rank, new_file = new_rank + move[0], new_file + move[1]

    return candidate

def generate_queen_moves(bitboards, from_square, color):
    candidate = []
    current_rank, current_file = divmod(from_square, 8)

    # Possible relative moves for a Queen (diagonal)
    queen_moves = [
        (1, 1), (1, 0), (1, -1),
        (0, 1), (0, -1),
        (-1, 1), (-1, 0), (-1, -1)
    ]

    for move in queen_moves:
        new_rank, new_file = current_rank + move[0], current_file + move[1]
        while 0 <= new_rank < 8 and 0 <= new_file < 8:
            new_square = 8 * new_rank + new_file
            # Square occupied
            if (bitboards[14] & (1 << new_square)):
                # Occupied by opponent piece
                if (bitboards[12 + (1 - color)] & (1 << new_square)):
                    candidate.append(new_square)
                break
            else:
                candidate.append(new_square)
                new_rank, new_file = new_rank + move[0], new_file + move[1]
    return candidate

def generate_king_moves(bitboards, from_square, color, castling_rights: dict = None):
    candidate = []
    current_rank, current_file = divmod(from_square, 8)

    king_moves = [
        (1, 1), (1, 0), (1, -1),
        (0, 1), (0, -1),
        (-1, 1), (-1, 0), (-1, -1)
    ]

    for move in king_moves:
        new_rank, new_file = current_rank + move[0], current_file + move[1]
        new_square = 8 * new_rank + new_file
        if 0 <= new_rank < 8 and 0 <= new_file < 8 and 0 <= new_square < 64:
            if not (bitboards[12 + color] & (1 << new_square)):
                candidate.append(new_square)

    # Castling
    # ! FIX
    if 0:
        if color == 0:
            if castling_rights.get('WK'):
                candidate.append(6)
            if castling_rights.get('WQ'):
                candidate.append(2)
        else:
            if castling_rights.get('BK'):
                candidate.append(62)
            if castling_rights.get('BQ'):
                candidate.append(58)

    return candidate