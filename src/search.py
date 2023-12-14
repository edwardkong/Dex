from movegenerator import MoveGenerator
import moveorder
import evaluate
from transpositiontable import TTEntry

class Search:
    def __init__(self, tt, depth=None, eval_func=None):
        if eval_func is None:
            self.eval_func = evaluate.evaluate_board
        self.tt = tt
        self.best_moves = {} # index: depth - 1 (eval, move)
        self.max_depth = depth

    def start_search(self, board):
        self.iterative_deepening(board)
        return self.best_moves[self.max_depth]

    def minimax_ab(self, board, depth, color, alpha, beta):
        tp = self.tt.lookup_key(board.zobrist_key, depth)
        if tp:
            return tp.eval, None
        
        mg = MoveGenerator(board, color)
        legal_moves = mg.generate_moves()

        ordered_moves = sorted(
            legal_moves, 
            key=lambda move: self.order_moves(board, move, depth), 
            reverse=True
            )

        if not legal_moves:
            if mg.in_check:
                if color == 1:
                    return float('100000000'), None
                else:
                    return float('-100000000'), None
            else:
                return 0.0, None
        # Terminal position needs to be checked before depth == 0
        if depth == 0:
            return self.eval_func(board), None

        if color == 0: # maximizing player
            max_eval = float('-inf')
            best_move = None
            for move in ordered_moves:
                pos = board.sim_move(move)
                eval, _ = self.minimax_ab(pos, depth - 1, 1, alpha, beta)

                entry = TTEntry(pos.zobrist_key, depth - 1, eval, pos.commits)
                self.tt.store_eval(entry)

                if eval > max_eval:
                    max_eval = eval
                    best_move = move

                alpha = max(alpha, eval)
                if beta < alpha:
                    break
            
            return max_eval, best_move
        
        else: # minimizing player
            min_eval = float('inf')
            best_move = None
            for move in ordered_moves:
                pos = board.sim_move(move)
                eval, _ = self.minimax_ab(pos, depth - 1, 0, alpha, beta)

                entry = TTEntry(pos.zobrist_key, depth - 1, eval, pos.commits)
                self.tt.store_eval(entry)

                if eval < min_eval:
                    min_eval = eval
                    best_move = move

                beta = min(beta, eval)
                if beta < alpha:
                    break
            return min_eval, best_move
        
    def iterative_deepening(self, board, alpha=None, beta=None):
        max_depth = self.max_depth
        color = board.color
        if alpha is None:
            alpha = float('-inf')
        if beta is None:
            beta = float('inf')

        for depth in range(1, max_depth + 1):
            eval, move = self.minimax_ab(board, depth, color, alpha, beta)
            self.best_moves[depth] = (eval, move)

            entry = TTEntry(board.zobrist_key, depth, eval, board.commits)
            self.tt.store_eval(entry)

    def order_moves(self, board, move, depth):
        # Get PV
        pv_move = self.best_moves.get(depth - 1)
        if pv_move and pv_move[1] == move:
            return float('inf')
        # Order priority moves (promotions, captures)
        return self.priority_moves(board, move)

    def priority_moves(self, board, move):
        from_square = move & 0x3F  # Source square
        to_square = (move >> 6) & 0x3F  # Destination square
        piece_type = (move >> 12) & 0x7  # Piece type (0-5)
        color = (move >> 15) & 0x1  # Color (0 for white, 1 for black)
        promotion_flag = (move >> 16) & 0x1 # 1 if promotion

        if promotion_flag:
            return 100

        if board.occupants[1 - color] & (1 << to_square):
            for i in range(5):
                if board.bitboards[i + (1 - color) * 6] & (1 << to_square):
                    return 10 * i + piece_type
            else:
                # En passant
                return 0
        else:
            return 0