import board, tools, scope

DIRECTIONS = [
        (1, 1), (1, -1), (-1, 1), (-1, -1),
        (1, 0), (-1, 0), (0, 1), (0, -1)
        ]

class MoveGenerator:

    def __init__(self, board, color):
        self.board = board
        self.color = color
        self.pinned_ray_mask = 0
        self.attacked_jump_mask = 0
        self.check_ray_mask = 0
        self.in_check = False
        self.double_check = False
        self.king_square = tools.bitscan_lsb(self.board.bitboards[5 + self.color * 6])
        self.moves = []
        self.attacked_ray_mask = 0

        self.generate_attacked_ray_mask()
        self.calculate_attacks_on_king()

    def generate_moves(self):
        """Returns all moves for all pieces in position for a color."""
        self.moves.extend(self.generate_king_moves())
        # Only the king can move in double check
        if self.double_check:
            return self.moves
        else:
            # Iterate through all pieces of the given color
            for piece_type in range(5):
                pieces = self.board.bitboards[piece_type + self.color * 6]
                while pieces:
                    # Find the index of the least significant set bit (LSB)
                    from_square = tools.bitscan_lsb(pieces)
                    

                    #test = self.generate_piece_moves(piece_type, from_square)
                    #print(from_square)
                    #print(piece_type)
                    #print(test)
                    
                    #self.moves.extend(test)

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
                if not (self.board.occupants[color] & (1 << new_square)): 
                    if (not (self.attacked_jump_mask & (1 << new_square))):
                        if (not (self.attacked_ray_mask & (1 << new_square))):
                            candidate.append(from_square | (new_square << 6) | (5 << 12) | (color << 15))
        # Castle
        if not self.in_check:
            kingside, queenside = scope.can_castle(self.board, self.color)
            if color:
                if kingside:
                    candidate.append(60 | (62 << 6) | (5 << 12) | (color << 15))
                if queenside:
                    candidate.append(60 | (58 << 6) | (5 << 12) | (color << 15))
            else:
                if kingside:
                    candidate.append(4 | (6 << 6) | (5 << 12) | (color << 15))
                if queenside:
                    candidate.append(4 | (2 << 6) | (5 << 12) | (color << 15))
        return candidate      
    
    def generate_piece_moves(self, piece_type, from_square):
        """Returns legal moves for each non-king piece."""        
        candidate = []
        legal_moves = []
        color = self.color
        #print(f"piece_type: {piece_type}")
        #print(f"from_square: {from_square}")

        if piece_type == 0:
            candidate.extend(self.generate_pawn_push(from_square))
            candidate.extend(self.generate_pawn_captures(from_square))
            candidate.extend(self.generate_pawn_ep(from_square))
        elif piece_type == 1:
            candidate.extend(self.generate_knight_moves(from_square))
        elif piece_type in (2, 3, 4):
            candidate.extend(self.generate_sliding_moves(from_square, piece_type))
        #print(f"candidate: {candidate}")
        for to_square in candidate:
            if type(to_square) == str:
                piece_type = tools.char_to_int_piece(to_square[-1])
                to_square = int(to_square[:-1])
            #print(to_square)
            # Piece is pinned and destination is outside of the pin or
            # King is in check and piece destination is not in check_ray (blocking)
            if (self.pinned_ray_mask & (1 << from_square) and not self.is_moving_along_pin(from_square, to_square)) or \
                (self.in_check and not self.check_ray_mask & (1 << to_square)):
                    continue
            
            move = from_square | (to_square << 6) | (piece_type << 12) | (color << 15)
            legal_moves.append(move)
        
        return legal_moves

    def calculate_attacks_on_king(self):
        """Search in rays expanding from the king's location to find attackers and pins."""
        bitboards = self.board.bitboards
        occupants = self.board.occupants
        color = self.color
        king_square = self.king_square

        king_rank = king_square // 8
        king_file = king_square % 8

        # Search for sliding piece attack rays in all directions
        
        start = 0 if bitboards[2 + (1 - color) * 6] or bitboards[4 + (1 - color) * 6] else 4
        end = 8 if bitboards[3 + (1 - color) * 6] or bitboards[4 + (1 - color) * 6] else 4

        for d in DIRECTIONS[start:end]:
            ray_mask = (1 << king_square)
            diag = abs(d[0]) == abs(d[1])
            new_rank, new_file = king_rank + d[0], king_file + d[1]
            friendly_piece_encountered = 0

            while 0 <= new_rank < 8 and 0 <= new_file < 8:
                new_square = 8 * new_rank + new_file
                ray_mask |= (1 << new_square)

                # Friendly piece occupied
                if occupants[color] & (1 << new_square):
                    if not friendly_piece_encountered:
                        friendly_piece_encountered = new_square
                    # Second friendly piece along ray
                    else:
                        break
                # Opponent piece occupied
                elif occupants[1 - color] & (1 << new_square):
                    for piece_type in range(6):
                        if bitboards[piece_type + (1 - color) * 6] & (1 << new_square):
                            break
                    # Opponent piece moves along ray
                    if (piece_type == 4) or (diag and piece_type == 2) or ((not diag) and (piece_type == 3)):
                        # Piece is pinned
                        if friendly_piece_encountered:
                            self.pinned_ray_mask |= ray_mask
                        # No friendly piece on ray, thus is check
                        else:
                            self.check_ray_mask |= ray_mask
                            self.double_check = self.in_check
                            self.in_check = True
                            xray_rank = king_rank - d[0]
                            xray_file = king_file - d[1]
                            xray_square = 8 * xray_rank + xray_file
                            if 0 <= xray_rank < 8 and 0 <= xray_file < 8:
                                if not self.board.occupants[color] & (1 << xray_square):
                                    self.attacked_ray_mask |= (1 << xray_square)
                    # Opponent piece does not have sight
                    else:
                        break
                new_rank += d[0]
                new_file += d[1]
            # King must move if double checked
            if self.double_check:
                break

        # Search for knight attacks
        knights = bitboards[1 + (1 - color) * 6]
        while knights:
            knight_square = tools.bitscan_lsb(knights)
            for move in scope.generate_knight_scope(knight_square):
                self.attacked_jump_mask |= (1 << move)
                if king_square  == move:
                    self.double_check = self.in_check
                    self.in_check = True
                    self.check_ray_mask |= (1 << knight_square)
            knights &= knights - 1

        # Search for pawn attacks
        pawns = bitboards[(1 - color) * 6]
        while pawns:
            pawn_square = tools.bitscan_lsb(pawns)
            r_diff = abs((pawn_square // 8) - (king_square // 8))
            f_diff = abs((pawn_square % 8) - (king_square % 8))
            if r_diff > 2 or f_diff > 2:
                pawns &= pawns - 1
                continue
            for move in scope.generate_pawn_scope(pawn_square, (1 - color)):
                self.attacked_jump_mask |= (1 << move)
                if king_square == move:
                    self.double_check = self.in_check
                    self.in_check = True
                    self.check_ray_mask |= (1 << pawn_square)
            pawns &= pawns -1

        # Search for opponent king scope
        opp_king = bitboards[5 + (1 - color) * 6]
        opp_king_square = tools.bitscan_lsb(opp_king)
        for move in scope.generate_king_scope(opp_king_square):
            self.attacked_jump_mask |= (1 << move)

    def generate_pawn_push(self, from_square):
        """Returns psuedo legal pawn pushes and push promotions."""
        candidate = []
        rank, file = divmod(from_square, 8)
        color = self.color
        
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
        pawn_scope = scope.generate_pawn_scope(from_square, self.color)

        # Check each square to see if it contains an opponent's piece
        for square in pawn_scope:
            if self.board.occupants[1 - self.color] & (1 << square):
                # If a capture will lead to a promotion, add the promotion moves
                if (self.color == 0 and rank == 6) or (self.color == 1 and rank == 1):
                    candidate.extend([f"{square}{promo}" for promo in "nbrq"])
                else:
                    candidate.append(square)

        return candidate

    def generate_pawn_ep(self, from_square):
        """
        Returns psuedo legal pawn en passant captures. Double pinned pawns in EP are checked.
        """
        candidate = []
        color = self.color
        board = self.board
        if board.en_passant_flag == -1:
            return candidate
        else:
            ep_file = board.en_passant_flag

        rank = from_square // 8
        file = from_square % 8

        if color == 0 and rank == 4 and abs(file - ep_file) == 1:
            to_square = from_square + ep_file - file + 8
        elif color == 1 and rank == 3 and abs(file - ep_file) == 1:
            to_square = from_square + ep_file - file - 8
        else:
            return candidate
        # Normal pins/blocks checked in piece gen. EP has special condition need to be checked, if both the capturing pawn and the captured pawn are in the pin ray.
        king_square = self.king_square
        king_rank = king_square // 8
        king_file = king_square % 8
        direction = 1 if file > king_file else -1

        # If king is horizontally aligned with the en passant pawns, check past the pawns to see if there are any rooks/queens on the rank, xraying the king.
        if king_rank == rank:
            pieces_encountered = 0
            square_on_rank = file + rank * 8

            while 0 <= file < 8:
                square_on_rank = file + rank * 8 + direction
                # Rook or Queen seen, not enough pieces blocking EP.
                if ((board.bitboards[3 + (1 - color) * 6] | board.bitboards[4 + (1 - color) * 6]) & (1 << square_on_rank)) and pieces_encountered < 3:
                    return candidate
                elif board.occupants[2] & (1 << square_on_rank):
                    pieces_encountered += 1
                file += direction
        candidate.append(to_square)
        return candidate

    def generate_knight_moves(self, from_square):
        """Returns psuedo legal knight moves."""
        candidate = []

        # Get the squares that the knight can potentially move to
        knight_scope = scope.generate_knight_scope(from_square)

        # Check each square to see if it is occupied by an opponent's piece or is empty
        for square in knight_scope:
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
                if self.board.occupants[self.color] & (1 << new_square):
                    break
                candidate.append(new_square)
                if self.board.occupants[1 - self.color] & (1 << new_square):
                    break
                new_rank += d[0] 
                new_file += d[1]

        return candidate
    
    def generate_sliding_scope(self, from_square, color, piece_type):
        """
        Takes a board's occupants.
        Returns sliding piece's scope given a square. piece_type -> {2: Bishop, 3: Rook, 4: Queen}
        """
        candidate = []
        rank, file = divmod(from_square, 8)

        # Possible relative moves for a sliding piece
        start = 0 if (piece_type == 2) or (piece_type == 4) else 4
        end = 8 if (piece_type == 3) or (piece_type == 4) else 4
        
        for d in DIRECTIONS[start:end]:
            new_rank, new_file = rank + d[0], file + d[1]
            while 0 <= new_rank < 8 and 0 <= new_file < 8:
                new_square = 8 * new_rank + new_file
                # Square occupied
                if (self.board.occupants[2] & (1 << new_square)):
                    candidate.append(new_square)
                    break
                else:
                    candidate.append(new_square)
                new_rank, new_file = new_rank + d[0], new_file + d[1]
        return candidate
    
    def generate_attacked_ray_mask(self):
        """Returns a mask of all squares that attacked by sliding pieces."""
        color = self.color
        
        for piece_type in (2, 3, 4):
            pieces = self.board.bitboards[piece_type + (1 - color) * 6]
            while pieces:
                    # Find the index of the least significant set bit (LSB)
                    from_square = tools.bitscan_lsb(pieces)
                    
                    for attacked_square in self.generate_sliding_scope(from_square, 1 - color, piece_type):
                        self.attacked_ray_mask |= (1 << attacked_square)

                    # Clear the LSB to move to the next piece
                    pieces &= pieces - 1
    
    def is_moving_along_pin(self, from_square, to_square):
        """
        If a piece is pinned, determines what direction the pin is and if the candidate move is along that pin. 
        Useful when there are multiple pins in position.
        Assumes the piece moving is pinned.
        """
        king_square = self.king_square

        # Convert squares to coordinates
        from_file, from_rank = from_square % 8, from_square // 8
        to_file, to_rank = to_square % 8, to_square // 8
        king_file, king_rank = king_square % 8, king_square // 8

        # Calculate magnitude
        mag_pin_file = from_file - king_file
        mag_pin_rank =  from_rank - king_rank

        # Calculate normalized directions
        dir_pin_file = (mag_pin_file // abs(mag_pin_file)) if mag_pin_file != 0 else 0
        dir_pin_rank = (mag_pin_rank // abs(mag_pin_rank)) if mag_pin_rank != 0 else 0

        
        new_file = king_file + dir_pin_file
        new_rank = king_rank + dir_pin_rank

        while 0 <= new_file < 8 and 0 <= new_rank < 8:
            if new_file == to_file and new_rank == to_rank:
                return True
            new_file += dir_pin_file
            new_rank += dir_pin_rank
        
        return False