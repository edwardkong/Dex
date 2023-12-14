def capture_priority(board, move, color):

    from_square = move & 0x3F  # Source square
    to_square = (move >> 6) & 0x3F  # Destination square
    piece_type = (move >> 12) & 0x7  # Piece type (0-5)
    color = (move >> 15) & 0x1  # Color (0 for white, 1 for black)

    for piece_type in range(6):
        if board.bitboards[piece_type] & (1 << from_square):
            break
    
    if board.occupants[1 - color] & (1 << to_square):
        if board.bitboards[(1 - color) * 6] & (1 << to_square):
            return 10 + piece_type
        if board.bitboards[1 + (1 - color) * 6] & (1 << to_square):
            return 20 + piece_type
        if board.bitboards[2 + (1 - color) * 6] & (1 << to_square):
            return 30 + piece_type
        if board.bitboards[3 + (1 - color) * 6] & (1 << to_square):
            return 40 + piece_type
        if board.bitboards[4 + (1 - color) * 6] & (1 << to_square):
            return 50 + piece_type
        else:
            return 0

    else:
        return 0