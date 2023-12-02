from movegenerator import MoveGenerator
import evaluate, tools, moveorder, movegenerator
"""
class Searcher(game_state, evaluate_func=None):
    def __init__(self, depth, color, evaluate_func):
        if evaluate_func:
            self.evaluate_func = evaluate_func
        else:
            self.evaluate_func = evaluate.evaluate_board

        self.depth = depth
        self.color = game_state.turn
        self.move_history = game_state.move_history
        self.game_state = game_state
        
        self.board = game_state.board
        self.alpha = float('-inf')
        self.beta = float('inf')

        return self.minimax_alpha_beta(self.board, self.depth, self.alpha, self. beta, self.color, self.evaluate_func)

    def minimax_alpha_beta(self, board, depth, alpha, beta, color, evaluate_func):
        move_generator = MoveGenerator(board, color)

        legal_moves = move_generator.generate_moves()

        ordered_moves = sorted(legal_moves, key=lambda move: moveorder.capture_priority(board, move, color), reverse=True)

        if not legal_moves:
            if move_generator.in_check:
                if color:
                    return float('100000000'), None
                else:
                    return float('-100000000'), None
            else:
                return 0.0, None

        if depth == 0:
            return evaluate_func(board), None

        if color == 0: # maximizing player
            max_eval = float('-inf')
            best_move = None
            for move in ordered_moves:
                eval_score, _ = self.minimax_alpha_beta(board.simulate_move(move), depth - 1, alpha, beta, 1, evaluate_func)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else: # minimizing player
            min_eval = float('inf')
            best_move = None
            for move in ordered_moves:              
                eval_score, _ = self.minimax_alpha_beta(board.simulate_move(move), depth - 1, alpha, beta, 0, evaluate_func)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move
"""
def minimax_alpha_beta(board, depth, alpha, beta, color, evaluate_func):
    mg = MoveGenerator(board, color)

    legal_moves = mg.generate_moves()

    ordered_moves = sorted(legal_moves, key=lambda move: moveorder.capture_priority(board, move, color), reverse=True)

    if not legal_moves:
        if mg.in_check:
            if color == 1:
                return float('100000000'), None
            else:
                return float('-100000000'), None
        else:
            return 0.0, None
    
    
    if depth == 0:
        return evaluate_func(board), None

    if color == 0: # maximizing player
        max_eval = float('-inf')
        best_move = None
        for move in ordered_moves:
            
            """if depth == 1:
                if tools.int_to_uci(move) == "c4g8":
                    print(f"\t\t\t {depth} {color}")
                    print(f"\t\t\t{tools.int_to_uci(move)}")
                    print("\t\t\t|_______\n")
                    
            elif depth == 2:
                if tools.int_to_uci(move):
                    print(f"\t\t{depth} {color}")
                    print(f"\t\t{tools.int_to_uci(move)}")
                    print("\t\t|_______\n")
            elif depth == 3: 
                if tools.int_to_uci(move):
                    print(f"\t{depth} {color}")
                    print(f"\t{tools.int_to_uci(move)}")
                    print("\t|_______\n")
            elif depth == 4: 
                if tools.int_to_uci(move):
                    print(f"{depth} {color}")
                    print(f"{tools.int_to_uci(move)}")
                    print("|_______\n")"""
            
                    
            
            eval_score, _ = minimax_alpha_beta(board.simulate_move(move), depth - 1, alpha, beta, 1, evaluate_func)
            #print(depth, tools.int_to_uci(move), eval_score, max_eval)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta < alpha:
                break
        
        return max_eval, best_move
    else: # minimizing player
        min_eval = float('inf')
        best_move = None
        for move in ordered_moves:
            
            """if depth == 1:
                if tools.int_to_uci(move):
                    print(f"\t\t\t {depth} {color}")
                    print(f"\t\t\t{tools.int_to_uci(move)}")
                    print("\t\t\t|_______\n")
                    
            elif depth == 2:
                if tools.int_to_uci(move) == "f7g6":
                    print(f"\t\t{depth} {color}")
                    print(f"\t\t{tools.int_to_uci(move)}")
                    print("\t\t|_______\n")
            elif depth == 3: 
                if tools.int_to_uci(move):
                    print(f"\t{depth} {color}")
                    print(f"\t{tools.int_to_uci(move)}")
                    print("\t|_______\n")
            elif depth == 4: 
                if tools.int_to_uci(move):
                    print(f"{depth} {color}")
                    print(f"{tools.int_to_uci(move)}")
                    print("|_______\n")"""
                    
                    
            eval_score, _ = minimax_alpha_beta(board.simulate_move(move), depth - 1, alpha, beta, 0, evaluate_func)
            #print(depth, tools.int_to_uci(move), eval_score, min_eval)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta < alpha:
                break
        return min_eval, best_move