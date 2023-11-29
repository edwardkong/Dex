import cProfile, time
import evaluate, search, game, position, movegen, makemove, tools

# Test from a specific board state - generate bitboards then play
# # Checkmate
# # Stalemate
# # Castle
# # En Passant

# Test specific modules - isolate module
# # Search
# # Evaluate
# # Move generation
# # Board update
# # Board calculations

def test_checkmate(bitboard, color):
    """ Given a bitboard position, verify that the engine will be able to identify forced checkmate lines and either play them or avoid them. """
    depth = 2
    evaluate_func = evaluate.evaluate_board
    test_game = game.GameState()

    ## Set up a checkmate position, copy bitboards here

    #eval, best_move = test_game.searchMM(depth, 0, evaluate_func)
    print(search.minimax_alpha_beta(bitboard, depth, float('-inf'), float('inf'), color, evaluate_func))

    #legal_moves = movegen.generate_moves(bitboard, color)
    #for move in legal_moves:
    #    evals = evaluate.evaluate_board(position.simulate_move(bitboard, move))
    #    print(f"{tools.parse_move(move)}  {evals}")

    #print(f"best: {tools.parse_move(best_move)}  {eval}")
#  position startpos moves e2e4 f7f6 d2d4 g7g5
# 
# [402712320, 66, 36, 129, 8, 16, 44789980546990080, 4755801206503243776, 2594073385365405696, 9295429630892703744, 576460752303423488, 1152921504606846976, 402712575, 18419476460218613760, 18419476460621326335, 15]
# Legal moves .. [1032, 1544, 1097, 1609, 1162, 1674, 1357, 1869, 1422, 1934, 1487, 1999, 2267, 2332, 5249, 4801, 5121, 5574, 5446, 4870, 8898, 9474, 10050, 10626, 8965, 9413, 9861, 10309, 10757, 17155, 17731, 18307, 18883, 17091, 17603, 21252, 21188]
# print(tools.encode_move(3, 39, 4, 0)) # 18883

# Mate in 1 is found on bitboard, is found in legal moves (inside search), but is not evaluated/processed in search

test_checkmate([402712320, 66, 36, 129, 8, 16, 44789980546990080, 4755801206503243776, 2594073385365405696, 9295429630892703744, 576460752303423488, 1152921504606846976, 402712575, 18419476460218613760, 18419476460621326335, 15], 0)