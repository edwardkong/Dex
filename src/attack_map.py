
    def initialize_attack_map(self):
        """Initializes attack maps."""
        self.attack_map = [0] * 14

    def generate_attack_map(self):
        """
        Returns bitboards representing squares attacked by each piece and color complex.
        0 - 5: White pawn, knight, bishop, rook, queen, king
        6 - 11: Black pawn, knight, bishop, rook, queen, king
        12: White combined
        13: Black combined
        """
        for piece in range(12):
            piece_type = piece % 6
            color = piece // 6
            pieces = self.bitboards[piece_type + color * 6]
            self.attack_map[piece] = self.get_attack_map_for_piece_type(piece_type, color, pieces, self)

        self.attack_map[12] = self.attack_map[0] | self.attack_map[1] | self.attack_map[2] | self.attack_map[3] | self.attack_map[4] | self.attack_map[5]
        self.attack_map[13] = self.attack_map[6] | self.attack_map[7] | self.attack_map[8] | self.attack_map[9] | self.attack_map[10] | self.attack_map[11]

    def get_attack_map_for_pieces(self, piece_type, color, pieces, board=None):
        attack_map = 0
        while pieces:
                square = pieces & -pieces
                for move in scope.get_scope_from_square(self, square, color, piece_type):
                    attack_map |= move
                pieces &= pieces - 1
        return attack_map

    def get_attack_map_for_sliding_pieces(self, piece_type, color, pieces, occupants=None):
        """Recalculates sliding pieces' attack maps after a move, thus accepting a copy of occupants after the move is made as opposed to applying the move to the board."""
        if occupants == None:
            occupants = self.occupants
        attack_map = 0
        while pieces:
                square = pieces & -pieces
                for move in scope.generate_sliding_scope(occupants, square, color, piece_type):
                    attack_map |= move
                pieces &= pieces - 1
        return attack_map

    def update_attack_map(self, move, board=None):
        """Updates the attack maps given a move. Currently works on unupdated board"""
        if board is None:
            board = self

        attack_map = board.attack_map.copy()

        # Extract information from the move
        from_square = move & 0x3F  # Source square
        to_square = (move >> 6) & 0x3F  # Destination square
        piece_type = (move >> 12) & 0x7  # Piece type (0-5)
        color = (move >> 15) & 0x1  # Color (0 for white, 1 for black)

        from_rank = from_square // 8
        from_file = from_square % 8

        # Needed for sliding piece calculations
        occupants_after_move = board.occupants.copy()
        occupants_after_move[color] = occupants_after_move[color] & ~(1 << from_square) | (1 << to_square)
        occupants_after_move[2] = occupants_after_move[2] & ~(1 << from_square) | (1 << to_square)
        
        # Castles
        is_castle = (abs(from_square - to_square) == 2 and piece_type == 5)

        if is_castle:
            king = board.bitboards[5 + color * 6]
            attack_map[5 + color * 6] = get_attack_map_for_pieces(5 + color * 6, color, king, board)
            rooks = board.bitboards[3 + color * 6]
            attack_map[3 + color * 6] = get_attack_map_for_pieces(3 + color * 6, color, rooks, board)
            return attack_map

        # Promotion
        is_promotion = ((from_rank == 1 and color == 1 and (board.bitboard[0] & (1 << from_square))) or (from_rank == 6 and color == 0 and (board.bitboard[6] & (1 << from_square))))
        
        if is_promotion:
            pawns_after_move = board.bitboards[color * 6] & ~(1 << from_square) | (1 << to_square)
            attack_map[color * 6] = board.get_attack_map_for_pieces(color * 6, color, pawns_after_move)
            
            promoted_pieces = board.bitboards[piece_type + color * 6] & (1 << to_square)
            if piece_type == 1:
                attack_map[piece_type + color * 6] = board.get_attack_map_for_pieces(piece_type, color, promoted_pieces)
            else:
                attack_map[piece_type + color * 6] = board.get_attack_map_for_sliding_pieces(piece_type, color, promoted_pieces, occupants_after_move)

        # Capture
        is_capture = board.occupants[1 - color] & (1 << to_square)

        # Remove captured piece's scope from attack map
        # Sliding piece scope need not be recalculated, as the capturing piece replaces the captured piece. Unless en passant.
        if is_capture:
            for piece in range(6):
                if board.bitboards[piece + (1 - color) * 6] & (1 << to_square):
                    pieces_after_capture = board.bitboards[piece + (1 - color) * 6] & ~(1 << to_square)
                    attack_map[piece + (1 - color) * 6] = board.get_attack_map_for_pieces(piece, 1 - color, pieces_after_capture)
                    break
            
        # Update moved piece's attack map
        pieces_after_move = board.bitboards[piece_type] & ~(1 << from_square) | (1 << to_square)
        attack_map[piece_type + color * 6] = board.get_attack_map_for_pieces(piece_type, color, pieces_after_move)

        # Sliding pieces
        # For each sliding piece type, if the move moves a piece into or out of its scope, recalculate the scope to the new move.
        for piece in (2, 3, 4, 8, 9, 10):
            for square in [from_square, to_square]:
                if board.attack_map[piece] & (1 << square):
                    pieces = board.bitboards[piece]
                    attack_map[piece] = board.get_attack_map_for_sliding_pieces(piece % 6, 1 - color, pieces, occupants_after_move)
                    break

        return attack_map
        
    def update_consolidated_attack_maps(self, board=None):
        """Updates instance attack maps for white & black."""
        if board is None:
            board = self

        board.attack_map[12] = board.attack_map[0] | board.attack_map[1] | board.attack_map[2] | board.attack_map[3] | board.attack_map[4] | board.attack_map[5]
        board.attack_map[13] = board.attack_map[6] | board.attack_map[7] | board.attack_map[8] | board.attack_map[9] | board.attack_map[10] | board.attack_map[11]
        
        return board.attack_map
            