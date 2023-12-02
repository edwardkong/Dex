from board import Board
from movegenerator import MoveGenerator
from gamestate import GameState

import moveorder, tools, gamestate, evaluate
import random, sys, subprocess
import gc, time
"""
Main creates a gamestate
gamestate creates a board
gamestate creates a searcher
searcher creates a movegenerator
searcher calls evaluate (should be created)

"""


class UCI:
    def coms():
        gc.disable()
        while(True):
            command = input()
            parsed_command = command.split(" ")

            if parsed_command[0] == "uci":
                print("id name Dex 0.0")
                print("id author Edward Kong")
                print("uciok")

            elif parsed_command[0] == "isready":
                print("readyok")

            elif parsed_command[0] == "position":
                if parsed_command[1] == "startpos":
                    new_game = GameState()
                    new_game.newGameUCI()
                    if len(parsed_command) > 2:
                        if parsed_command[2] == "moves":
                            for move in parsed_command[3:]:
                                given_move = tools.uci_to_int(move, new_game.board.bitboards)
                                new_game.make_move(given_move)

            elif parsed_command[0] == "go":
                if parsed_command[1] == "movetime":
                    eval, best_move = new_game.startSearchTimed(parsed_command[2], depth, eval_func)
                    print(f"bestmove {tools.int_to_uci(best_move)}")
                    new_game.make_move(best_move)
                    eval = None
                    best_move = None
                elif parsed_command[1] == "infinite": # inifinite search
                    eval, best_move = new_game.search(depth, new_game.turn, eval_func)
                else:
                    eval, best_move = new_game.search(depth, new_game.turn, eval_func)
                    print(f"bestmove {tools.int_to_uci(best_move)}")
                    new_game.make_move(best_move)
                    #eval = None
                    #best_move = None
                    #gc.collect()

            elif parsed_command[0] == "stop":
                if best_move:
                    print(f"bestmove {tools.int_to_uci(best_move)}")
                    new_game.board.make_move(best_move)
                    #gc.collect()

            elif parsed_command[0] == "quit":
                quit()

if __name__ == "__main__":
    eval_func = evaluate.evaluate_board
    depth = 1
    UCI.coms()