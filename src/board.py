from zobristhash import ZobristHash
import tools
# implement zobrist key gen on board update + tt implementation

class Board:
    # Board representing position of pieces
    def __init__(self, board=None):
        if board:
            self.color = board.color
            self.bitboards = list(board.bitboards)
            self.occupants = list(board.occupants)
            self.castling_rights = board.castling_rights
            self.en_passant_flag = board.en_passant_flag
            self.zobrist_key = board.zobrist_key
            # Count commital/irreversible moves such as
            # pawn pushes or captures. Used for 
            # age-based eviction in TranpositionTable.
            self.commits = board.commits
        else:
            self.new_board()

    def copy_board(self):
        copy_board = Board(self)
        return copy_board

    def new_board(self) -> None:
        self.color = 0
        self.initialize_bitboard()
        self.initialize_occupants()
        self.initialize_castling()
        self.en_passant_flag = -1 # -1 for false, range(0, 8) for file
        self.zobrist_key = ZobristHash.create_hash_key(self)
        self.commits = 0

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
        self.color = 1 - self.color
        return self

    def is_castling(self, from_square, to_square, piece_type):
        """Checks if a move is castle."""
        if piece_type % 6 == 5 and abs(from_square - to_square) == 2:
                return True
        return False

    def rook_update_castling(self, from_square, to_square):
        """Updates castling rights by checking if a piece moves 
        to or from a rook's starting square.
        """
        rook_castling_rights = {
            7: (1 << 0),
            0: (1 << 1),
            63: (1 << 2),
            56: (1 << 3)
        }
        # Check both in case rook takes rook
        if from_square in rook_castling_rights:
            self.castling_rights &= ~rook_castling_rights.get(from_square)
        if to_square in rook_castling_rights:
            self.castling_rights &= ~rook_castling_rights.get(to_square)
    
    def king_update_castling(self, to_square, color):
        """Updates rook position and castling rights."""
        # Stores rook's (from, to) squares, key as to_square
        rook_move_squares = {
            6: (7, 5), # White Kingside 0b0001
            2: (0, 3), # White Queenside 0b0010
            58: (56, 59), # Black Kingside 0b0100
            62: (63, 61) # Black Queenside 0b1000
        }
        rook_from_square, rook_to_square = rook_move_squares.get(to_square)
        self.remove_from_bitboard(3 + color * 6, rook_from_square)
        self.add_to_bitboard(3 + color * 6, rook_to_square)
        
    def piece_captured(self, from_square, to_square, color, piece_type=None):
        """Returns the piece_type (0-12) of the captured piece 
        if a piece was captured. Returns -1 if not a capture.
        """
        # Diagonal pawn move with no piece on destination square is en passant
        if piece_type == 0 and abs(from_square - to_square) in (7, 9):
            if not self.occupants[1 - color] & (1 << to_square):
                return 0 + (1 - color) * 6
        # Normal capture
        if self.occupants[1 - color] & (1 << to_square):
            for piece in range(6):
                captured_piece = piece + (1 - color) * 6
                if self.bitboards[captured_piece] & (1 << to_square):
                    return captured_piece
        return -1
        
    def is_en_passant(self, from_square, to_square, color):
        """Returns the en passant square (pawn that was captured) 
        if move was en passant. Returns -1 if not en passant.
        """
        if (abs(from_square - to_square) in (7, 9) and 
            not self.occupants[1 - color] & (1 << to_square)):
            return to_square + 8 if from_square > to_square else to_square - 8
        return -1
    
    def remove_from_bitboard(self, piece_type, square):
        """Removes a piece from its bitboard. piece_type in range 0:12."""
        self.bitboards[piece_type] &= ~(1 << square)
        self.zobrist_key ^= ZobristHash.table[square][piece_type]

    def add_to_bitboard(self, piece_type, square):
        """Adds a piece to its bitboard. piece_type in range 0:12."""
        self.bitboards[piece_type] |= (1 << square)
        self.zobrist_key ^= ZobristHash.table[square][piece_type]

    def update_board(self, move):
        """Updates piece bitboards based on move as a 17-bit int."""
        # Extract information from the move
        from_square = move & 0x3F  # Source square
        to_square = (move >> 6) & 0x3F  # Destination square
        piece_type = (move >> 12) & 0x7  # Piece type (0-5)
        color = (move >> 15) & 0x1  # Color (0 for white, 1 for black)
        promotion_flag = (move >> 16) & 0x1 # 1 if promotion
        # Added capture flag for quiescence search, but not yet
        # refactored other logic to utilize flag.
        capture_flag = (move >> 17) & 0x1

        piece_type_color = piece_type + color * 6
        captured_piece = self.piece_captured(from_square, to_square, 
                                             color, piece_type)
        is_capture = captured_piece > -1
        commital = is_capture
        
        # Reset Zobrist Hash for color, castling, and ep
        self.zobrist_key ^= ZobristHash.table[64]
        self.zobrist_key ^= ZobristHash.table[65][self.castling_rights]
        self.zobrist_key ^= ZobristHash.table[66][self.en_passant_flag]

        # Promotion
        if promotion_flag:
            # Piece_type contains the promotion piece if promotion_flag = 1
            promotion_piece = piece_type + color * 6
            piece_type = 0 + color * 6
            if is_capture:
                self.remove_from_bitboard(captured_piece, to_square)
            self.remove_from_bitboard(piece_type, from_square)
            self.add_to_bitboard(promotion_piece, to_square)
            commital = True

        # Pawn moves, non-promotion
        elif piece_type == 0:
            if is_capture:
                ep_square = self.is_en_passant(from_square, to_square, color)
                if ep_square != -1 and self.en_passant_flag != -1:
                    self.remove_from_bitboard(captured_piece, ep_square)
                else:
                    self.remove_from_bitboard(captured_piece, to_square)
            self.remove_from_bitboard(piece_type_color, from_square)
            self.add_to_bitboard(piece_type_color, to_square)
            commital = True

        # Update en passant flag
        if (abs(from_square - to_square) == 16 and piece_type == 0):
            self.en_passant_flag = to_square % 8
        else:
            self.en_passant_flag = -1

        # King moves
        if piece_type == 5:
            if is_capture:
                self.remove_from_bitboard(captured_piece, to_square)
            elif self.is_castling(from_square, to_square, piece_type):
                # Update rook position and castling rights
                self.king_update_castling(to_square, color)
                commital = True
            self.remove_from_bitboard(piece_type_color, from_square)
            self.add_to_bitboard(piece_type_color, to_square)
            self.castling_rights &= (0b1100 >> (color * 2))

        # Piece moves
        if piece_type in (1, 2, 3, 4):
            if is_capture:
                self.remove_from_bitboard(captured_piece, to_square)
            self.remove_from_bitboard(piece_type_color, from_square)
            self.add_to_bitboard(piece_type_color, to_square)

        # Any piece moves from or to a rook's starting square
        if (self.castling_rights and 
            (from_square in (7, 0, 63, 56) or to_square in (7, 0, 63, 56))):
            self.rook_update_castling(from_square, to_square)

        self.zobrist_key ^= ZobristHash.table[65][self.castling_rights]
        self.zobrist_key ^= ZobristHash.table[66][self.en_passant_flag]

        if commital:
            self.commits += 1

        return self.bitboards

    def sim_move(self, move):
        """Returns a copy of the updated board."""
        board_copy = self.copy_board()
        board_copy.update_board(move)
        board_copy.refresh_occupant_bitboards()
        board_copy.color = 1 - self.color

        return board_copy

    def is_commital_move(self, move):
        from_square = move & 0x3F  # Source square
        to_square = (move >> 6) & 0x3F  # Destination square
        piece_type = (move >> 12) & 0x7  # Piece type (0-5)
        color = (move >> 15) & 0x1  # Color (0 for white, 1 for black)
        promotion_flag = (move >> 16) & 0x1 # 1 if promotion

        if piece_type == 0 or promotion_flag:
            return True
        if self.piece_captured(from_square, to_square, color, piece_type) > -1:
            return True
        if self.is_castling(from_square, to_square, piece_type):
            return True
        return False

    def refresh_occupant_bitboards(self):
        """Returns occupants[] bitboards representing occupied squares.
        White pieces: occupants[0]
        Black pieces: occupants[1]
        All pieces: occupants[2]
        """
        self.occupants[0] = tools.combine_bitboard(self, 0)
        self.occupants[1] = tools.combine_bitboard(self, 1)
        self.occupants[2] = tools.combine_bitboard(self)