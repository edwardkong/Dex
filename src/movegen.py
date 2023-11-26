import game, position, tools, makemove

def generate_moves(board, color):
    moves = []
    bitboards = board.bitboards
    # ! HARDCODE - FIX CASTLING RIGHTS - IN BOARD OR GAMESTATE??
    castling_rights = {'WK': 1, 'WQ': 1, 'BK': 1, 'BQ': 1} 

    # Iterate through all pieces of the given color
    for piece_type in range(6):
        pieces = bitboards[piece_type][color]
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


def generate_piece_moves(bitboards, piece_type, from_square, color, castling_rights, last_move = None):
    moves = []

    # Implement move generation logic for each piece type
    # Verify if each move will put the king in check
    if piece_type == 0:  # Pawn
        for candidate in generate_pawn_moves(bitboards, from_square, color, last_move):
            if type(candidate) == str:
                promo_piece = tools.char_to_int_piece(candidate[2])
                move = from_square | (candidate[:2] << 6) | (promo_piece << 12) | (color << 15)
            else:
                move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            if position.is_legal_position(position.update_board(bitboards, move), 1 - color):
                moves.append(move)
    elif piece_type == 1:  # Knight
        for candidate in generate_knight_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            if position.is_legal_position(position.update_board(bitboards, move), 1 - color):
                moves.append(move)
    elif piece_type == 2:  # Bishop
        for candidate in generate_bishop_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            if position.is_legal_position(position.update_board(bitboards, move), 1 - color):
                moves.append(move)
    elif piece_type == 3:  # Rook
        for candidate in generate_rook_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            if position.is_legal_position(position.update_board(bitboards, move), 1 - color):
                moves.append(move)
    elif piece_type == 4:  # Queen
        for candidate in generate_queen_moves(bitboards, from_square, color):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            if position.is_legal_position(position.update_board(bitboards, move), 1 - color):
                moves.append(move)
    elif piece_type == 5: # King
        for candidate in generate_king_moves(bitboards, from_square, color, castling_rights):
            move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
            if position.is_legal_position(position.update_board(bitboards, move), 1 - color):
                moves.append(move)
    
    return moves

def generate_pawn_moves(bitboards, from_square, color, last_move = None):
    candidate = []
    rank, file = divmod(from_square, 8)

    friendly_pieces = tools.combine_bitboard(bitboards, color)
    opp_pieces = tools.combine_bitboard(bitboards, 1 - color)
    all_pieces = tools.combine_bitboard(bitboards)
    
    # Single move forward (no promotion)
    if 1 <= rank < 7:
        to_square = from_square + 8 if color == 0 else from_square - 8
        if position.is_square_occupied(bitboards, to_square) == -1:
            candidate.append(to_square)
    to_square = None

    # Double move forward
    if (color == 0 and rank == 1) or (color == 1 and rank == 6):
        step_square = from_square + 8 if color == 0 else from_square - 8
        to_square = from_square + 16 if color == 0 else from_square - 16
        if position.is_square_occupied(bitboards, step_square) == -1 and position.is_square_occupied(bitboards, to_square) == -1:
            candidate.append(to_square)
    
    # Capture moves
    cand_temp = []
    if color == 0:
        if file == 0:
            to_square = from_square + 9
            if opp_pieces & (1 << to_square):
                cand_temp.append(to_square)
        elif file == 7:
            to_square = from_square + 7
            if opp_pieces & (1 << to_square):
                cand_temp.append(to_square)
        else:
            to_square = (from_square + 7, from_square + 9)
            for i in to_square:
                if opp_pieces & (1 << i):
                    cand_temp.append(i)
    if color == 1:
        if file == 0:
            to_square = from_square - 7
            if opp_pieces & (1 << to_square):
                cand_temp.append(to_square)
        elif file == 7:
            to_square = from_square - 9
            if opp_pieces & (1 << to_square):
                cand_temp.append(to_square)
        else:
            to_square = (from_square - 7, from_square - 9)
            for i in to_square:
                if opp_pieces & (1 << i):
                    cand_temp.append(i)
    for move in cand_temp:
        if move > 55 or move < 8:
            for prom in "nbrq":
                candidate.append(f"{move}{prom}")
        else:
            candidate.append(move)
    cand_temp, to_square = None, None

    # Promotion
    if (color == 0 and rank == 6):
        to_square = from_square + 8
        if position.is_square_occupied(bitboards, to_square) == -1:
            for prom in "nbrq":
                candidate.append(f"{to_square}{prom}")
        to_square = None
    if (color == 1 and rank == 1):
        to_square = from_square - 8
        if position.is_square_occupied(bitboards, to_square) == -1:
            for prom in "nbrq":
                candidate.append(f"{to_square}{prom}")
        to_square = None

    # En Passant
    # ! Implement try catch in case no last_move
    en_passant_legal = False
    try:
        if last_move is not None:
            last_move_from = ord(last_move[0]) - ord('a') + (int(last_move[1]) - 1) * 8
            last_move_to = ord(last_move[2]) - ord('a') + (int(last_move[3]) - 1) * 8
            if from_square in range(24, 40):
                if abs(last_move_from - last_move_to) == 16:            
                    if bitboards[0][1-color] & (1 << last_move_to):
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
        if 0 <= new_rank < 8 and 0 <= new_file < 8:
            if not position.is_square_occupied_friendly(bitboards, new_square, color):
                candidate.append(new_square)
    return candidate

def generate_bishop_moves(bitboards, from_square, color):
    candidate = []
    current_rank, current_file = divmod(from_square, 8)

    friendly_pieces = tools.combine_bitboard(bitboards, color)
    opp_pieces = tools.combine_bitboard(bitboards, 1 - color)
    all_pieces = tools.combine_bitboard(bitboards)

    # Possible relative moves for a bishop (diagonal)
    bishop_moves = [
        (1, 1), (1, -1),
        (-1, 1), (-1, -1)
    ]

    for move in bishop_moves:
        new_rank, new_file = current_rank + move[0], current_file + move[1]
        friendly_collision = False
        opp_collision = False
        while 0 <= new_rank < 8 and 0 <= new_file < 8:
            new_square = 8 * new_rank + new_file
            friendly_collision = friendly_pieces & (1 << new_square)
            opp_collision = opp_pieces & (1 << new_square)
            if friendly_collision:
                break
            elif opp_collision:
                candidate.append(new_square)
                break
            else:
                candidate.append(new_square)
                new_rank, new_file = new_rank + move[0], new_file + move[1]

    return candidate

def generate_rook_moves(bitboards, from_square, color):
    candidate = []
    current_rank, current_file = divmod(from_square, 8)

    friendly_pieces = tools.combine_bitboard(bitboards, color)
    opp_pieces = tools.combine_bitboard(bitboards, 1 - color)
    all_pieces = tools.combine_bitboard(bitboards)

    # Possible relative moves for a bishop (diagonal)
    rook_moves = [
        (1, 0), (-1, 0),
        (0, 1), (0, -1)
    ]

    for move in rook_moves:
        new_rank, new_file = current_rank + move[0], current_file + move[1]
        friendly_collision = False
        opp_collision = False
        while 0 <= new_rank < 8 and 0 <= new_file < 8:
            new_square = 8 * new_rank + new_file
            friendly_collision = friendly_pieces & (1 << new_square)
            opp_collision = opp_pieces & (1 << new_square)
            if friendly_collision:
                break
            elif opp_collision:
                candidate.append(new_square)
                break
            else:
                candidate.append(new_square)
                new_rank, new_file = new_rank + move[0], new_file + move[1]

    return candidate

def generate_queen_moves(bitboards, from_square, color):
    candidate = []
    current_rank, current_file = divmod(from_square, 8)

    friendly_pieces = tools.combine_bitboard(bitboards, color)
    opp_pieces = tools.combine_bitboard(bitboards, 1 - color)
    all_pieces = tools.combine_bitboard(bitboards)

    # Possible relative moves for a Queen (diagonal)
    queen_moves = [
        (1, 1), (1, 0), (1, -1),
        (0, 1), (0, -1),
        (-1, 1), (-1, 0), (-1, -1)
    ]

    for move in queen_moves:
        new_rank, new_file = current_rank + move[0], current_file + move[1]
        friendly_collision = False
        opp_collision = False
        while 0 <= new_rank < 8 and 0 <= new_file < 8:
            new_square = 8 * new_rank + new_file
            friendly_collision = friendly_pieces & (1 << new_square)
            opp_collision = opp_pieces & (1 << new_square)
            if friendly_collision:
                break
            elif opp_collision:
                candidate.append(new_square)
                break
            else:
                candidate.append(new_square)
                new_rank, new_file = new_rank + move[0], new_file + move[1]
    return candidate

def generate_king_moves(bitboards, from_square, color, castling_rights: dict = None):
    candidate = []
    current_rank, current_file = divmod(from_square, 8)

    friendly_pieces = tools.combine_bitboard(bitboards, color)
    opp_pieces = tools.combine_bitboard(bitboards, 1 - color)
    all_pieces = tools.combine_bitboard(bitboards)

    king_moves = [
        (1, 1), (1, 0), (1, -1),
        (0, 1), (0, -1),
        (-1, 1), (-1, 0), (-1, -1)
    ]
    for move in king_moves:
        new_rank, new_file = current_rank + move[0], current_file + move[1]
        new_square = 8 * new_rank + new_file
        if 0 <= new_rank < 8 and 0 <= new_file < 8:
            friendly_collision = friendly_pieces & (1 << new_square)
            if friendly_collision:
                continue
            else:
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