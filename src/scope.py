
    def get_scope_from_square(board, from_square, color, piece_type):
        if piece_type == 0:
            return generate_pawn_scope(from_square, color)
        elif piece_type == 1:
            return generate_knight_scope(from_square)
        elif piece_type in (2, 3, 4):
            return generate_sliding_scope(board.occupants, from_square, color, piece_type)
        elif piece_type == 5:
            return generate_king_scope(from_square)

def generate_pawn_scope(from_square, color):
        """Returns pawn's scope given a square."""
        candidate = []

        file = from_square % 8
        direction = [-7, -9] if color else [9, 7]

        if file == 0:
            candidate.append(from_square + direction[0])
        elif file == 7:
            candidate.append(from_square + direction[1])
        else:
            candidate.extend([from_square + d for d in direction])
        
        return candidate

def generate_knight_scope(from_square):
    """Returns knight's scope given a square."""
    candidate = []
    rank, file = divmod(from_square, 8)

    # Possible relative moves for a knight
    direction = [
        (2, 1), (1, 2),
        (-2, 1), (-1, 2),
        (2, -1), (1, -2),
        (-2, -1), (-1, -2)
    ]

    for d in direction:
        new_rank, new_file = rank + d[0], file + d[1]

        # Check if the new square is within the board boundaries
        if 0 <= new_rank < 8 and 0 <= new_file < 8:
            candidate.append(8 * new_rank + new_file)
    return candidate

def generate_sliding_scope(occupants, from_square, color, piece_type):
        """
        Takes a board's occupants.
        Returns sliding piece's scope given a square. piece_type -> {2: Bishop, 3: Rook, 4: Queen}
        """
        candidate = []
        rank, file = divmod(from_square, 8)

        # Possible relative moves for a sliding piece
        sliding_moves = [
            (1, 1), (1, -1), (-1, 1), (-1, -1),
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]
        if piece_type == 2:
            directions = sliding_moves[:4]
        elif piece_type == 3:
            directions = sliding_moves[4:]
        elif piece_type == 4:
            directions = sliding_moves

        for d in directions:
            new_rank, new_file = rank + move[0], file + move[1]
            while 0 <= new_rank < 8 and 0 <= new_file < 8:
                new_square = 8 * new_rank + new_file
                # Square occupied
                if (occupants[2] & (1 << new_square)):
                    candidate.append(new_square)
                else:
                    candidate.append(new_square)
                    rank, file = new_rank + move[0], new_file + move[1]
        return candidate

    def generate_king_scope(from_square):
        """Returns king's scope given a square."""
        candidate = []
        rank, file = divmod(from_square, 8)

        # Possible relative moves for a king
        direction = [
            (1, 1), (1, 0), (1, -1),
            (0, 1), (0, -1),
            (-1, 1), (-1, 0), (-1, -1)
        ]

        for d in direction:
            new_rank, new_file = rank + d[0], file + d[1]

            # Check if the new square is within the board boundaries
            if 0 <= new_rank < 8 and 0 <= new_file < 8:
                candidate.append(8 * new_rank + new_file)
        return candidate