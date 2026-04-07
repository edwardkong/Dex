from gamestate import GameState
from board import Board
from book import OpeningBook
from tablebase import probe_tablebase
import tools
import eval
import sys
import time
import precompute


class UCI:
    def coms(self):
        new_game = GameState()
        new_game.newGameUCI()
        best_move = None
        opening_book = OpeningBook()
        # Default to NNUE eval (heuristic available via setoption)
        from eval.nnue.v1 import NNUEEvaluator
        nnue_evaluator = NNUEEvaluator()
        use_nnue = True
        new_game.nnue_evaluator = nnue_evaluator

        while True:
            try:
                command = input()
            except EOFError:
                break
            parsed_command = command.split(" ")

            if parsed_command[0] == "uci":
                print("id name Dex 0.3")
                print("id author Edward Kong")
                print("option name EvalType type combo default nnue var heuristic var nnue")
                print("uciok")

            elif parsed_command[0] == "isready":
                print("readyok")

            elif parsed_command[0] == "setoption":
                # Parse: setoption name EvalType value nnue
                if "name" in parsed_command and "value" in parsed_command:
                    name_idx = parsed_command.index("name") + 1
                    value_idx = parsed_command.index("value") + 1
                    if name_idx < len(parsed_command) and value_idx < len(parsed_command):
                        opt_name = parsed_command[name_idx]
                        opt_value = parsed_command[value_idx]
                        if opt_name == "EvalType":
                            if opt_value == "nnue":
                                if nnue_evaluator is None:
                                    from eval.nnue.v1 import NNUEEvaluator
                                    nnue_evaluator = NNUEEvaluator(None)  # Default path
                                    print("info string NNUE loaded", file=sys.stderr)
                                use_nnue = True
                                new_game.nnue_evaluator = nnue_evaluator
                                print("info string Eval: NNUE")
                            else:
                                use_nnue = False
                                new_game.nnue_evaluator = None
                                print("info string Eval: heuristic")

            elif parsed_command[0] == "ucinewgame":
                new_game = GameState()
                new_game.newGameUCI()
                new_game.tt.clear()
                if use_nnue:
                    new_game.nnue_evaluator = nnue_evaluator

            elif parsed_command[0] == "position":
                new_game = GameState()
                new_game.newGameUCI()
                if use_nnue:
                    new_game.nnue_evaluator = nnue_evaluator
                from_startpos = False

                if parsed_command[1] == "startpos":
                    from_startpos = True
                    if len(parsed_command) > 3 and parsed_command[2] == "moves":
                        for move_str in parsed_command[3:]:
                            given_move = tools.uci_to_int(
                                move_str, new_game.board.bitboards)
                            new_game.make_move(given_move)

                elif parsed_command[1] == "fen":
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
                    if use_nnue:
                        new_game.nnue_evaluator = nnue_evaluator

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
                    # Reserve 500ms for latency/overhead
                    safe_remaining = max(remaining - 500, 100)
                    # Use less time when clock is low
                    if safe_remaining < 10000:  # Under 10 seconds
                        time_limit = (safe_remaining / 40.0 + increment * 0.5) / 1000.0
                    elif safe_remaining < 30000:  # Under 30 seconds
                        time_limit = (safe_remaining / 30.0 + increment * 0.6) / 1000.0
                    else:
                        time_limit = (safe_remaining / 20.0 + increment * 0.75) / 1000.0

                if "infinite" not in params:
                    # Try endgame tablebase first (perfect play)
                    tb_result = probe_tablebase(new_game.board)
                    if tb_result:
                        tb_move, tb_eval = tb_result
                        print(f"info string tablebase move {tb_move} eval {tb_eval}")
                        print(f"bestmove {tb_move}")
                        sys.stdout.flush()
                        move_num = len(new_game.move_history) // 2 + 1
                        print(f"[dex] source=tablebase move={tb_move} eval={tb_eval} "
                              f"ply={len(new_game.move_history)}", file=sys.stderr)
                        continue

                    # Try opening book (only from startpos)
                    book_move = opening_book.probe(new_game.move_history) if from_startpos else None
                    if book_move:
                        move_num = len(new_game.move_history) // 2 + 1
                        print(f"info string book move {book_move}")
                        print(f"bestmove {book_move}")
                        sys.stdout.flush()
                        print(f"[dex] source=book move={book_move} "
                              f"ply={len(new_game.move_history)} "
                              f"history={' '.join(new_game.move_history[-4:]) if new_game.move_history else 'start'}",
                              file=sys.stderr)
                        continue

                # Engine search
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
