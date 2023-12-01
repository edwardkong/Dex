import evaluate, tools, moveorder, gamestate, movegenerator

def minimax_alpha_beta(board, depth, alpha, beta, color, evaluate_func):
    mg = movegenerator.MoveGenerator(board, color)

    legal_moves = mg.generate_moves()

    ordered_moves = sorted(legal_moves, key=lambda move: moveorder.capture_priority(board, move, color))

    for m in legal_moves: 
        print("========")
        print(tools.int_to_uci(m))
        print(depth)
        print(color)
        if tools.int_to_uci(m) = "e8d7":
            print(mg.check_jump_mask)
            print(mg.check_ray_mask)
    print(legal_moves)
    #quit()

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
            eval_score, _ = minimax_alpha_beta(board.simulate_move(move), depth - 1, alpha, beta, 1, evaluate_func)
            #print(f"depth {depth} inside max")
            #print(depth, eval_score, tools.int_to_uci(move) if move else "none")
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
        for move in ordered_moves:
            eval_score, _ = minimax_alpha_beta(board.simulate_move(move), depth - 1, alpha, beta, 0, evaluate_func)
            #print(f"depth {depth} inside min")
            #print(depth, eval_score, tools.int_to_uci(move) if move else "none")
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        #print(makemove.int_to_uci(move), min_eval, makemove.int_to_uci(best_move))
        return min_eval, best_move