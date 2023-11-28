import evaluate, tools, position, game, movegen, makemove

def minimax(bitboards, depth, color, evaluate_func):
    
    legal_moves = movegen.generate_moves(bitboards, color)
    
    if not legal_moves:
        if not color:
            return float('-inf'), None
        else:
            return float('inf'), None

    if depth == 0:
        return evaluate_func(bitboards), None

    if not color: # maximizing player
        max_eval = float('-inf')
        best_move = None
        for move in legal_moves:
            child_position = position.simulate_move(bitboards, move)
            eval_score, _ = minimax(child_position, depth - 1, 1, evaluate_func)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
        #print(max_eval, makemove.int_to_uci(best_move))
        return max_eval, best_move
    else: # minimizing player
        min_eval = float('inf')
        best_move = None
        for move in legal_moves:
            child_position = position.simulate_move(bitboards, move)
            eval_score, _ = minimax(child_position, depth - 1, 0, evaluate_func)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
        #print(min_eval, makemove.int_to_uci(best_move))
        return min_eval, best_move

def minimax_alpha_beta(bitboards, depth, alpha, beta, color, evaluate_func):

    legal_moves = movegen.generate_moves(bitboards, color)


    #for m in legal_moves: print(makemove.int_to_uci(m))
    #print(legal_moves)
    #quit()

    if not legal_moves:
        if color == 1:
            return float('-inf'), None
        else:
            return float('inf'), None
    
    # Move this in front
    if depth == 0:
        return evaluate_func(bitboards), None
    

    if color == 0: # maximizing player
        max_eval = float('-inf')
        best_move = None
        for move in legal_moves:
            child_position = position.simulate_move(bitboards, move)
            eval_score, _ = minimax_alpha_beta(child_position, depth - 1, alpha, beta, 1, evaluate_func)
            #print(f"depth {depth} inside max")
            #print(eval_score, makemove.int_to_uci(move) if move else "none")
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        #print(makemove.int_to_uci(move), max_eval, makemove.int_to_uci(best_move))
        return max_eval, best_move
    else: # minimizing player
        min_eval = float('inf')
        best_move = None
        for move in legal_moves:
            child_position = position.simulate_move(bitboards, move)
            eval_score, _ = minimax_alpha_beta(child_position, depth - 1, alpha, beta, 0, evaluate_func)
            #print(f"depth {depth} inside min")
            #print(eval_score, makemove.int_to_uci(move) if move else "none")
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        #print(makemove.int_to_uci(move), min_eval, makemove.int_to_uci(best_move))
        return min_eval, best_move