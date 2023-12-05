import tools

class Board:
    # Board representing position of pieces
    def __init__(self, board=None):
        if board:
            self.bitboards = list(board.bitboards)
            self.occupants = list(board.occupants)
            self.castling_rights = board.castling_rights
            self.en_passant_flag = board.en_passant_flag
        else:
            self.new_board()

    def copy_board(self):
        copy_board = Board(self)
        return copy_board

    def new_board(self) -> None:
        self.initialize_bitboard()
        self.initialize_occupants()
        self.initialize_castling()
        self.en_passant_flag = -1 # -1 for false, range(0, 8) for file

    def initialize_bitboard(self):
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

        self.occupants[0] = tools.combine_bitboard(self, 0)
        self.occupants[1] = tools.combine_bitboard(self, 1)
        self.occupants[2] = tools.combine_bitboard(self)

    def initialize_castling(self):
        self.castling_rights = 0b1111

    def make_move(self, move):
        """Updates the board given a move."""
        self.update_board(move)
        self.refresh_occupant_bitboards()
        return self

    def update_board(self, move):
        # Extract information from the move
        from_square = move & 0x3F  # Source square
        to_square = (move >> 6) & 0x3F  # Destination square
        piece_type = (move >> 12) & 0x7  # Piece type (0-5)
        color = (move >> 15) & 0x1  # Color (0 for white, 1 for black)

        # Check if it's a pawn and moving to last rank
        is_promotion = (self.bitboards[0 + color * 6] & (1 << from_square)) and (
            to_square // 8 == 0 or to_square // 8 == 7
        )

        # Castling Update
        # Has rook moved?
        if piece_type == 3:
            if from_square == 7:
                self.castling_rights &= ~(1 << 0)
            elif from_square == 0:
                self.castling_rights &= ~(1 << 1)
            elif from_square == 63:
                self.castling_rights &= ~(1 << 2)
            elif from_square == 56:
                self.castling_rights &= ~(1 << 3)

        # Has rook been captured?
        if self.castling_rights & (1 << 0):
            if not self.bitboards[3] & (1 << 7):
                self.castling_rights &= ~(1 << 0)
        if self.castling_rights & (1 << 1):
            if not self.bitboards[3] & (1 << 0):
                self.castling_rights &= ~(1 << 1)
        if self.castling_rights & (1 << 2):
            if not self.bitboards[9] & (1 << 63):
                self.castling_rights &= ~(1 << 3)
        if self.castling_rights & (1 << 3):
            if not self.bitboards[9] & (1 << 56):
                self.castling_rights &= ~(1 << 3)

        # Capture promotion
        if is_promotion:
            if abs(from_square - to_square) in (7, 9):
                for captured_piece in range(6):
                    if self.bitboards[captured_piece + (1 - color) * 6] & (1 << to_square):
                        self.bitboards[captured_piece + (1 - color) * 6] &= ~(
                            1 << to_square
                        )  # Clear captured piece on promotion square
                        break
            self.bitboards[0 + color * 6] &= ~(
                1 << from_square
            )  # Clear pawn from source square
            self.bitboards[piece_type + color * 6] |= (
                1 << to_square
            )  # Add promoted piece to destination square
            return self.bitboards

        # Pawn moves, non-promotion
        elif piece_type == 0:
            # Infer if it's a capture based on the destination square
            if abs(from_square - to_square) in (7, 9):
                # Determine if capture is en passant
                en_passant = True
                # If diagonal pawn move, but no piece on the destination square, it is en passant
                for captured_piece in range(6):
                    if self.bitboards[captured_piece + (1 - color) * 6] & (1 << to_square):
                        en_passant = False
                        break
                if en_passant:
                    en_passant_square = (
                        to_square + 8 if from_square > to_square else to_square - 8
                    )
                    self.bitboards[0 + (1 - color) * 6] &= ~(
                        1 << en_passant_square
                    )  # Clear pawn captured by en passant
                    self.bitboards[0 + color * 6] &= ~(
                        1 << from_square
                    )  # Clear capturing piece from source square
                else:
                    self.bitboards[0 + color * 6] &= ~(1 << from_square)
                    self.bitboards[captured_piece + (1 - color) * 6] &= ~(
                        1 << to_square
                    )  # Clear destination square (piece captured)

            # Normal move
            else:
                self.bitboards[0 + color * 6] &= ~(1 << from_square)  # Clear pawn from source square

            # Set the destination square in the bitboard
            self.bitboards[piece_type + color * 6] |= 1 << to_square

        # Castling
        elif piece_type == 5:  # King
            # Check for castling
            if abs(from_square - to_square) == 2:
                if color == 0:  # White
                    if to_square == 6:
                        # White king-side castling
                        rook_from_square = 7
                        rook_to_square = 5
                        self.bitboards[3] &= ~(1 << rook_from_square)  # Clear the rook from the source square
                        self.bitboards[3] |= (1 << rook_to_square)  # Set the rook on the destination square
                    elif to_square == 2:
                        # White queen-side castling
                        rook_from_square = 0
                        rook_to_square = 3
                        self.bitboards[3] &= ~(1 << rook_from_square)  # Clear the rook from the source square
                        self.bitboards[3] |= (1 << rook_to_square)  # Set the rook on the destination square
                    self.castling_rights &= 0b1100 # Set white's castling rights to 00
                else:  # Black
                    if to_square == 58:
                        # Black queen-side castling
                        rook_from_square = 56
                        rook_to_square = 59
                        self.bitboards[9] &= ~(1 << rook_from_square)  # Clear the rook from the source square
                        self.bitboards[9] |= (1 << rook_to_square)  # Set the rook on the destination square
                    elif to_square == 62:
                        # Black king-side castling
                        rook_from_square = 63
                        rook_to_square = 61
                        self.bitboards[9] &= ~(1 << rook_from_square)  # Clear the rook from the source square
                        self.bitboards[9] |= (1 << rook_to_square)  # Set the rook on the destination square
                    self.castling_rights &= 0b11 # Set black's castling rights to 00
                self.bitboards[piece_type + color * 6] &= ~(1 << from_square)  # Clear piece from source square                
                self.bitboards[piece_type + color * 6] |= (1 << to_square) # Set the destination square in the bitboard
            else:
                # Check if it's a capture
                if self.occupants[1 - color] & (1 << to_square):
                    for captured_piece in range(6):
                        if self.bitboards[captured_piece + (1 - color) * 6] & (1 << to_square):
                            self.bitboards[captured_piece + (1 - color) * 6] &= ~(1 << to_square)  # Clear captured piece on destination square
                            break
                self.bitboards[piece_type + color * 6] &= ~(1 << from_square)  # Clear piece from source square
                self.bitboards[piece_type + color * 6] |= (1 << to_square) # Set the destination square in the bitboard

                if color: 
                    self.castling_rights &= 0b11
                else: 
                    self.castling_rights &= 0b1100

        # Check if it's a capture
        elif piece_type in (1, 2, 3, 4):
            if self.occupants[1 - color] & (1 << to_square):
                for captured_piece in range(6):
                    if self.bitboards[captured_piece + (1 - color) * 6] & (1 << to_square):
                        self.bitboards[captured_piece + (1 - color) * 6] &= ~(1 << to_square)  # Clear captured piece on destination square
                        break
            self.bitboards[piece_type + color * 6] &= ~(1 << from_square)  # Clear piece from source square
            self.bitboards[piece_type + color * 6] |= (1 << to_square)
            return self.bitboards

        # En passant update
        if self.en_passant_flag != -1:
            self.en_passant_flag = -1
        if (abs(from_square - to_square) == 16 and piece_type == 0):
            self.en_passant_flag = to_square % 8

        return self.bitboards

    def simulate_move(self, move):
        """Simulate a move without updating the board"""
        board_copy = self.copy_board()
        board_copy.update_board(move)
        board_copy.refresh_occupant_bitboards()

        return board_copy

    def refresh_occupant_bitboards(self):
        """Returns occupants[] as bitboards representing white, black, and combined pieces."""

        self.occupants[0] = tools.combine_bitboard(self, 0)
        self.occupants[1] = tools.combine_bitboard(self, 1)
        self.occupants[2] = tools.combine_bitboard(self)

    def is_square_attacked(self, square, color):
        """Returns if true if a square is attacked by opponent."""
        return self.attack_map[12 + color] & (1 << square)

    def is_square_occupied(self, square, color=None):
        """Returns true if a square is occupied by the specified color. If no color is specified, returns true if the square is occupied by any piece."""
        return self.occupants[color] & (1 << square) if color else self.occupants[2] & (1 << square)

    def is_in_check(self, color, board=None):
        if board is None:
            board = self
        return board.bitboards[5 + color * 6] & board.attack_map[12 + color]