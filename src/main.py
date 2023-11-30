from board import Board
from movegenerator import MoveGenerator

import moveorder, tools, gamestate, evaluate
import random, sys, subprocess
import gc, time


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
                    ng = gamestate.GameState()
                    ng.newGameUCI()
                    for move in parsed_command[3:]:
                        int_move = tools.uci_to_int(move, ng.board.bitboards)
                        ng.makemove(int_move)

            elif parsed_command[0] == "go":
                if ng.move < 5: depth = 2
                elif ng.move < 21: depth = 3
                else: depth = 4
                if parsed_command[1] == "movetime":
                    eval, best_move = ng.startSearchTimed(parsed_command[2], depth, eval_func)
                    print(f"bestmove {tools.int_to_uci(best_move)}")
                    ng.makemove(best_move)
                    eval = None
                    best_move = None
                elif parsed_command[1] == "infinite": # inifinite search
                    eval, best_move = ng.search(depth, ng.turn, eval_func)
                else:
                    eval, best_move = ng.search(depth, ng.turn, eval_func)
                    print(f"bestmove {tools.int_to_uci(best_move)}")
                    ng.makemove(best_move)
                    #eval = None
                    #best_move = None
                    #gc.collect()

            elif parsed_command[0] == "stop":
                if best_move:
                    print(f"bestmove {tools.int_to_uci(best_move)}")
                    ng.makemove(best_move)
                    #gc.collect()

            elif parsed_command[0] == "quit":
                quit()

if __name__ == "__main__":
    eval_func = evaluate.evaluate_board
    depth = 2
    UCI.coms()