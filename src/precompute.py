class Precompute:
    def __init__(self):
        self.diag_lookup = {}
        self.a_diag_lookup = {}
        self.initialize_diagonal_masks
        self.initialize_antidiagonal_masks

        self.rank, self.file = self.precompute_orthogonal_moves() # Verified
        self.diagonal, self.anti_diagonal = self.precompute_diagonal_moves() # Verified

    def initialize_diagonal_masks(self):
        masks = [
            0x80, # h1
            0x8040, 
            0x804020, 
            0x80402010, 
            0x8040201008, 
            0x804020100804, 
            0x80402010080402,
            0x8040201008040201, 
            0x4020100804020100, 
            0x2010080402010000, 
            0x1008040201000000,
            0x804020100000000, 
            0x402010000000000,
            0x201000000000000, 
            0x100000000000000 # a8
        ]
        for s in range(64):
            for m in masks:
                if m & (1 << s):
                    self.diag_lookup[s] = m
                    break

        return masks

    def initialize_antidiagonal_masks(self):
        masks = [
            0x1, # a1
            0x102, 
            0x10204, 
            0x1020408, 
            0x102040810, 
            0x10204081020, 
            0x1020408102040,
            0x102040810204080, 
            0x204081020408000, 
            0x408102040800000, 
            0x810204080000000,
            0x1020408000000000, 
            0x2040800000000000, 
            0x4080000000000000, 
            0x8000000000000000 # h8
        ]

        for s in range(64):
            for m in masks:
                if m & (1 << s):
                    self.a_diag_lookup[s] = m
                    break

        return masks
    
    def get_diagonal_mask(self, square):
        for mask in self.initialize_diagonal_masks():
            if mask & (1 << square):
                return mask

    def get_antidiagonal_mask(self, square):
        for mask in self.initialize_antidiagonal_masks():
            if mask & (1 << square):
                return mask
            
    def precompute_orthogonal_moves(self):
        rank_moves = {}
        file_moves = {}
        for piece_square in range(8):  # 0 to 7 for each square in a rank
            for occupants in range(128):  # 2^7 configurations (excluding the piece itself)
                # Stores occupants as 8 bits
                occupants_mask = (occupants >> piece_square) << (piece_square + 1)
                occupants_mask |= occupants & ((1 << piece_square) - 1)
                occupants_mask |= (1 << piece_square)
                moves = 0  # This will be a bitboard of legal moves
                # Calculate moves to the right
                for file in range(piece_square + 1, 8):
                    moves |= (1 << file)
                    if occupants & (1 << (file - 1)):  # Adjusting the blocker position
                        break
                # Calculate moves to the left
                for file in range(piece_square - 1, -1, -1):
                    moves |= (1 << file)
                    if occupants & (1 << (file)):  # Adjusting the blocker position
                        break
                moves &= ~(1 << piece_square)
                rank_moves[(piece_square, occupants_mask)] = moves
                file_moves[(piece_square, self.rotate_270(occupants_mask))] = self.rotate_270(moves)
        return rank_moves, file_moves

    def rotate_90(self, bitboard):
        rotated = 0
        for i in range(8):
            if bitboard & (1 << i):
                #rotated |= (1 < (((i << 3) ^ 0x38) & 0x38))
                rotated |= (1 << ((7 - i) * 8))
        return rotated
    
    def rotate_270(self, bitboard):
        rotated = 0
        for i in range(8):
            if bitboard & (1 << i):
                #rotated |= (((i >> 3) | (i << 3)) & 63) ^ 7
                rotated |= (1 << i*8)
        return rotated

    def count_bits(self, bitmask):
        count = 0
        while bitmask:
            count += bitmask & 1
            bitmask >>= 1
        return count

    def precompute_diagonal_moves(self):
        diagonal_moves = {}
        antidiagonal_moves = {}

        for square in range(64):
            diagonal_mask = self.get_diagonal_mask(square)
            antidiagonal_mask = self.get_antidiagonal_mask(square)

            # Calculate the number of bits in each mask (number of squares in the diagonal)
            diagonal_length = self.count_bits(diagonal_mask)
            antidiagonal_length = self.count_bits(antidiagonal_mask)

            # Iterate over all possible blocker configurations for each diagonal and antidiagonal
            for blockers in range(1 << (diagonal_length)):
                
                real_blockers = self.map_blockers_to_actual_board(blockers, diagonal_mask)
                real_blockers |= (1 << square)
                diagonal_moves[(square, real_blockers)] = self.calc_diag_moves(square, diagonal_mask, real_blockers)
            
            for blockers in range(1 << (antidiagonal_length)):

                real_blockers = self.map_blockers_to_actual_board(blockers, antidiagonal_mask)
                real_blockers |= (1 << square)
                antidiagonal_moves[(square, real_blockers)] = self.calc_diag_moves(square, antidiagonal_mask, real_blockers)

        return diagonal_moves, antidiagonal_moves
    
    def map_blockers_to_actual_board(self, blockers, mask):
        actual_blockers = 0
        mask_index = 0

        # Iterate over each bit in the mask
        for square in range(64):
            if mask & (1 << square):  # Check if the square is part of the mask
                if blockers & (1 << mask_index):  # Check if there is a blocker in this position
                    actual_blockers |= (1 << square)  # Place the blocker on the actual board
                mask_index += 1  # Move to the next position in the blocker configuration

        return actual_blockers

    def calc_diag_moves(self, square, line_mask, blockers):
        moves = 0
        row = square // 8
        col = square % 8
        # Diagonal directions: NE, NW, SE, SW
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dr, dc in directions:
            r, c = row, col
            while True:
                r += dr
                c += dc
                if not (0 <= r < 8 and 0 <= c < 8):
                    break  # Out of board bounds
                move_sq = r * 8 + c
                if line_mask & (1 << move_sq):  # Check if the square is on the line
                    moves |= (1 << move_sq)
                    if blockers & (1 << move_sq):  # Stop if there's a blocker
                        break

        return moves

def format_to_8x8(binary_number):
    # Ensure the binary number has 64 bits, padding with zeros if necessary
    formatted_binary = format(binary_number, '064b')

    # Split the 64-bit number into 8 groups of 8 bits each and reverse each row
    rows = [formatted_binary[i:i+8][::-1] for i in range(56, -8, -8)]

    # Reverse the order of the rows and join them with a newline character for display
    return '\n'.join(rows[::-1])

# sliding_moves.rank: {(piece_file, rank_occupants): (legal_moves)}
# sliding_moves.file: {(piece_rank, file_occupants): (legal_moves)}
# sliding_moves.diagonal: {(piece_square, diagonal_occupants): (legal_moves)}
# sliding_moves.anti_diagonal: {(piece_square, antidiag_occupants): (legal_moves)}
sliding_moves = Precompute()


if __name__ == '__main__':
    p = Precompute()
    #print(p.anti_diagonal[5][1099511631904])
    #print(format_to_8x8(p.map_blockers_to_actual_board(0b111111, 0x10204081020)))
    for i in range(1 << 8):
        print(bin(p.rotate_90(i)))
    
    """
    for i in p.anti_diagonal.items():
        if i[0][0] == 5:
            #print(f"{i[0][0]} {bin(i[0][1])} {bin(i[1])}")
            print(f"{i[0][0]}-------- \n{format_to_8x8(i[0][1])}")# \n\n{format_to_8x8(i[1])}")
    
    for m in p.initialize_antidiagonal_masks():
        print(format_to_8x8(m))
        print()

    for square in range(64):
        diagonal_mask = p.get_diagonal_mask(square)
        antidiagonal_mask = p.get_antidiagonal_mask(square)
        print(square)
        print('--------')
        print(format_to_8x8(diagonal_mask))
        print()
        print(format_to_8x8(antidiagonal_mask))
        print()
        print(format_to_8x8(diagonal_mask | antidiagonal_mask))
        print()"""