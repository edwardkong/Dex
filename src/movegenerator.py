import game, board, tools

DIRECTIONS = [
        (1, 1), (1, -1), (-1, 1), (-1, -1),
        (1, 0), (-1, 0), (0, 1), (0, -1)
]

class MoveGenerator:

    def __init__(self, board, color):
        self.board = board
        self.color = color
        self.pinned_ray_mask = 0
        self.check_ray_mask = 0
        self.in_check = False
        self.double_check = False
        self.king_square = self.board.bitboards[5 + self.color * 6]
        self.moves = []

        self.calculate_attacks_on_king(self.board)

    def generate_moves(self):
        """Returns all moves for all pieces in position for a color."""
        self.moves.extend(generate_king_moves(self.king_square))
    
        # Only the king can move in double check
        if double_check:
            return self.moves
        else:
            # Iterate through all pieces of the given color
            for piece_type in range(5):
                pieces = self.board.bitboards[piece_type + self.color * 6]
                while pieces:
                    # Find the index of the least significant set bit (LSB)
                    from_square = tools.bitscan_lsb(pieces)
                    
                    # Generate moves for the current piece
                    self.moves.extend(self.generate_piece_moves(piece_type, from_square))

                    # Clear the LSB to move to the next piece
                    pieces &= pieces - 1
        
            return self.moves

        return self.moves

    def generate_king_moves(self):
        """Returns list of legal king moves."""
        candidate = []
        from_square = self.king_square
        color = self.color
        rank = from_square // 8
        file = from_square % 8

        for d in DIRECTIONS:
            new_rank, new_file = rank + d[0], file + d[1]
            new_square = 8 * new_rank + new_file
            if 0 <= new_rank < 8 and 0 <= new_file < 8:
                if not self.board.occupants[color] & (1 << new_square) and not self.board.is_square_attacked(new_square):
                    candidate.append(from_square | (new_square << 6) | (5 << 12) | (color << 15))
        # Castle
        if not self.in_check:
            # White Kingside
            if (from_square == 4) & (self.board.castling_rights & (1 << 3)):
                if not self.board.is_square_occupied(5) and not self.board.is_square_occupied(6) and not self.board.is_square_attacked(5, color) and not self.board.is_square_attacked(6, color):
                        candidate.append(4 | (6 << 6) | (5 << 12) | (color << 15))
            # White Queenside
            if (from_square == 4) & (self.board.castling_rights & (1 << 2)):
                if not self.board.is_square_occupied(3) and not self.board.is_square_occupied(2) and not self.board.is_square_attacked(3, color) and not self.board.is_square_attacked(2, color):
                        candidate.append(4 | (2 << 6) | (5 << 12) | (color << 15))
            # Black Kingside
            if (from_square == 60) & (self.board.castling_rights & (1 << 1)):
                if not self.board.is_square_occupied(61) and not self.board.is_square_occupied(62) and not self.board.is_square_attacked(61, color) and not self.board.is_square_attacked(62, color):
                        candidate.append(60 | (62 << 6) | (5 << 12) | (color << 15))
            # Black Queenside
            if (from_square == 60) & (self.board.castling_rights & (1 << 0)):
                if not self.board.is_square_occupied(59) and not self.board.is_square_occupied(58) and not self.board.is_square_attacked(59, color) and not self.board.is_square_attacked(58, color):
                        candidate.append(60 | (58 << 6) | (5 << 12) | (color << 15))        
        
        return candidate      
    
    def generate_piece_moves(self, piece_type, from_square):
        """Returns legal moves for each non-king piece."""
        piece_pseudo_functions = {
            0: (self.generate_pawn_push, self.generate_pawn_captures),
            1: (self.generate_knight_moves,),
            2: (self.generate_sliding_moves,),
            3: (self.generate_sliding_moves,),
            4: (self.generate_sliding_moves,)
        }
        
        candidate = []
        legal_moves = []
        color = self.color       
        
        for func in piece_pseudo_functions[piece_type]:
            candidate.extend(func(from_square))
        
        for to_square in candidate:
            # Piece is pinned and destination is outside of the pin
            if (self.pinned_ray_mask & (1 << from_square) and not self.pinned_ray_mask & (1 << to_square)) or
                # King is in check and piece destination is not in check_ray (blocking)
                (if self.in_check and not self.check_ray_mask & (1 << to_square)):
                    continue
            move = from_square | (new_square << 6) | (piece_type << 12) | (color << 15)
            legal_moves.append(move)
        
        return legal_moves

    def calculate_attacks_on_king(self, board, color):
        """Search in rays expanding from the king's location to find attackers and pins."""
        bitboards = self.board.bitboards
        occupants = self.board.occupants
        attack_map = self.board.attack_map
        color = self.color

        king_rank = self.king_square // 8
        king_file = self.king_square % 8

        ray_mask = 0

        # Search for sliding piece attack rays in all directions
        
        start = 0 if bitboards[2 + color * 6] or bitboards[4 + color * 6] else 4
        end = 8 if bitboards[3 + color * 6] or bitboards[4 + color * 6] else 4
        
        for d in DIRECTIONS[start:end]:
            diag = d[0] and d[1]
            new_rank, new_file = king_rank + d[0], king_file + d[1]
            friendly_piece_encountered = 0

            while 0 <= new_rank < 8 and 0 <= new_file < 8:
                new_square = 8 * new_rank + new_file
                ray_mask |= new_square

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
                            self.pinned_ray_mask |= ray_mask
                        # No friendly piece on ray, thus is check
                        else:
                            self.check_ray_mask |= ray_mask
                            self.double_check = self.in_check
                            self.in_check = True
                    # Opponent piece does not have sight
                    else:
                        break
            # King must move if double checked
            if self.double_check:
                break
        
        # Search for knight attacks
        if attack_map[1 + color * 6] & (1 << self.king_square):
            self.double_check = self.in_check
            self.in_check = True

        # Search for pawn attacks
        if attack_map[color * 6] & (1 << self.king_square):
            self.double_check = self.in_check
            self.in_check = True

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

    def generate_pawn_push(self, from_square, color):
        """Returns psuedo legal pawn pushes and push promotions."""
        candidate = []
        rank, file = divmod(from_square, 8)
        
        # Single step forward
        single_square = from_square + 8 if color == 0 else from_square - 8
        if 1 <= rank < 7 and not (self.board.occupants[2] & (1 << single_square)):
            # Single step promotion
            if (color == 0 and rank == 6) or (color == 1 and rank == 1):
                candidate.extend([f"{single_square}{promo}" for promo in "nbrq"])
            else:
                candidate.append(single_square)
            # Double step forward
            if (color == 0 and rank == 1) or (color == 1 and rank == 6):
                double_square = from_square + 16 if color == 0 else from_square - 16
                if not (self.board.occupants[2] & (1 << double_square)):
                    candidate.append(double_square)
        
        return candidate

    def generate_pawn_captures(self, from_square):
        """Returns psuedo legal pawn captures and capture promotions."""
        candidate = []
        rank = from_square // 8

        # Get the squares that the pawn can potentially capture to
        scope = scope.generate_pawn_scope(from_square, self.color)

        # Check each square to see if it contains an opponent's piece
        for square in scope:
            if self.board.occupants[1 - self.color] & (1 << square):
                # If a capture will lead to a promotion, add the promotion moves
                if (self.color == 0 and rank == 6) or (self.color == 1 and rank == 1):
                    candidate.extend([f"{square}{promo}" for promo in "nbrq"])
                else:
                    candidate.append(square)

        return candidate

    def generate_pawn_ep(self, from_square, color):
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

    def generate_knight_moves(self, from_square):
        """Returns psuedo legal knight moves."""
        candidate = []

        # Get the squares that the knight can potentially move to
        scope = scope.generate_knight_scope(from_square)

        # Check each square to see if it is occupied by an opponent's piece or is empty
        for square in scope:
            if not self.board.occupants[self.color] & (1 << square):
                candidate.append(square)

        return candidate

    def generate_sliding_moves(self, from_square, piece_type):
        """Returns psuedo legal moves for sliding pieces, including captures. piece_type -> {2: Bishop, 3: Rook, 4: Queen}"""
        candidate = []
        rank, file = divmod(from_square, 8)

        start = 0 if (piece_type == 2) or (piece_type == 4) else 4
        end = 8 if (piece_type == 3) or (piece_type == 4) else 4
        
        for d in DIRECTIONS[start:end]:
            new_rank, new_file = rank + d[0], file + d[1]
            while 0 <= new_rank < 8 and 0 <= new_file < 8:
                new_square = 8 * new_rank + new_file
                # Square occupied
                if not (self.occupants[self.color] & (1 << new_square)):
                    candidate.append(new_square)
                else:
                    break
                rank, file = new_rank + d[0], new_file + d[1]

        return candidate