from movegenerator import MoveGenerator
import evaluate
from transpositiontable import TTEntry
import tools

class Search:
    def __init__(self, tt, depth=None, eval_func=None):
        self.order = 0 
        if eval_func is None:
            self.eval_func = evaluate.evaluate_board
        self.tt = tt
        self.best_moves = {} # index: depth - 1 (eval, move)
        self.max_depth = depth

    def start_search(self, board):
        self.iterative_deepening(board)
        return self.best_moves[self.max_depth]

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

    def minimax_ab(self, board, depth, color, alpha, beta, capture_flag=False):
        tp = self.tt.lookup_key(board.zobrist_key, depth)
        if tp:
            return tp.eval, None
        
        mg = MoveGenerator(board)
        legal_moves = mg.generate_moves()

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
            if capture_flag:
                return self.quiescence_search(board, alpha, beta, limit=4), None
            else:
                return self.eval_func(board), None

        ordered_moves = sorted(
            legal_moves, 
            key=lambda move: self.order_moves(board, move, depth), 
            reverse=True
            )

        if color == 0: # maximizing player
            max_eval = float('-inf')
            best_move = None
            for move in ordered_moves:
                capture_flag = (move >> 17) & 0x1
                
                pos = board.sim_move(move)
                eval, _ = self.minimax_ab(pos, depth - 1, 1, alpha, beta, capture_flag)
                f.write("maximizing\n")
                if depth == 4:
                    print(f"depth: {depth} - move: {tools.int_to_uci(move)} - eval: {eval}\n")
                f.write(f"depth: {depth} - move: {tools.int_to_uci(move)} - eval: {eval}\n")


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
                capture_flag = (move >> 17) & 0x1
                pos = board.sim_move(move)
                eval, _ = self.minimax_ab(pos, depth - 1, 0, alpha, beta, capture_flag)
                f.write("minimizing\n")
                if depth == 4:
                    print(f"depth: {depth} - move: {tools.int_to_uci(move)} - eval: {eval}\n")
                f.write(f"depth: {depth} - move: {tools.int_to_uci(move)} - eval: {eval}\n")


                entry = TTEntry(pos.zobrist_key, depth - 1, eval, pos.commits)
                self.tt.store_eval(entry)

                if eval < min_eval:
                    min_eval = eval
                    best_move = move

                beta = min(beta, eval)
                if beta < alpha:
                    break
            return min_eval, best_move

    def quiescence_search(self, board, alpha, beta, limit=None):
        stand_pat = self.eval_func(board)
        if board.color == 0:
            if stand_pat >= beta:
                return beta
            if alpha < stand_pat:
                alpha = stand_pat
        else:
            if stand_pat <= alpha:
                return alpha
            if beta > stand_pat:
                beta = stand_pat

        mg = MoveGenerator(board)
        legal_captures = mg.generate_forcing_moves()

        if not legal_captures:
            if mg.in_check:
                if board.color == 1:
                    return float('100000000')
                else:
                    return float('-100000000')
            else:
                moves = mg.generate_moves()
                if not moves:
                    return 0.0
                else:
                    return stand_pat

        if (limit is not None and limit <= 0):
            return stand_pat

        ordered_captures = sorted(mg.generate_forcing_moves(), 
            key=lambda move: self.priority_moves(board, move), 
            reverse=True)

        if board.color == 0:
            max_eval = float('-inf')
            for move in ordered_captures:
                pos = board.sim_move(move)
                eval = self.quiescence_search(pos, alpha, beta, None if not limit else limit - 1)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in ordered_captures:
                pos = board.sim_move(move)
                eval = self.quiescence_search(pos, alpha, beta, None if not limit else limit - 1)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

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
                    return 10 * i + (piece_type * -1)
            else:
                # En passant
                return 0
        else:
            return 0
        """
        NEGAMAX IMPLEMENTATION
    def quiescence_search_nega(self, board, alpha, beta, ply=0, limit=None):
        tp = self.tt.lookup_key(board.zobrist_key, limit)
        if tp:
            ##f.write(f"q transposition {tp.eval}\n")
            return tp.eval
        ##f.write("----\n")
        #f.write(f'ply: {str(iter)}\n')
        stand_pat = self.eval_func(board)  # Static evaluation of the current position
        #f.write(f"stand_pat: {stand_pat}\n")
        ##f.write('\n')
        ##f.write(f"limit: {limit}\n")
        if stand_pat >= beta:
            ##f.write(f"beta cutoff {beta}\n")
            return beta
        if alpha < stand_pat:
            ##f.write(f"alpha pass {alpha}\n")
            alpha = stand_pat
        if limit is not None and limit <= 0:
            return stand_pat
        
        mg = MoveGenerator(board)
        legal_moves = sorted(mg.generate_forcing_moves(), 
            key=lambda move: self.priority_moves(board, move), 
            reverse=True)
        
        ##f.write(f'moves: ')
        #if not legal_moves: #f.write('N/A')
        
        #for move in legal_moves:
        #    #f.write(f"{tools.int_to_uci(move)} ")
        ##f.write("\n\n")
        for move in legal_moves:
            ##f.write("----\n")
            #f.write(f"\nsimulating: {tools.int_to_uci(move)}\n")
            pos = board.sim_move(move)
            eval = -self.quiescence_search(pos, -beta, -alpha, ply+1, None if limit is None else limit - 1)

            #entry = TTEntry(pos.zobrist_key, limit, eval, pos.commits)
            #self.tt.store_eval(entry)

            if eval >= beta:
                return beta
            if eval > alpha:
                alpha = eval

        return alpha

    def negamax(self, board, depth, color, alpha, beta):
        self.order += 1
        #f.write(str(self.order) + ': ' + str(depth)+ ' ')
        tp = self.tt.lookup_key(board.zobrist_key, depth)
        if tp:
            return tp.eval, None

        mg = MoveGenerator(board)
        legal_moves = mg.generate_moves()

        if not legal_moves:
            if mg.in_check:
                if color == 1:
                    return float('100000000'), None
                else:
                    return float('-100000000'), None
            else:
                return 0.0, None

        if depth == 0:
            if color == 0:
                return self.quiescence_search(board, alpha, beta, limit=8), None
                return self.eval_func(board), None
            else:
                return -self.quiescence_search(board, alpha, beta, limit=8), None
                return -self.eval_func(board), None


        ordered_moves = sorted(
            legal_moves, 
            key=lambda move: self.order_moves(board, move, depth), 
            reverse=True
            )
        
        max_eval = float('-inf')
        for move in ordered_moves:
            #f.write(tools.int_to_uci(move) + '\n')
            pos = board.sim_move(move)
            eval = -self.negamax(pos, depth - 1, 1 - color, -beta, -alpha)[0]

            #f.write(f"color: {color} depth: {depth} move: {tools.int_to_uci(move)} eval: {eval} max_eval: {max_eval} alpha: {alpha} beta: {beta}\n")

            entry = TTEntry(pos.zobrist_key, depth - 1, eval, pos.commits)
            self.tt.store_eval(entry)

            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta < alpha:
                break
        return max_eval, best_move
"""