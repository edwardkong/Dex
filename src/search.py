from movegenerator import MoveGenerator
import moveorder
import evaluate
from transpositiontable import TTEntry


class Search:
    def __init__(self, tt, eval_func=None):
        if eval_func is None:
            self.eval_func = evaluate.evaluate_board
        self.tt = tt

    def minimax_ab(self, board, depth, color, alpha=None, beta=None):
        if alpha is None:
            alpha = float('-inf')
        if beta is None:
            beta = float('inf')

        tp = self.tt.lookup_key(board.zobrist_key, depth)
        if tp:
            return tp.eval, None

        mg = MoveGenerator(board, color)
        legal_moves = mg.generate_moves()

        ordered_moves = sorted(
            legal_moves, 
            key=lambda move: moveorder.capture_priority(board, move, color), 
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
        
        if depth == 0:
            return self.eval_func(board), None

        if color == 0: # maximizing player
            max_eval = float('-inf')
            best_move = None
            for move in ordered_moves:
                pos = board.sim_move(move)
                eval, _ = self.minimax_ab(pos, depth - 1, 1, alpha, beta)

                entry = TTEntry(pos.zobrist_key, depth, eval, pos.commits)
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

                entry = TTEntry(pos.zobrist_key, depth, eval, pos.commits)
                self.tt.store_eval(entry)

                if eval < min_eval:
                    min_eval = eval
                    best_move = move

                beta = min(beta, eval)
                if beta < alpha:
                    break
            return min_eval, best_move