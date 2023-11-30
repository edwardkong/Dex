import game, position, tools, makemove

class MoveGenerator:

    def __init__(self, board, color):
        self.board = board
        self.color = color
        self.ray_mask = 0
        self.pinned_ray_mask = 0
        self.pinned_piece_mask = 0
        self.check_ray_mask = 0
        self.in_check = False
        self.double_check = False
        self.moves = []

    def calculate_attacks_on_king(self, board, color):
        """Search in rays expanding from the king's location to find attackers and pins."""
        bitboards = self.board.bitboards
        occupants = self.board.occupants
        attack_maps = self.attack_maps

        king_square = bitboards[5 + color]
        king_rank = king_square // 8
        king_file = king_square % 8

        # Search for sliding piece attack rays in all directions
        directions = [
            (1, 1), (1, -1), (-1, 1), (-1, -1),
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]
        start = 0 if bitboards[2 + color * 6] or bitboards[4 + color * 6] else 4
        end = 8 if bitboards[3 + color * 6] or bitboards[4 + color * 6] else 4
        
        for d in directions[start:end]:
            diag = d[0] and d[1]
            new_rank, new_file = king_rank + d[0], king_file + d[1]
            friendly_piece_encountered = 0

            while 0 <= new_rank < 8 and 0 <= new_file < 8:
                new_square = 8 * new_rank + new_file
                self.ray_mask |= new_square

                # Friendly piece occupied
                if occupants[color] & (1 << new_square):
                    # Second friendly piece along ray
                    if not friendly_piece_encountered:
                        friendly_piece_encountered = new_square
                    else:
                        break
                # Opponent piece occupied
                elif occupants[1 - color] & (1 << new_square):
                    for piece_type in bitboards[piece_type + (1 - color) * 6]:
                        if bitboards[piece_type + (1 - color) * 6] & (1 << new_square):
                            break
                    # Opponent piece moves along ray
                    if piece_type == 4 or diag & piece_type == 2 or not diag & piece_type == 3:
                        # Piece is pinned
                        if friendly_piece_encountered:
                            self.pinned_ray_mask |= self.ray_mask
                        # No friendly piece on ray, thus is check
                        else:
                            self.check_ray_mask |= self.ray_mask
                            self.double_check = self.in_check
                            self.in_check = True
                    # Opponent piece does not have sight
                    else:
                        break
            # King must move if double checked
            if self.double_check:
                break
        
        # Search for knight attacks
        if attack_maps[1 + color * 6] & (1 << king_square):
            self.double_check = self.in_check
            self.in_check = True

        # Search for pawn attacks
        if attack_maps[color * 6] & (1 << king_square):
            self.double_check = self.in_check
            self.in_check = True



    def generate_king_moves(bitboards, from_square, color):
        """Returns psuedo legal king moves given a board."""
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

        if bitboards[15]:
            kingside, queenside = position.can_castle(bitboards, color)
            if color == 0:
                if kingside:
                    candidate.append(6)
                if queenside:
                    candidate.append(2)
            elif color == 1:
                if kingside:
                    candidate.append(62)
                if queenside:
                    candidate.append(58)

        return candidate
    

        def generate_psuedo_castle(board, from_square):
        """Returns psuedo legal king castles given the castling rights of a board."""
        candidate = []
        if from_square == 5:
            if board.castling_rights & (1 << 3):
                candidate.append(6)
            if board.castling_rights & (1 << 2):
                candidate.append(2)
        elif from_square == 60:
            if board.castling_rights & (1 << 1):
                candidate.append(62)
            if board.castling_rights & (1 << 0):
                candidate.append(58)
        return candidate            

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

    def is_move_legal(board, from_square, to_square, piece_type, color):
        # Check if the king moves to an attacked square
        # Check if the king is in scope (in check)
        # Check if the king is in double check (king must move)
        # # Check if the move blocks the scope
        # # Check if the moving piece is pinned & if the move is along the pin

        # King moves to attacked square
        if piece_type == 5 and to_square & board.attack_maps[13 - color]:
            return False



            
        


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



    def generate_piece_moves(bitboards, piece_type, from_square, color, last_move = None):
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
            for candidate in generate_king_moves(bitboards, from_square, color):
                move = from_square | (candidate << 6) | (piece_type << 12) | (color << 15)
                if position.is_legal_position(position.simulate_move(bitboards, move), 1 - color):
                    moves.append(move)
        return moves

    def generate_pawn_push(board, from_square, color):
        """Returns psuedo legal pawn pushes and push promotions."""
        candidate = []
        rank, file = divmod(from_square, 8)
        
        # Single step forward
        single_square = from_square + 8 if color == 0 else from_square - 8
        if 1 <= rank < 7 and not (board.occupants[2] & (1 << single_square)):
            # Single step promotion
            if (color == 0 and rank == 6) or (color == 1 and rank == 1):
                candidate.extend([f"{single_square}{promo}" for promo in "nbrq"])
            else:
                candidate.append(single_square)
            # Double step forward
            if (color == 0 and rank == 1) or (color == 1 and rank == 6):
                double_square = from_square + 16 if color == 0 else from_square - 16
                if not (board.occupants[2] & (1 << double_square)):
                    candidate.append(double_square)
        
        return candidate

    def generate_pawn_captures(board, from_square, color):
        """Returns psuedo legal pawn captures and capture promotions."""
        candidate = []
        opponent_color = 1 - color
        rank = from_square // 8

        # Get the squares that the pawn can potentially capture to
        scope = generate_pawn_scope(from_square, color)

        # Check each square to see if it contains an opponent's piece
        for square in scope:
            if board.occupants[opponent_color] & (1 << square):
                # If a capture will lead to a promotion, add the promotion moves
                if (color == 0 and rank == 6) or (color == 1 and rank == 1):
                    candidate.extend([f"{square}{promo}" for promo in "nbrq"])
                else:
                    candidate.append(square)

        return candidate

    def generate_pawn_ep(board, from_square, color):
        """
        Returns psuedo legal pawn en passant
        ! Not yet implemented !
        """
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

    def generate_knight_moves(board, from_square, color):
        """Returns psuedo legal knight moves."""
        candidate = []

        # Get the squares that the knight can potentially move to
        scope = generate_knight_scope(from_square)

        # Check each square to see if it is occupied by an opponent's piece or is empty
        for square in scope:
            if not board.occupants[color] & (1 << square):
                candidate.append(square)

        return candidate

    def generate_sliding_moves(occupants, from_square, color, piece_type):
        """
        Takes a board's occupants.
        Returns psuedo legal moves for sliding pieces, including captures. piece_type -> {2: Bishop, 3: Rook, 4: Queen}
        """
        ccandidate = []
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
                if not (occupants[color] & (1 << new_square)):
                    candidate.append(new_square)
                else:
                    break
                rank, file = new_rank + move[0], new_file + move[1]

        return candidate



