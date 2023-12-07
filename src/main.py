from gamestate import GameState
import tools
import evaluate
import gc

class UCI:
    def __init__(self, request=None) -> None:
            self.eval_func = evaluate.evaluate_board
            self.depth = 4
            gc.disable()
            self.get_input(request)

    def coms(self):
        eval_func = evaluate.evaluate_board
        depth = 4
        gc.disable()
        while True:
            self.get_input(eval_func)

    def get_input(self, eval_func):
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
            if new_game.move > 20:
                    depth = evaluate.update_depth(new_game)

            if parsed_command[1] == "movetime":
                eval, best_move = new_game.startSearchTimed(parsed_command[2], depth, eval_func)
                print(f"bestmove {tools.int_to_uci(best_move)}")
                new_game.make_move(best_move)
                eval = None
                best_move = None

            elif parsed_command[1] == "infinite":
                eval, best_move = new_game.search(depth, new_game.turn, eval_func)

            else:
                eval, best_move = new_game.search(depth, new_game.turn, eval_func)
                print(f"bestmove {tools.int_to_uci(best_move)}")
                new_game.make_move(best_move)

            gc.collect()

        elif parsed_command[0] == "stop":
            if best_move:
                print(f"bestmove {tools.int_to_uci(best_move)}")
                new_game.board.make_move(best_move)
                gc.collect()

        elif parsed_command[0] == "quit":
            quit()

if __name__ == "__main__":
    #new_uci = UCI()
    #new_uci.coms()
    new_lambda = LambdaUCI()
    new_lambda.lambda_game()