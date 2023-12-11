from gamestate import GameState
import tools
import evaluate
import gc

class UCI:
    def coms(self):
        eval_func = evaluate.evaluate_board
        depth = 4
        #gc.disable()
        new_game = GameState()
        new_game.newGameUCI()
        while True:
            command = input()
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
                #gc.collect()

            elif parsed_command[0] == "stop":
                if best_move:
                    print(f"bestmove {tools.int_to_uci(best_move)}")
                    new_game.board.make_move(best_move)
                    #gc.collect()

            elif parsed_command[0] == "quit":
                quit()

if __name__ == "__main__":
    new_uci = UCI()
    new_uci.coms()