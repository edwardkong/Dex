import position, makemove, movegen, tools, game
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
                    ng = game.GameState()
                    for move in parsed_command[3:]:
                        int_move = makemove.uci_to_int(move, ng.board.bitboards)
                        ng.makemove(int_move)
            elif parsed_command[0] == "go":
                if parsed_command[1] == "movetime":
                    int_move, best_move = ng.startSearchTimed(parsed_command[2])
                    print(f"bestmove {best_move}")
                    ng.makemove(int_move)
                    int_move = None
                    best_move = None
                elif parsed_command[1] == "infinite": # inifinite search
                    int_move, best_move = ng.search()
                else:
                    int_move, best_move = ng.search()
                    print(f"bestmove {best_move}")
                    ng.makemove(int_move)
                    int_move = None
                    best_move = None
                    gc.collect()
            elif parsed_command[0] == "stop":
                if int_move and best_move:
                    print(f"bestmove {best_move}")
                    ng.makemove(int_move)
                    gc.collect()
            elif parsed_command[0] == "quit":
                quit()

if __name__ == "__main__":
    UCI.coms()