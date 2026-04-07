import math
import os

from movegenerator import MoveGenerator
from zobristhash import ZobristHash
import eval
from eval import is_insufficient_material
from transpositiontable import TTEntry, EXACT, LOWERBOUND, UPPERBOUND

# Local Syzygy tablebase for search evaluation
_syzygy_tb = None
try:
    import chess.syzygy
    _tb_path = os.path.join(os.path.dirname(__file__), '..', 'syzygy')
    if os.path.isdir(_tb_path):
        _syzygy_tb = chess.syzygy.open_tablebase(_tb_path, load_dtz=False)
except ImportError:
    pass

MATE_SCORE = 100000
MAX_PLY = 64
ASPIRATION_WINDOW = 50
TB_WIN_SCORE = 9000  # Tablebase win, below mate but above any heuristic eval


def _probe_syzygy_wdl(board) -> int | None:
    """Probe local Syzygy WDL tables. Returns score or None.

    Only probes positions with 6 or fewer pieces.
    Returns side-to-move relative score:
      +TB_WIN_SCORE for win, 0 for draw, -TB_WIN_SCORE for loss.
    """
    if _syzygy_tb is None:
        return None

    # Count pieces
    count = 0
    occ = board.occupants[2]
    while occ:
        count += 1
        occ &= occ - 1
    if count > 6:
        return None

    # Convert to python-chess board for probing
    try:
        import chess
        b = chess.Board()
        b.clear()
        piece_map = {
            0: (chess.PAWN, chess.WHITE), 1: (chess.KNIGHT, chess.WHITE),
            2: (chess.BISHOP, chess.WHITE), 3: (chess.ROOK, chess.WHITE),
            4: (chess.QUEEN, chess.WHITE), 5: (chess.KING, chess.WHITE),
            6: (chess.PAWN, chess.BLACK), 7: (chess.KNIGHT, chess.BLACK),
            8: (chess.BISHOP, chess.BLACK), 9: (chess.ROOK, chess.BLACK),
            10: (chess.QUEEN, chess.BLACK), 11: (chess.KING, chess.BLACK),
        }
        for idx in range(12):
            bb = board.bitboards[idx]
            pt, color = piece_map[idx]
            while bb:
                sq = (bb & -bb).bit_length() - 1
                b.set_piece_at(sq, chess.Piece(pt, color))
                bb &= bb - 1
        b.turn = chess.WHITE if board.color == 0 else chess.BLACK

        wdl = _syzygy_tb.probe_wdl(b)
        if wdl > 0:
            return TB_WIN_SCORE
        elif wdl < 0:
            return -TB_WIN_SCORE
        else:
            return 0
    except Exception:
        return None


class Search:
    def __init__(self, tt, depth=None, eval_func=None,
                 position_history=None, halfmove_clock=0,
                 nnue_evaluator=None):
        self.nodes = 0
        if eval_func is None:
            self.eval_func = eval.evaluate_board
        else:
            self.eval_func = eval_func
        self.tt = tt
        self.best_moves = {}
        self.max_depth = depth
        self.killers = [[None, None] for _ in range(MAX_PLY)]
        self.history = [[[0] * 64 for _ in range(64)] for _ in range(2)]
        self.position_history = list(position_history) if position_history else []
        self.halfmove_clock = halfmove_clock
        self.nnue = nnue_evaluator
        self.accum_stack = []  # Stack of accumulators for make/unmake

    def _eval(self, board) -> int:
        """Evaluate using NNUE accumulator if available, else heuristic."""
        if self.nnue and self.accum_stack:
            return self.nnue.evaluate_from_accumulator(
                self.accum_stack[-1], board.color)
        return self.eval_func(board)

    def _make_move_with_accum(self, board, move):
        """Make a move and update the NNUE accumulator incrementally."""
        # Extract move info before make_move changes the board
        from_sq = move & 0x3F
        to_sq = (move >> 6) & 0x3F
        piece_type = (move >> 12) & 0x7
        color = (move >> 15) & 0x1
        promotion_flag = (move >> 16) & 0x1
        piece_type_color = piece_type + color * 6

        # Detect captured piece before the board changes
        captured_piece = -1
        if board.occupants[1 - color] & (1 << to_sq):
            for pt in range(6):
                if board.bitboards[pt + (1 - color) * 6] & (1 << to_sq):
                    captured_piece = pt + (1 - color) * 6
                    break
        # En passant capture
        elif (piece_type == 0 and board.en_passant_flag != -1
              and (to_sq & 7) == board.en_passant_flag
              and abs(from_sq - to_sq) in (7, 9)):
            captured_piece = 0 + (1 - color) * 6

        # Make the actual move
        undo = board.make_move(move)

        # Update accumulator if NNUE is active
        if self.nnue and self.accum_stack:
            prev_accum = self.accum_stack[-1]
            promotion_piece = -1
            if promotion_flag:
                promotion_piece = piece_type + color * 6  # piece_type has promo piece
                piece_type_color = 0 + color * 6  # was a pawn

            new_accum = self.nnue.update_accumulator(
                prev_accum, piece_type_color, from_sq, to_sq,
                captured_piece=captured_piece,
                promotion_piece=promotion_piece)
            self.accum_stack.append(new_accum)

        return undo

    def _unmake_move_with_accum(self, board, undo):
        """Unmake a move and restore the previous accumulator."""
        board.unmake_move(undo)
        if self.nnue and len(self.accum_stack) > 1:
            self.accum_stack.pop()

    def start_search(self, board):
        # Compute initial accumulator if NNUE is active
        if self.nnue:
            self.accum_stack = [self.nnue.compute_accumulator(board)]
        self.second_best = {}  # {depth: (eval, move)} for repetition avoidance
        self.iterative_deepening(board)
        return self.best_moves[self.max_depth]

    def iterative_deepening(self, board):
        depth = self.max_depth
        prev = self.best_moves.get(depth - 1)
        if prev is None or depth <= 2:
            alpha = float('-inf')
            beta = float('inf')
        else:
            # Aspiration window around previous score
            alpha = prev[0] - ASPIRATION_WINDOW
            beta = prev[0] + ASPIRATION_WINDOW

        eval_score, move = self.negamax(board, depth, 0, alpha, beta)

        # Re-search with full window if score fell outside aspiration
        if eval_score <= alpha or eval_score >= beta:
            eval_score, move = self.negamax(board, depth, 0,
                                            float('-inf'), float('inf'))

        self.best_moves[depth] = (eval_score, move)

    def negamax(self, board, depth, ply, alpha, beta, capture_flag=False,
                null_move_allowed=True):
        self.nodes += 1
        orig_alpha = alpha
        in_check = False

        # Draw detection (skip at root)
        if ply > 0:
            # 50-move rule
            if self.halfmove_clock + ply >= 100:
                return 0, None
            # Threefold repetition
            key = board.zobrist_key
            if self.position_history.count(key) >= 2:
                return 0, None
            # Insufficient material
            if is_insufficient_material(board):
                return 0, None

        # TT lookup
        tp = self.tt.lookup_key(board.zobrist_key, depth)
        if tp:
            if ply > 0:
                if tp.bound == EXACT:
                    return tp.eval, tp.best_move
                elif tp.bound == LOWERBOUND:
                    alpha = max(alpha, tp.eval)
                elif tp.bound == UPPERBOUND:
                    beta = min(beta, tp.eval)
                if alpha >= beta:
                    return tp.eval, tp.best_move

        mg = MoveGenerator(board)
        legal_moves = mg.generate_moves()
        in_check = mg.in_check

        # No legal moves: checkmate or stalemate
        if not legal_moves:
            if in_check:
                return -MATE_SCORE + ply, None
            else:
                return 0, None

        # Check extension: search one ply deeper when in check
        if in_check:
            depth += 1

        # Leaf node
        if depth == 0:
            # Probe local tablebase at leaf for positions with ≤6 pieces
            tb_score = _probe_syzygy_wdl(board)
            if tb_score is not None:
                return tb_score, None
            return self.quiescence_search(board, alpha, beta, limit=4), None

        # Probe tablebase at interior nodes too (enables finding winning trades)
        if ply > 0:
            tb_score = _probe_syzygy_wdl(board)
            if tb_score is not None:
                return tb_score, None

        # Static eval (used for NMP, futility pruning, razoring)
        static_eval = self._eval(board) if not in_check else alpha

        # Null move pruning: skip our turn and search at reduced depth
        # Don't use NMP: in check, after a capture, or at shallow depth
        if (null_move_allowed and depth >= 3 and not in_check
                and not capture_flag and ply > 0
                and static_eval >= beta):
                R = 2 + (depth > 6)
                # Flip color and update Zobrist key to match
                board.color = 1 - board.color
                board.zobrist_key ^= ZobristHash.table[64]
                null_score, _ = self.negamax(board, depth - 1 - R, ply + 1,
                                             -beta, -beta + 1,
                                             capture_flag=False,
                                             null_move_allowed=False)
                null_score = -null_score
                # Restore color and Zobrist key
                board.color = 1 - board.color
                board.zobrist_key ^= ZobristHash.table[64]

                if null_score >= beta:
                    return beta, None

        # Order moves
        tt_move = self.tt.lookup_move(board.zobrist_key)
        ordered_moves = sorted(
            legal_moves,
            key=lambda move: self.order_moves(board, move, depth, ply, tt_move),
            reverse=True
        )

        # Futility pruning: at shallow depth, skip quiet moves that can't raise alpha
        futility_pruning = False
        if depth <= 3 and not in_check and abs(alpha) < MATE_SCORE - 100:
            futility_margin = [0, 200, 500, 900][depth]
            if static_eval + futility_margin < alpha:
                futility_pruning = True

        best_eval = float('-inf')
        best_move = None
        second_eval = float('-inf')
        second_move = None
        moves_searched = 0

        for move in ordered_moves:
            capture_flag = (move >> 17) & 0x1
            promotion_flag = (move >> 16) & 0x1

            # Futility pruning: skip quiet moves at shallow depths
            if (futility_pruning and moves_searched > 0
                    and not capture_flag and not promotion_flag):
                continue

            undo = self._make_move_with_accum(board, move)
            self.position_history.append(board.zobrist_key)

            # PVS + LMR
            if moves_searched == 0:
                # First move: full window search
                eval_score, _ = self.negamax(board, depth - 1,
                                             ply + 1, -beta, -alpha, capture_flag)
                eval_score = -eval_score
            else:
                # Late move reductions for quiet moves
                reduction = 0
                if (moves_searched >= 4 and depth >= 3
                        and not capture_flag and not in_check):
                    reduction = int(math.log(moves_searched) * math.log(depth) / 2.0)
                    reduction = max(reduction, 1)
                    reduction = min(reduction, depth - 2)

                # Scout search with zero window (PVS)
                eval_score, _ = self.negamax(board, depth - 1 - reduction,
                                             ply + 1, -alpha - 1, -alpha, capture_flag)
                eval_score = -eval_score

                # Re-search with full window if scout found improvement
                if eval_score > alpha and (reduction > 0 or eval_score < beta):
                    eval_score, _ = self.negamax(board, depth - 1, ply + 1,
                                                 -beta, -alpha, capture_flag)
                    eval_score = -eval_score

            self.position_history.pop()
            self._unmake_move_with_accum(board, undo)
            moves_searched += 1

            if eval_score > best_eval:
                if ply == 0:
                    second_eval = best_eval
                    second_move = best_move
                best_eval = eval_score
                best_move = move
            elif ply == 0 and eval_score > second_eval:
                second_eval = eval_score
                second_move = move

            alpha = max(alpha, eval_score)
            if alpha >= beta:
                if not capture_flag:
                    self._store_killer(ply, move)
                    from_sq = move & 0x3F
                    to_sq = (move >> 6) & 0x3F
                    color = (move >> 15) & 0x1
                    self.history[color][from_sq][to_sq] += depth * depth
                break

        # Store in TT
        if best_eval <= orig_alpha:
            bound = UPPERBOUND
        elif best_eval >= beta:
            bound = LOWERBOUND
        else:
            bound = EXACT
        entry = TTEntry(board.zobrist_key, depth, best_eval, board.commits,
                        bound, best_move)
        self.tt.store_eval(entry)

        # Track second-best at root for repetition avoidance
        if ply == 0 and second_move is not None:
            self.second_best[depth] = (second_eval, second_move)

        return best_eval, best_move

    def quiescence_search(self, board, alpha, beta, limit=None):
        self.nodes += 1
        stand_pat = self._eval(board)

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
                all_moves = mg.generate_moves()
                if not all_moves:
                    return -MATE_SCORE
            return stand_pat

        ordered_captures = sorted(legal_captures,
            key=lambda move: self.priority_moves(board, move),
            reverse=True)

        DELTA_MARGIN = 200
        piece_vals = [101, 316, 329, 494, 903, 0]

        for move in ordered_captures:
            # Delta pruning: skip captures that can't possibly raise alpha
            promotion_flag = (move >> 16) & 0x1
            if not promotion_flag:
                to_sq = (move >> 6) & 0x3F
                color = (move >> 15) & 0x1
                # Find captured piece value
                captured_val = 0
                for pt in range(5):
                    if board.bitboards[pt + (1 - color) * 6] & (1 << to_sq):
                        captured_val = piece_vals[pt]
                        break
                if stand_pat + captured_val + DELTA_MARGIN < alpha:
                    continue

            undo = self._make_move_with_accum(board, move)
            eval_score = -self.quiescence_search(board, -beta, -alpha,
                                                  None if limit is None else limit - 1)
            self._unmake_move_with_accum(board, undo)

            if eval_score >= beta:
                return beta
            if eval_score > alpha:
                alpha = eval_score

        return alpha

    def _store_killer(self, ply, move):
        if ply >= MAX_PLY:
            return
        if self.killers[ply][0] != move:
            self.killers[ply][1] = self.killers[ply][0]
            self.killers[ply][0] = move

    def order_moves(self, board, move, depth, ply, tt_move):
        if tt_move and move == tt_move:
            return 200000

        pv_move = self.best_moves.get(depth - 1)
        if pv_move and pv_move[1] == move:
            return 190000

        to_square = (move >> 6) & 0x3F
        piece_type = (move >> 12) & 0x7
        color = (move >> 15) & 0x1
        promotion_flag = (move >> 16) & 0x1
        capture_flag = (move >> 17) & 0x1

        if promotion_flag:
            return 180000

        if capture_flag or (board.occupants[1 - color] & (1 << to_square)):
            for i in range(5):
                if board.bitboards[i + (1 - color) * 6] & (1 << to_square):
                    return 100000 + 10 * i - piece_type
            return 100000

        if ply < MAX_PLY:
            if move == self.killers[ply][0]:
                return 90000
            if move == self.killers[ply][1]:
                return 89000

        from_square = move & 0x3F
        return self.history[color][from_square][to_square]

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
                    return 10 * i - piece_type
            return 0
        return 0
