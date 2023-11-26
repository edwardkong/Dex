import position, tools
import copy

# Constants for piece types
PAWN = 0
KNIGHT = 1
BISHOP = 2
ROOK = 3
QUEEN = 4
KING = 5

# Constants for colors
WHITE = 0
BLACK = 1

def initialize_bitboard():
    # Initialize an empty bitboard for each piece type and color
    bitboards = {
        PAWN: {WHITE: 0, BLACK: 0},
        KNIGHT: {WHITE: 0, BLACK: 0},
        BISHOP: {WHITE: 0, BLACK: 0},
        ROOK: {WHITE: 0, BLACK: 0},
        QUEEN: {WHITE: 0, BLACK: 0},
        KING: {WHITE: 0, BLACK: 0}
    }

    # Set the bits for each piece in the starting position
    # ! HACKED - FIX
    starting_position = (
        "RNBQKBNR"
        "PPPPPPPP"
        "        "
        "        "
        "        "
        "        "
        "pppppppp"
        "rnbqkbnr"
    )

    for square, piece in enumerate(starting_position):
        if piece == ' ':
            continue

        piece_type = "PNBRQK".index(piece.upper())
        color = 0 if piece.isupper() else 1

        bitboards[piece_type][color] |= 1 << square

    return bitboards

# Accepts bitboards positions and a 32bit move, returns updated bitboards
def update_board(BB, move) -> dict:
    bitboards = copy.deepcopy(BB)
    # Extract information from the move
    from_square = move & 0x3F  # Source square
    to_square = (move >> 6) & 0x3F  # Destination square
    piece_type = (move >> 12) & 0x7  # Piece type (0-5)
    color = (move >> 15) & 0x1  # Color (0 for white, 1 for black)

     # Check if it's a pawn and moving to last rank
    is_promotion = (bitboards[0][color] & (1 << from_square)) and (to_square // 8 == 0 or to_square // 8 == 7)

    # ! Add capture promotion
    if is_promotion:
        if abs(from_square - to_square) in (7, 9):
            for captured_piece in range(6):
                if (bitboards[captured_piece][1 - color] & (1 << to_square)):
                    bitboards[captured_piece][1 - color] &= ~(1 << to_square) # Clear captured piece on promotion square
                    break
        bitboards[0][color] &= ~(1 << from_square) # Clear pawn from source square
        bitboards[piece_type][color] |= 1 << to_square
        return bitboards

    # Pawn moves, non-promotion
    elif piece_type == 0:
        # Infer if it's a capture based on the destination square
        if abs(from_square - to_square) in (7, 9):
            # Determine if capture is en passant
            en_passant = True
            # If diagonal pawn move, but no piece on the destination square, it is en passant
            for captured_piece in range(6):
                if (bitboards[captured_piece][1 - color] & (1 << to_square)):
                    en_passant = False
                    break
            if en_passant:
                en_passant_square = to_square + 8 if from_square > to_square else to_square - 8
                bitboards[0][1-color] &= ~(1 << en_passant_square) # Clear pawn captured by en passant
                bitboards[0][color] &= ~(1 << from_square) # Clear capturing piece from source square
            else:
                bitboards[0][color] &= ~(1 << from_square)
                bitboards[captured_piece][1 - color] &= ~(1 << to_square) # Clear destination square (piece captured)
            
        # Normal move
        else:
            bitboards[0][color] &= ~(1 << from_square) # Clear pawn from source square

        # Set the destination square in the bitboard
        bitboards[piece_type][color] |= 1 << to_square
        return bitboards

    elif piece_type in (1, 2, 3, 4, 5):
        # Check if it's a capture
        for captured_piece in range(6):
            if (bitboards[captured_piece][1 - color] & (1 << to_square)):
                bitboards[captured_piece][1 - color] &= ~(1 << to_square) # Clear captured piece on destination square
                break
        bitboards[piece_type][color] &= ~(1 << from_square) # Clear piece from source square
        bitboards[piece_type][color] |= 1 << to_square
        return bitboards

    # Castling
    elif piece_type == 5:  # King
        # Check for castling
        if abs(from_square - to_square) == 2:
            if color == 0:  # White
                if to_square == 6:
                    # White king-side castling
                    rook_from_square = 7
                    rook_to_square = 5
                    bitboards[3][color] &= ~(1 << rook_from_square)  # Clear the rook from the source square
                    bitboards[3][color] |= 1 << rook_to_square  # Set the rook on the destination square
                elif to_square == 2:
                    # White queen-side castling
                    rook_from_square = 0
                    rook_to_square = 3
                    bitboards[3][color] &= ~(1 << rook_from_square)  # Clear the rook from the source square
                    bitboards[3][color] |= 1 << rook_to_square  # Set the rook on the destination square
            else:  # Black
                if to_square == 58:
                    # Black queen-side castling
                    rook_from_square = 56
                    rook_to_square = 59
                    bitboards[3][color] &= ~(1 << rook_from_square)  # Clear the rook from the source square
                    bitboards[3][color] |= 1 << rook_to_square  # Set the rook on the destination square
                elif to_square == 62:
                    # Black king-side castling
                    rook_from_square = 63
                    rook_to_square = 61
                    bitboards[3][color] &= ~(1 << rook_from_square)  # Clear the rook from the source square
                    bitboards[3][color] |= 1 << rook_to_square  # Set the rook on the destination square
        else: 
            bitboards[piece_type][color] &= ~(1 << from_square) # Clear piece from source square

        # Set the destination square in the bitboard
        bitboards[piece_type][color] |= 1 << to_square
        return bitboards

    return bitboards

# Returns color if occupied or -1 if unoccupied
def is_square_occupied(bitboards, square) -> int:
    for piece in range(12):
        color = piece & 1
        piece_type = piece >> 1
        if bitboards[piece_type][color] & (1 << square):
            return color
    return -1

def is_square_occupied_friendly(bitboards, square, color) -> bool:
    for piece_type in range(6):
        if bitboards[piece_type][color] & (1 << square):
            return True
    return False

# If color = white, checks if attacked by black
def is_square_attacked(bitboards, square, color):
    for piece_type in range(6):
        pieces = bitboards[piece_type][1 - color]
        while pieces:
            from_square = tools.bitscan_lsb(pieces)
            if piece_type == 0 and is_in_pawn_scope(from_square, square, 1 - color):
                return True
            elif piece_type == 1 and is_in_knight_scope(from_square, square):
                return True
            elif piece_type == 2 and is_in_bishop_scope(bitboards, from_square, square):
                return True
            elif piece_type == 3 and is_in_rook_scope(bitboards, from_square, square):
                return True
            elif piece_type == 4 and is_in_queen_scope(bitboards, from_square, square):
                return True
            elif piece_type == 5 and is_in_king_scope(from_square, square):
                return True
            pieces &= pieces - 1
    return False

def is_in_pawn_scope(attacker_square, target_square, color) -> bool:
    attacker_rank, attacker_file = divmod(attacker_square, 8)
    target_rank, target_file = divmod(target_square, 8)

    return (abs(target_file - attacker_file) == 1) and ((target_rank - attacker_rank) == (1 if color == 0 else -1))

def is_in_knight_scope(attacker_square, target_square) -> bool:
    rank_diff = abs((attacker_square // 8) - (target_square // 8))
    file_diff = abs((attacker_square % 8) - (target_square % 8))

    return (rank_diff == 1 and file_diff == 2) or (rank_diff == 2 and file_diff == 1)

def is_in_bishop_scope(bitboards, attacker_square, target_square) -> bool:
    attacker_rank, attacker_file = divmod(attacker_square, 8)
    target_rank, target_file = divmod(target_square, 8)

    if abs(attacker_rank - target_rank) != abs(attacker_file - target_file):
        return False

    rank_increment = 1 if target_rank > attacker_rank else -1
    file_increment = 1 if target_file > attacker_file else -1

    current_rank, current_file = attacker_rank + rank_increment, attacker_file + file_increment
    while current_rank != target_rank:
        current_square = 8 * current_rank + current_file
        if is_square_occupied(bitboards, current_square) > -1:
            return False
        current_rank += rank_increment
        current_file += file_increment

    return True

def is_in_rook_scope(bitboards, attacker_square, target_square) -> bool:
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
            if is_square_occupied(bitboards, current_square) > -1:
                # There is a piece in the path of the rook
                return False
            current_file += file_increment
    else:  # Moving vertically
        rank_increment = 1 if target_rank > attacker_rank else -1
        current_rank = attacker_rank + rank_increment
        while current_rank != target_rank:
            current_square = 8 * current_rank + attacker_file
            if is_square_occupied(bitboards, current_square) > -1:
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

def is_in_check(bitboards, color):
    king_square = tools.bitscan_lsb(bitboards[5][color])
    if is_square_attacked(bitboards, king_square, color):
        return True

def is_legal_position(bitboards, color):
    # Color = Turn to play
    if is_in_check(bitboards, 1 - color):
        return False
    return True

if __name__ == "__main__":
    # Initialize bitboards for the starting position
    position = initialize_bitboard()
