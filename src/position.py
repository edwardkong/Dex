import position, tools, evaluate
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
    bitboards = [0] * 12

    starting_position = [
        0xFF00, # WP 0
        0x42, # WN 1 
        0x24, # WB 2
        0x81, # WR 3
        0x8, # WQ 4
        0x10, # WK 5
        0xFF000000000000, #BP 6 
        0x4200000000000000, #BN 7 
        0x2400000000000000, #BB 8
        0x8100000000000000, #BR 9
        0x800000000000000, #BQ 10
        0x1000000000000000, #BK 11
        0, # W occupants 12
        0, # B occupants 13
        0, # All occupants 14
        0 # Castling rules (wk, wq, bk, bq)
    ]

    starting_position[12] = tools.combine_bitboard(starting_position, 0)
    starting_position[13] = tools.combine_bitboard(starting_position, 1)
    starting_position[14] = tools.combine_bitboard(starting_position)
    starting_position[15] = 0b1111

    return starting_position

def refresh_occupant_bitboards(bitboards):
    bitboards[12] = tools.combine_bitboard(bitboards, 0)
    bitboards[13] = tools.combine_bitboard(bitboards, 1)
    bitboards[14] = tools.combine_bitboard(bitboards)
    return bitboards

# Accepts bitboards positions and a 32bit move, returns updated bitboards
def update_board(bitboards, move) -> list:
    # Extract information from the move
    from_square = move & 0x3F  # Source square
    to_square = (move >> 6) & 0x3F  # Destination square
    piece_type = (move >> 12) & 0x7  # Piece type (0-5)
    color = (move >> 15) & 0x1  # Color (0 for white, 1 for black)

     # Check if it's a pawn and moving to last rank
    is_promotion = (bitboards[0 + color*6] & (1 << from_square)) and (to_square // 8 == 0 or to_square // 8 == 7)

    # ! Add capture promotion
    if is_promotion:
        if abs(from_square - to_square) in (7, 9):
            for captured_piece in range(6):
                if (bitboards[captured_piece + (1 - color)*6] & (1 << to_square)):
                    bitboards[captured_piece + (1 - color)*6] &= ~(1 << to_square) # Clear captured piece on promotion square
                    break
        bitboards[0 + color*6] &= ~(1 << from_square) # Clear pawn from source square
        bitboards[piece_type + color*6] |= 1 << to_square
        return bitboards

    # Pawn moves, non-promotion
    elif piece_type == 0:
        # Infer if it's a capture based on the destination square
        if abs(from_square - to_square) in (7, 9):
            # Determine if capture is en passant
            en_passant = True
            # If diagonal pawn move, but no piece on the destination square, it is en passant
            for captured_piece in range(6):
                if (bitboards[captured_piece + (1 - color)*6] & (1 << to_square)):
                    en_passant = False
                    break
            if en_passant:
                en_passant_square = to_square + 8 if from_square > to_square else to_square - 8
                bitboards[0 + (1 - color)*6] &= ~(1 << en_passant_square) # Clear pawn captured by en passant
                bitboards[0 + color*6] &= ~(1 << from_square) # Clear capturing piece from source square
            else:
                bitboards[0 + color*6] &= ~(1 << from_square)
                bitboards[captured_piece + (1 - color)*6] &= ~(1 << to_square) # Clear destination square (piece captured)
            
        # Normal move
        else:
            bitboards[0 + color*6] &= ~(1 << from_square) # Clear pawn from source square

        # Set the destination square in the bitboard
        bitboards[piece_type + color*6] |= 1 << to_square
        return bitboards

    # Castling
    elif piece_type == 5:  # King
        # Check for castling
        if color == 0: bitboards[15] &= (0b1100)
        else: bitboards[15] &= (0b11)
        
        if abs(from_square - to_square) == 2:
            if color == 0:  # White
                if to_square == 6:
                    # White king-side castling
                    rook_from_square = 7
                    rook_to_square = 5
                    bitboards[3 + color*6] &= ~(1 << rook_from_square)  # Clear the rook from the source square
                    bitboards[3 + color*6] |= 1 << rook_to_square  # Set the rook on the destination square
                elif to_square == 2:
                    # White queen-side castling
                    rook_from_square = 0
                    rook_to_square = 3
                    bitboards[3 + color*6] &= ~(1 << rook_from_square)  # Clear the rook from the source square
                    bitboards[3 + color*6] |= 1 << rook_to_square  # Set the rook on the destination square
                bitboards[15] &= (0b11)
            else:  # Black
                if to_square == 58:
                    # Black queen-side castling
                    rook_from_square = 56
                    rook_to_square = 59
                    bitboards[3 + color*6] &= ~(1 << rook_from_square)  # Clear the rook from the source square
                    bitboards[3 + color*6] |= 1 << rook_to_square  # Set the rook on the destination square
                elif to_square == 62:
                    # Black king-side castling
                    rook_from_square = 63
                    rook_to_square = 61
                    bitboards[3 + color*6] &= ~(1 << rook_from_square)  # Clear the rook from the source square
                    bitboards[3 + color*6] |= 1 << rook_to_square  # Set the rook on the destination square   
                bitboards[15] &= (0b1100)         

            bitboards[piece_type + color*6] &= ~(1 << from_square) # Clear piece from source square
            # Set the destination square in the bitboard
            bitboards[piece_type + color*6] |= 1 << to_square
        
            return bitboards

    # Has rook moved?
    elif piece_type == 4:
        if from_square == 7:
            bitboards[15] &= ~(1 << 3)
        elif from_square == 0:
            bitboards[15] &= ~(1 << 2)  
        elif from_square == 63:
            bitboards[15] &= ~(1 << 1)   
        elif from_square == 56:
            bitboards[15] &= ~(1)

    # Has rook been captured?
    if bitboards[15] & (1 << 3):
        if not bitboards[3] & (1 << 7):
            bitboards[15] &= ~(1 << 3)
    if bitboards[15] & (1 << 2):
        if not bitboards[3] & (1 << 0):
            bitboards[15] &= ~(1 << 2)    
    if bitboards[15] & (1 << 1):
        if not bitboards[9] & (1 << 63):
            bitboards[15] &= ~(1 << 1)    
    if bitboards[15] & (1):
        if not bitboards[9] & (1 << 56):
            bitboards[15] &= ~(1)

    # Check if it's a capture
    if piece_type in (1, 2, 3, 4, 5):
        if bitboards[12 + (1 - color)] & (1 << to_square):
            for captured_piece in range(6):
                if (bitboards[captured_piece + (1 - color)*6] & (1 << to_square)):
                    bitboards[captured_piece + (1 - color)*6] &= ~(1 << to_square) # Clear captured piece on destination square
                    break
        bitboards[piece_type + color*6] &= ~(1 << from_square) # Clear piece from source square
        bitboards[piece_type + color*6] |= 1 << to_square
        return bitboards
    
    return bitboards

def simulate_move(bitboards, move):
    temp_board = bitboards.copy()

    return refresh_occupant_bitboards(update_board(temp_board, move))

# Checks if any opponent pieces has line of sight with the color king
def in_los(bitboards, color):
    king_square = tools.bitscan_lsb(bitboards[5 + color*6])
    king_rank, king_file = divmod(king_square, 8)

    # Bishop
    bishops = bitboards[2 + (1- color)*6]
    while bishops:
        from_square = tools.bitscan_lsb(bishops)
        attacker_rank, attacker_file = divmod(from_square, 8)

        if abs(attacker_rank - king_rank) == abs(attacker_file - king_file):
            return True
        bishops &= bishops - 1

    # Rook
    rooks = bitboards[3 + (1 - color)*6]
    while rooks:
        from_square = tools.bitscan_lsb(rooks)
        attacker_rank, attacker_file = divmod(from_square, 8)

        if attacker_rank == king_rank or attacker_file == king_file:
            return True
        rooks &= rooks - 1
    # Queen
    queens = bitboards[4 + (1 - color)*6]
    while queens:
        from_square = tools.bitscan_lsb(queens)
        attacker_rank, attacker_file = divmod(from_square, 8)

        if attacker_rank == king_rank or attacker_file == king_file:
            return True
        elif abs(attacker_rank - king_rank) == abs(attacker_file - king_file):
            return True
        queens &= queens - 1
    return False


# Returns bool
def is_square_occupied_orig(bitboards, square) -> bool:
    
    for piece in range(12):
        if (1 << square) > bitboards[piece]:
            continue
        elif bitboards[piece] & (1 << square):
            return True
    return False
    
def is_square_occupied(bitboards, square): #optimized with occupant bitboards
    return bitboards[14] & (1 << square)
    

def is_square_occupied_friendly(bitboards, square, color) -> bool:
    return bitboards[12 + color] & (1 << square)

# If color = white, checks if attacked by black
def is_square_attacked(bitboards, square, color):
    for piece_type in range(6):
        pieces = bitboards[piece_type + (1 - color)*6]
        while pieces:
            from_square = tools.bitscan_lsb(pieces)
            if piece_type == 0:
                if color == 0:
                    if square + 10 <= tools.bitscan_lsb(pieces):
                        pieces = 0
                        continue
                elif color == 1:
                    if square - 10 >= tools.bitscan_msb(pieces):
                        pieces = 0
                        continue
                if is_in_pawn_scope(from_square, square, 1 - color):
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
        if current_rank >= 8 or current_rank < 0 or current_file >= 8 or current_file < 0:
            return False
        current_square = 8 * current_rank + current_file
        if (bitboards[14] & (1 << current_square)):
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
            if (bitboards[14] & (1 << current_square)):
                # There is a piece in the path of the rook
                return False
            current_file += file_increment
    else:  # Moving vertically
        rank_increment = 1 if target_rank > attacker_rank else -1
        current_rank = attacker_rank + rank_increment
        while current_rank != target_rank:
            current_square = 8 * current_rank + attacker_file
            if (bitboards[14] & (1 << current_square)):
                # There is a piece in the path of the rook
                return False
            current_rank += rank_increment

    return True

def can_castle(bitboards, color) -> bool:
    kingside, queenside = False, False
    # King cannot castle while in check
    if is_in_check(bitboards, color):
        return False, False
    if color == 0:
        if bitboards[15] & (1 << 3):
            # We only check if the castle through square is in check, because the resulting position will be illegal if the destination square is in check
            if not bitboards[14] & (0b11 << 5):
                if is_square_attacked(bitboards, 5, color):
                    kingside = False
                else:
                    kingside = True
        
        if bitboards[15] & (1 << 2):
            if not bitboards[14] & (0b111 << 1):
                if is_square_attacked(bitboards, 3, color):
                    queenside = False
                else:
                    queenside = True
    elif color == 1:
        if bitboards[15] & (1 << 1):
            if not bitboards[14] & (0b11 << 61):
                if is_square_attacked(bitboards, 61, color):
                    kingside = False
                else:
                    kingside = True
        
        if bitboards[15] & (1 << 0):
            if not bitboards[14] & (0b111 << 57):
                if is_square_attacked(bitboards, 59, color):
                    queenside = False
                else:
                    queenside = True
    
    return kingside, queenside

def is_in_queen_scope(bitboards, attacker_square, target_square) -> bool:
    return is_in_bishop_scope(bitboards, attacker_square, target_square) or is_in_rook_scope(bitboards, attacker_square, target_square)

def is_in_king_scope(attacker_square, target_square) -> bool:
    attacker_rank, attacker_file = divmod(attacker_square, 8)
    target_rank, target_file = divmod(target_square, 8)

    return (abs(target_file - attacker_file) <= 1) and (abs(target_rank - attacker_rank) <= 1)

def is_in_check(bitboards, color):
    king_square = tools.bitscan_lsb(bitboards[5 + color*6])
    if is_square_attacked(bitboards, king_square, color):
        return True
    return False

def is_legal_position(bitboards, color):
    # Color = Turn to play
    if is_in_check(bitboards, 1 - color):
        return False
    return True


def get_scope(bitboards, piece_type, square, color):
    scope = []
    rank, file = divmod(square, 8)

    if piece_type == 0:
        if 0 <= file < 7:
            attacked = (square - 7) if color else (square + 9)
            if 0 <= attacked < 64:
                scope.append(attacked)
        if 1 <= file < 8:
            attacked = (square - 9) if color else (square + 7)
            if 0 <= attacked < 64:
                scope.append(attacked)

    elif piece_type == 1:
        for i in ([2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]):
            attacked = square + i[0] + i[1]*8
            if 0 <= attacked < 64:
                scope.append(attacked)

    elif piece_type == 2:
        for i in ([1, 1], [1, -1], [-1, 1], [-1, -1]):
            curr_rank = rank + i[0]
            curr_file = file + i[1]
            while 0 <= curr_rank < 8 and 0 <= curr_file < 8:
                attacked = curr_rank*8 + file
                if not is_square_occupied(bitboards, attacked):
                    if 0 <= attacked < 64:
                        scope.append(attacked)
                else:
                    break
                curr_rank += i[0]
                curr_file += i[1]

    ### FINISH ?
    #if piece_type == 3:
    #elif piece_type == 4:
    #elif piece_type == 5:

def gen_attacked_squares(bitboards, color):
    attacked_squares = 0
    get_scope()

def update_attacked_squares(attacked_squares, move):
    # Accepts a bitboard of attacked squares (for a certain color) and updates it when a move is made.

    return

if __name__ == "__main__":
    # Initialize bitboards for the starting position
    position = initialize_bitboard()
