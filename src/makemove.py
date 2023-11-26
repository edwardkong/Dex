# Standard UCI move notation includes 4 characters, source square and destination square. 
# Castling is specified by king position (i.e. e1g1).
# Promotions are specified with 5 characters, to disambiguate promting pieces (i.e. g7g8q)

def uci_to_int(lan_move, bitboards):
    # Basic error checking
    if not lan_move or not bitboards:
        print("Invalid input.")
        return None

    # Convert UCI LAN to coordinates
    from_square, to_square, promotion = lan_move[:2], lan_move[2:4], lan_move[4:]

    # Map coordinates to bitboard indices
    from_index = 8 * (int(from_square[1]) - 1) + ord(from_square[0]) - ord('a')
    to_index = 8 * (int(to_square[1]) - 1) + ord(to_square[0]) - ord('a')

    # Determine the piece type & color
    for piece_color in range(12):
        color = piece_color & 1
        piece_type = piece_color >> 1

        if (bitboards[piece_type][color] & (1 << from_index)):
            break
    else:
        print("Invalid move: No piece found on the source square.")
        return None

    # Consider if the move is a promotion
    if promotion:
        promotion_mapping = {'n': 1, 'b': 2, 'r': 3, 'q': 4}
        piece_type = promotion_mapping.get(promotion.lower(), 0)
    
    # Generate the move as a 32-bit integer
    return from_index | (to_index << 6) | (piece_type << 12) | (color << 15)

def int_to_uci(move):
    from_square = move & 0x3F  # Source square
    to_square = (move >> 6) & 0x3F  # Destination square
    piece_type = (move >> 12) & 0x7  # Piece type (0-5)
    color = (move >> 15) & 0x1  # Color (0 for white, 1 for black)
    f_file = from_square % 8
    f_rank = from_square // 8
    f_s = chr(ord('a') + f_file) + str(f_rank + 1)

    t_file = to_square % 8
    t_rank = to_square // 8
    t_s = chr(ord('a') + t_file) + str(t_rank + 1)


    return f"{f_s}{t_s}"