from gamestate import GameState
import tools
import evaluate
import precompute

import cProfile
import pstats
import sys
#import tracemalloc

import platform
imp = platform.python_implementation()

pre_commands = [
    'position startpos',
    'go',
    'position startpos moves d2d4 e7e5',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6 e2g4 c8b8',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6 e2g4 c8b8 g4f5 g6f4',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6 e2g4 c8b8 g4f5 g6f4 d3g3 f6e5',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6 e2g4 c8b8 g4f5 g6f4 d3g3 f6e5 f5h7 f4h7',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6 e2g4 c8b8 g4f5 g6f4 d3g3 f6e5 f5h7 f4h7 f2f4 h7f4',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6 e2g4 c8b8 g4f5 g6f4 d3g3 f6e5 f5h7 f4h7 f2f4 h7f4 g3f3 d6d5',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6 e2g4 c8b8 g4f5 g6f4 d3g3 f6e5 f5h7 f4h7 f2f4 h7f4 g3f3 d6d5 e4d5 f4d5',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6 e2g4 c8b8 g4f5 g6f4 d3g3 f6e5 f5h7 f4h7 f2f4 h7f4 g3f3 d6d5 e4d5 f4d5 f3e2 d5e3',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6 e2g4 c8b8 g4f5 g6f4 d3g3 f6e5 f5h7 f4h7 f2f4 h7f4 g3f3 d6d5 e4d5 f4d5 f3e2 d5e3 f1f8 d8f8',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6 e2g4 c8b8 g4f5 g6f4 d3g3 f6e5 f5h7 f4h7 f2f4 h7f4 g3f3 d6d5 e4d5 f4d5 f3e2 d5e3 f1f8 d8f8 e2d3 e3d1',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6 e2g4 c8b8 g4f5 g6f4 d3g3 f6e5 f5h7 f4h7 f2f4 h7f4 g3f3 d6d5 e4d5 f4d5 f3e2 d5e3 f1f8 d8f8 e2d3 e3d1 c3d1 c5d6',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6 e2g4 c8b8 g4f5 g6f4 d3g3 f6e5 f5h7 f4h7 f2f4 h7f4 g3f3 d6d5 e4d5 f4d5 f3e2 d5e3 f1f8 d8f8 e2d3 e3d1 c3d1 c5d6 d3d2 e5e4',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6 e2g4 c8b8 g4f5 g6f4 d3g3 f6e5 f5h7 f4h7 f2f4 h7f4 g3f3 d6d5 e4d5 f4d5 f3e2 d5e3 f1f8 d8f8 e2d3 e3d1 c3d1 c5d6 d3d2 e5e4 h1g1 e4g4',
    'go',
    'position startpos moves d2d4 e7e5 d4e5 b8c6 g1f3 f8b4 c1d2 b4c5 e2e4 d8e7 d2c3 f7f6 d1d5 f6e5 c3e5 d7d6 f1b5 c8d7 e5c3 g8f6 c3f6 e7f6 b1c3 e8c8 b5d3 c6e5 d3e2 c7c6 d5d2 d7h3 e1g1 h8f8 a1d1 h3g2 g1g2 e5f3 d2d3 f3h4 g2h1 h4g6 e2g4 c8b8 g4f5 g6f4 d3g3 f6e5 f5h7 f4h7 f2f4 h7f4 g3f3 d6d5 e4d5 f4d5 f3e2 d5e3 f1f8 d8f8 e2d3 e3d1 c3d1 c5d6 d3d2 e5e4 h1g1 e4g4 d2g2 g4d1',
    'go'
    ]
pre_iter = iter(pre_commands)

class UCI:
    #@profile
    def coms(self):
        eval_func = evaluate.evaluate_board
        depth = 4
        new_game = GameState()
        new_game.newGameUCI()

        turn = 0
        while True:
            """
            try:
                command = next(pre_iter)
            except StopIteration:
                return
            """
            try:
                command = next(pre_iter)
            except StopIteration:
                break
            if command != 'go':
                turn += 1

            try:
                loop_profiler = cProfile.Profile()
                loop_profiler.enable()

                #original code
                parsed_command = command.split(" ")

                if parsed_command[0] == "uci":
                    print("id name Dex 0.0")
                    print("id author Edward Kong")
                    print("uciok")

                elif parsed_command[0] == "isready":
                    print("readyok")

                elif parsed_command[0] == "ucinewgame":
                    new_game = GameState()
                    new_game.newGameUCI()

                elif parsed_command[0] == "position":
                    if parsed_command[1] == "startpos":                    
                        if len(parsed_command) > 2:
                            if parsed_command[2] == "moves":
                                if new_game.move_history == parsed_command[3:-1]:
                                    new_game.make_move(
                                        tools.uci_to_int(parsed_command[-1],
                                        new_game.board.bitboards))
                                else:
                                    for move in parsed_command[3:]:
                                        given_move = tools.uci_to_int(
                                            move, new_game.board.bitboards)
                                        new_game.make_move(given_move)

                elif parsed_command[0] == "go":
                    if len(parsed_command) > 1:
                        if parsed_command[1] == "movetime":
                            eval, best_move = new_game.search()
                            print(f"bestmove {tools.int_to_uci(best_move)}")
                            new_game.make_move(best_move)
                        elif parsed_command[1] == "infinite":
                            eval, best_move = new_game.search()
                    else:
                        eval, best_move = new_game.search()
                        print(f"bestmove {tools.int_to_uci(best_move)}")
                        new_game.make_move(best_move)

                elif parsed_command[0] == "stop":
                    if best_move:
                        print(f"bestmove {tools.int_to_uci(best_move)}")
                        new_game.board.make_move(best_move)

                elif parsed_command[0] == "quit":
                    sys.exit(0)
                #/original code

                loop_profiler.disable()
                if command == 'go':
                    if 'CPython' == imp:
                        output_file = f'./benchmark/CPython_{turn}'
                    else:
                        output_file = f'./benchmark/PyPy_{turn}'
                    
                    loop_profiler.dump_stats(f"{output_file}_{turn}.prof")
                    with open(f"{output_file}.txt", "w") as f:
                        stats = pstats.Stats(loop_profiler, stream=f).sort_stats('cumulative')
                        stats.print_stats()

            except KeyboardInterrupt:
                break

if 'CPython' == imp:
    output_file = f'./benchmark/CPython_stats'
else:
    output_file = f'./benchmark/PyPy_stats'

"""
if 'CPython' == imp:
    output_file = f'./benchmark/CPython_{int(len(pre_commands)/2)}'
else:
    output_file = f'./benchmark/PyPy_{int(len(pre_commands)/2)}'
"""
def run_profiler():
    """Run with profiler for debugging."""
    profiler = cProfile.Profile()
    #tracemalloc.start()
    try:
        profiler.enable()
        new_uci.coms()
    except KeyboardInterrupt:
        print("Keyboard Interrupt caught, ending profiling...")
    finally:
        profiler.disable()
        profiler.dump_stats(f"{output_file}.prof")
        # Print profiling results to a human-readable file
        with open(f"{output_file}.txt", "w") as f:
            stats = pstats.Stats(profiler, stream=f).sort_stats('cumulative')
            stats.print_stats()
    
        """current, peak = tracemalloc.get_traced_memory()
        print(f"Current memory usage: {current / 10**6} MB; Peak: {peak / 10**6} MB")
        tracemalloc.stop()"""


if __name__ == "__main__":
    new_uci = UCI()
    #run_profiler()
    new_uci.coms()
