from gamestate import GameState
from board import Board
import tools
import evaluate
import sys
import time
import precompute


class UCI:
    def coms(self):
        new_game = GameState()
        new_game.newGameUCI()
        best_move = None

        while True:
            try:
                command = input()
            except EOFError:
                break
            parsed_command = command.split(" ")

            if parsed_command[0] == "uci":
                print("id name Dex 0.3")
                print("id author Edward Kong")
                print("uciok")

            elif parsed_command[0] == "isready":
                print("readyok")

            elif parsed_command[0] == "ucinewgame":
                new_game = GameState()
                new_game.newGameUCI()
                new_game.tt.clear()

            elif parsed_command[0] == "position":
                new_game = GameState()
                new_game.newGameUCI()

                if parsed_command[1] == "startpos":
                    if len(parsed_command) > 3 and parsed_command[2] == "moves":
                        for move_str in parsed_command[3:]:
                            given_move = tools.uci_to_int(
                                move_str, new_game.board.bitboards)
                            new_game.make_move(given_move)

                elif parsed_command[1] == "fen":
                    # Find where moves start (if any)
                    fen_parts = []
                    moves_idx = None
                    for i in range(2, len(parsed_command)):
                        if parsed_command[i] == "moves":
                            moves_idx = i
                            break
                        fen_parts.append(parsed_command[i])

                    fen_string = " ".join(fen_parts)
                    new_game = GameState(board=Board.from_fen(fen_string))
                    new_game.newGameUCI()

                    if moves_idx is not None:
                        for move_str in parsed_command[moves_idx + 1:]:
                            given_move = tools.uci_to_int(
                                move_str, new_game.board.bitboards)
                            new_game.make_move(given_move)

            elif parsed_command[0] == "go":
                # Parse time control arguments
                time_limit = None
                params = {}
                i = 1
                while i < len(parsed_command):
                    key = parsed_command[i]
                    if key in ("wtime", "btime", "winc", "binc",
                               "movestogo", "depth", "movetime", "nodes"):
                        if i + 1 < len(parsed_command):
                            params[key] = int(parsed_command[i + 1])
                            i += 2
                        else:
                            i += 1
                    elif key == "infinite":
                        params["infinite"] = True
                        i += 1
                    else:
                        i += 1

                # Calculate time for this move
                if "movetime" in params:
                    time_limit = params["movetime"] / 1000.0
                elif "wtime" in params or "btime" in params:
                    if new_game.board.color == 0:
                        remaining = params.get("wtime", 60000)
                        increment = params.get("winc", 0)
                    else:
                        remaining = params.get("btime", 60000)
                        increment = params.get("binc", 0)
                    time_limit = (remaining / 30.0 + increment) / 1000.0

                eval_score, best_move = new_game.search(time_limit=time_limit)

                if "infinite" not in params:
                    print(f"bestmove {tools.int_to_uci(best_move)}")
                    sys.stdout.flush()

            elif parsed_command[0] == "stop":
                if best_move is not None:
                    print(f"bestmove {tools.int_to_uci(best_move)}")
                    sys.stdout.flush()

            elif parsed_command[0] == "quit":
                sys.exit(0)


if __name__ == "__main__":
    new_uci = UCI()
    new_uci.coms()
