import scope, 

class Board:
    # Board representing position of pieces
    def __init__(self, bitboard=None):
        if bitboard:
            self.newBoard(bitboard)
        else:
            self.newBoard()

    def initialize_bitboard(self):
        self.bitboards = [0] * 12

        self.bitboards = [
            0xFF00,  # WP 0
            0x42,  # WN 1
            0x24,  # WB 2
            0x81,  # WR 3
            0x8,  # WQ 4
            0x10,  # WK 5
            0xFF000000000000,  # BP 6
            0x4200000000000000,  # BN 7
            0x2400000000000000,  # BB 8
            0x8100000000000000,  # BR 9
            0x800000000000000,  # BQ 10
            0x1000000000000000,  # BK 11
        ]

    def initialize_occupants(self):
        self.occupants = [0] * 3

        self.occupants[0] = tools.combine_bitboard(self.bitboards, 0)
        self.occupants[1] = tools.combine_bitboard(self.bitboards, 1)
        self.occupants[2] = tools.combine_bitboard(self.bitboards)

    def initialize_castling(self):
        self.castling_rights = 0b1111

    def newBoard(self) -> None:
        self.initialize_bitboard()
        self.initialize_occupants()
        self.initialize_castling()

    def updateBoard(self, move, board=None):
        if board is None:
            board = self

        bitboards = board.bitboards
        castling_rights = board.castling_rights

        # Extract information from the move
        from_square = move & 0x3F  # Source square
        to_square = (move >> 6) & 0x3F  # Destination square
        piece_type = (move >> 12) & 0x7  # Piece type (0-5)
        color = (move >> 15) & 0x1  # Color (0 for white, 1 for black)

        # Check if it's a pawn and moving to last rank
        is_promotion = (bitboards[0 + color * 6] & (1 << from_square)) and (
            to_square // 8 == 0 or to_square // 8 == 7
        )

        # Capture promotion
        if is_promotion:
            if abs(from_square - to_square) in (7, 9):
                for captured_piece in range(6):
                    if bitboards[captured_piece + (1 - color) * 6] & (1 << to_square):
                        bitboards[captured_piece + (1 - color) * 6] &= ~(
                            1 << to_square
                        )  # Clear captured piece on promotion square
                        break
            bitboards[0 + color * 6] &= ~(
                1 << from_square
            )  # Clear pawn from source square
            bitboards[piece_type + color * 6] |= (
                1 << to_square
            )  # Add promoted piece to destination square
            return bitboards

        # Pawn moves, non-promotion
        elif piece_type == 0:
            # Infer if it's a capture based on the destination square
            if abs(from_square - to_square) in (7, 9):
                # Determine if capture is en passant
                en_passant = True
                # If diagonal pawn move, but no piece on the destination square, it is en passant
                for captured_piece in range(6):
                    if bitboards[captured_piece + (1 - color) * 6] & (1 << to_square):
                        en_passant = False
                        break
                if en_passant:
                    en_passant_square = (
                        to_square + 8 if from_square > to_square else to_square - 8
                    )
                    bitboards[0 + (1 - color) * 6] &= ~(
                        1 << en_passant_square
                    )  # Clear pawn captured by en passant
                    bitboards[0 + color * 6] &= ~(
                        1 << from_square
                    )  # Clear capturing piece from source square
                else:
                    bitboards[0 + color * 6] &= ~(1 << from_square)
                    bitboards[captured_piece + (1 - color) * 6] &= ~(
                        1 << to_square
                    )  # Clear destination square (piece captured)

            # Normal move
            else:
                bitboards[0 + color * 6] &= ~(
                    1 << from_square
                )  # Clear pawn from source square

            # Set the destination square in the bitboard
            bitboards[piece_type + color * 6] |= 1 << to_square
            return bitboards

        # Castling
        elif piece_type == 5:  # King
            # Check for castling
            if color == 0:
                castling_rights &= 0b1100
            else:
                castling_rights &= 0b11

            if abs(from_square - to_square) == 2:
                if color == 0:  # White
                    if to_square == 6:
                        # White king-side castling
                        rook_from_square = 7
                        rook_to_square = 5
                        bitboards[3 + color * 6] &= ~(
                            1 << rook_from_square
                        )  # Clear the rook from the source square
                        bitboards[3 + color * 6] |= (
                            1 << rook_to_square
                        )  # Set the rook on the destination square
                    elif to_square == 2:
                        # White queen-side castling
                        rook_from_square = 0
                        rook_to_square = 3
                        bitboards[3 + color * 6] &= ~(
                            1 << rook_from_square
                        )  # Clear the rook from the source square
                        bitboards[3 + color * 6] |= (
                            1 << rook_to_square
                        )  # Set the rook on the destination square
                    castling_rights &= 0b11
                else:  # Black
                    if to_square == 58:
                        # Black queen-side castling
                        rook_from_square = 56
                        rook_to_square = 59
                        bitboards[3 + color * 6] &= ~(
                            1 << rook_from_square
                        )  # Clear the rook from the source square
                        bitboards[3 + color * 6] |= (
                            1 << rook_to_square
                        )  # Set the rook on the destination square
                    elif to_square == 62:
                        # Black king-side castling
                        rook_from_square = 63
                        rook_to_square = 61
                        bitboards[3 + color * 6] &= ~(
                            1 << rook_from_square
                        )  # Clear the rook from the source square
                        bitboards[3 + color * 6] |= (
                            1 << rook_to_square
                        )  # Set the rook on the destination square
                    castling_rights &= 0b1100

                bitboards[piece_type + color * 6] &= ~(
                    1 << from_square
                )  # Clear piece from source square
                # Set the destination square in the bitboard
                bitboards[piece_type + color * 6] |= 1 << to_square

                return bitboards

        # Has rook moved?
        elif piece_type == 4:
            if from_square == 7:
                castling_rights &= ~(1 << 3)
            elif from_square == 0:
                castling_rights &= ~(1 << 2)
            elif from_square == 63:
                castling_rights &= ~(1 << 1)
            elif from_square == 56:
                castling_rights &= ~(1)

        # Has rook been captured?
        if castling_rights & (1 << 3):
            if not bitboards[3] & (1 << 7):
                castling_rights &= ~(1 << 3)
        if castling_rights & (1 << 2):
            if not bitboards[3] & (1 << 0):
                castling_rights &= ~(1 << 2)
        if castling_rights & (1 << 1):
            if not bitboards[9] & (1 << 63):
                castling_rights &= ~(1 << 1)
        if castling_rights & (1):
            if not bitboards[9] & (1 << 56):
                castling_rights &= ~(1)

        # Check if it's a capture
        if piece_type in (1, 2, 3, 4, 5):
            if occupancy_bitboards[1 - color] & (1 << to_square):
                for captured_piece in range(6):
                    if bitboards[captured_piece + (1 - color) * 6] & (1 << to_square):
                        bitboards[captured_piece + (1 - color) * 6] &= ~(
                            1 << to_square
                        )  # Clear captured piece on destination square
                        break
            bitboards[piece_type + color * 6] &= ~(
                1 << from_square
            )  # Clear piece from source square
            bitboards[piece_type + color * 6] |= 1 << to_square
            return bitboards

        return bitboards

    def simulate_move(self, move):
        """Simulate a move without updating the board"""
        board_copy = self.board.copy()
        board_copy.updateBoard(move)
        return board_copy

    def refresh_occupant_bitboards(self, board=None):
        """Returns occupants[] as bitboards representing white, black, and combined pieces."""
        if board is None:
            board = self

        board.occupants[0] = tools.combine_bitboard(board.bitboards, 0)
        board.occupants[1] = tools.combine_bitboard(board.bitboards, 1)
        board.occupants[2] = tools.combine_bitboard(board.bitboards)

        return board

    def initialize_attack_map(self):
        """Initializes attack maps."""
        self.attack_map = [0] * 14

    def generate_attack_map(self, board = None):
        """
        Returns bitboards representing squares attacked by each piece and color complex.
        0 - 5: White pawn, knight, bishop, rook, queen, king
        6 - 11: Black pawn, knight, bishop, rook, queen, king
        12: White combined
        13: Black combined
        """
        if board is None:
            board = self
        attack_map = [0] * 14

        for piece in range(12):
            piece_type = piece % 6
            color = piece // 6
            pieces = board.bitboards[piece_type + color * 6]
            board.attack_map[piece] = self.get_attack_map_for_piece_type(piece_type, color, pieces, board)

        board.attack_map[12] = board.attack_map[0] | board.attack_map[1] | board.attack_map[2] | board.attack_map[3] | board.attack_map[4] | board.attack_map[5]
        board.attack_map[13] = board.attack_map[6] | board.attack_map[7] | board.attack_map[8] | board.attack_map[9] | board.attack_map[10] | board.attack_map[11]
        return board.attack_map

    def get_attack_map_for_pieces(self, piece_type, color, pieces, board = None):
        attack_map = 0
        while pieces:
                square = pieces & -pieces
                for move in scope.get_scope_from_square(board, square, color, piece_type):
                    attack_map |= move
                pieces &= pieces - 1
        return attack_map

    # Recalculates sliding pieces' attack maps after a move, thus accepting a copy of occupants after the move is made as opposed to applying the move to the board.
    def get_attack_map_for_sliding_pieces(self, piece_type, color, pieces, occupants = None):
        if occupants == None:
            occupants = self.occupants
        attack_map = 0
        while pieces:
                square = pieces & -pieces
                for move in scope.generate_sliding_scope(occupants, square, color, piece_type):
                    attack_map |= move
                pieces &= pieces - 1
        return attack_map

    def update_attack_map(self, move, board = None):
        """Updates the attack maps given a move."""
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

    def update_consolidated_attack_maps(self, board = None):
        """Updates instance attack maps for white & black."""
        if board is None:
            board = self

        board.attack_map[12] = board.attack_map[0] | board.attack_map[1] | board.attack_map[2] | board.attack_map[3] | board.attack_map[4] | board.attack_map[5]
        board.attack_map[13] = board.attack_map[6] | board.attack_map[7] | board.attack_map[8] | board.attack_map[9] | board.attack_map[10] | board.attack_map[11]
        
        return board.attack_map
            
    def is_square_attacked(self, square, color):
        """Returns if true if a square is attacked by opponent."""
        return self.attack_map[12 + color] & (1 << square)

    def is_square_occupied(self, square, color = None):
        """Returns true if a square is occupied by the specified color. If no color is specified, returns true if the square is occupied by any piece."""
        return self.occupants[color] & (1 << square) if color else self.occupants[2] & (1 << square)

    def is_in_check(self, color, board = None):
        if board is None:
            board = self
        return board.bitboards[5 + color * 6] & board.attack_map[12 + color]