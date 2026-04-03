from movegenerator import MoveGenerator
import evaluate
from transpositiontable import TTEntry, EXACT, LOWERBOUND, UPPERBOUND

MATE_SCORE = 100000


class Search:
    def __init__(self, tt, depth=None, eval_func=None):
        self.nodes = 0
        if eval_func is None:
            self.eval_func = evaluate.evaluate_board
        else:
            self.eval_func = eval_func
        self.tt = tt
        self.best_moves = {}
        self.max_depth = depth

    def start_search(self, board):
        self.iterative_deepening(board)
        return self.best_moves[self.max_depth]

    def iterative_deepening(self, board):
        for depth in range(1, self.max_depth + 1):
            alpha = float('-inf')
            beta = float('inf')
            eval_score, move = self.negamax(board, depth, alpha, beta)
            self.best_moves[depth] = (eval_score, move)

    def negamax(self, board, depth, alpha, beta, capture_flag=False):
        self.nodes += 1
        orig_alpha = alpha

        # TT lookup
        tp = self.tt.lookup_key(board.zobrist_key, depth)
        if tp:
            if tp.bound == EXACT:
                return tp.eval, None
            elif tp.bound == LOWERBOUND:
                alpha = max(alpha, tp.eval)
            elif tp.bound == UPPERBOUND:
                beta = min(beta, tp.eval)
            if alpha >= beta:
                return tp.eval, None

        mg = MoveGenerator(board)
        legal_moves = mg.generate_moves()

        # No legal moves: checkmate or stalemate
        if not legal_moves:
            if mg.in_check:
                return -MATE_SCORE - depth, None  # Prefer shorter mates
            else:
                return 0, None

        # Leaf node
        if depth == 0:
            if capture_flag:
                return self.quiescence_search(board, alpha, beta, limit=4), None
            else:
                return self.eval_func(board), None

        ordered_moves = sorted(
            legal_moves,
            key=lambda move: self.order_moves(board, move, depth),
            reverse=True
        )

        best_eval = float('-inf')
        best_move = None
        for move in ordered_moves:
            capture_flag = (move >> 17) & 0x1

            undo = board.make_move(move)
            eval_score, _ = self.negamax(board, depth - 1, -beta, -alpha, capture_flag)
            eval_score = -eval_score
            board.unmake_move(undo)

            if eval_score > best_eval:
                best_eval = eval_score
                best_move = move

            alpha = max(alpha, eval_score)
            if alpha >= beta:
                break

        # Store in TT with bound type
        if best_eval <= orig_alpha:
            bound = UPPERBOUND
        elif best_eval >= beta:
            bound = LOWERBOUND
        else:
            bound = EXACT
        entry = TTEntry(board.zobrist_key, depth, best_eval, board.commits, bound)
        self.tt.store_eval(entry)

        return best_eval, best_move

    def quiescence_search(self, board, alpha, beta, limit=None):
        self.nodes += 1
        stand_pat = self.eval_func(board)

        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        if limit is not None and limit <= 0:
            return stand_pat

        mg = MoveGenerator(board)
        legal_captures = mg.generate_forcing_moves()

        if not legal_captures:
            if mg.in_check:
                # Generate all moves to check for checkmate vs stalemate
                all_moves = mg.generate_moves()
                if not all_moves:
                    return -MATE_SCORE
            return stand_pat

        ordered_captures = sorted(legal_captures,
            key=lambda move: self.priority_moves(board, move),
            reverse=True)

        for move in ordered_captures:
            undo = board.make_move(move)
            eval_score = -self.quiescence_search(board, -beta, -alpha,
                                                  None if limit is None else limit - 1)
            board.unmake_move(undo)

            if eval_score >= beta:
                return beta
            if eval_score > alpha:
                alpha = eval_score

        return alpha

    def order_moves(self, board, move, depth):
        # PV move from previous iteration
        pv_move = self.best_moves.get(depth - 1)
        if pv_move and pv_move[1] == move:
            return float('inf')
        return self.priority_moves(board, move)

    def priority_moves(self, board, move):
        to_square = (move >> 6) & 0x3F
        piece_type = (move >> 12) & 0x7
        color = (move >> 15) & 0x1
        promotion_flag = (move >> 16) & 0x1

        if promotion_flag:
            return 100

        if board.occupants[1 - color] & (1 << to_square):
            for i in range(5):
                if board.bitboards[i + (1 - color) * 6] & (1 << to_square):
                    return 10 * i + (piece_type * -1)
            return 0  # En passant
        return 0
