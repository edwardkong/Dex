"""Strength benchmark for Dex chess engine.

Runs the engine on tactical puzzle positions and checks if it finds
the correct move. Reports solve rate as a proxy for playing strength.

Uses a curated set of tactical positions defined as move sequences
from startpos (since FEN parsing is not yet available).

Usage: python benchmark/strength.py [--depth N] [--output FILE]
"""

import sys
import os
import json
import time
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from board import Board
from search import Search
from transpositiontable import TranspositionTable
import tools

# Tactical test positions defined as (moves_from_startpos, expected_best_move, description).
# These test common tactical motifs the engine should find at depth 4-5.
TACTICAL_POSITIONS = [
    {
        "name": "Scholar's mate threat",
        "moves": ["e2e4", "e7e5", "f1c4", "b8c6", "d1h5"],
        "best": "g7g6",
        "description": "Must block Qxf7#",
    },
    {
        "name": "Fork: knight fork on f7",
        "moves": [
            "e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6",
            "f3g5",
        ],
        "best": "d7d5",
        "description": "Must counter Nxf7 threat with d5",
    },
    {
        "name": "Capture hanging piece",
        "moves": [
            "e2e4", "e7e5", "g1f3", "d7d6", "d2d4", "c8g4",
            "d4e5",
        ],
        "best": "g4f3",
        "description": "Take the undefended knight",
    },
    {
        "name": "Recapture correctly",
        "moves": [
            "d2d4", "d7d5", "c2c4", "d5c4",
        ],
        "best": "e2e3",
        "accept": ["e2e3", "e2e4", "g1f3"],
        "description": "Develop and regain pawn",
    },
    {
        "name": "Defend attacked piece",
        "moves": [
            "e2e4", "e7e5", "g1f3", "b8c6", "f1b5",
        ],
        "best": "a7a6",
        "accept": ["a7a6", "g8f6", "d7d6", "f7f5"],
        "description": "Respond to Ruy Lopez",
    },
    {
        "name": "Don't hang the queen",
        "moves": [
            "e2e4", "e7e5", "d1h5", "b8c6",
        ],
        "best": "h5f3",
        "accept": ["h5e2", "h5f3", "h5g4", "h5h4", "h5h3", "h5e5", "h5g5"],
        "description": "Queen must not go to f7 (Nc6 defends) or stay attacked",
    },
    {
        "name": "Castle to safety",
        "moves": [
            "e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5",
        ],
        "best": "e1g1",
        "accept": ["e1g1", "d2d3", "c2c3"],
        "description": "Castling is a strong option here",
    },
    {
        "name": "Win material: pin",
        "moves": [
            "d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6",
            "c1g5",
        ],
        "best": "f8e7",
        "accept": ["f8e7", "f8b4", "h7h6", "d5c4"],
        "description": "Break the pin or develop",
    },
    {
        "name": "Pawn push advantage",
        "moves": [
            "e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4",
            "f3d4", "g8f6", "b1c3", "a7a6",
        ],
        "best": "f1e2",
        "accept": ["f1e2", "f2f3", "c1e3", "f1d3"],
        "description": "Develop in the Najdorf",
    },
    {
        "name": "Trade to simplify when ahead",
        "moves": [
            "e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6",
            "b5c6", "d7c6", "e1g1", "c8g4",
        ],
        "best": "h2h3",
        "accept": ["h2h3", "d2d3"],
        "description": "Kick the bishop, maintain structure",
    },
    {
        "name": "Opening trap avoidance",
        "moves": [
            "e2e4", "e7e5", "g1f3", "g8f6", "f3e5",
        ],
        "best": "d7d6",
        "accept": ["d7d6", "f8d6"],
        "description": "Kick the knight, don't play Nxe4 (falls into trap)",
    },
    {
        "name": "Central control",
        "moves": [
            "e2e4", "c7c6",
        ],
        "best": "d2d4",
        "accept": ["d2d4", "g1f3", "b1c3", "d2d3"],
        "description": "Seize the center vs Caro-Kann",
    },
]


def setup_board(moves_uci: list[str]) -> Board:
    """Create a board by playing UCI moves from startpos."""
    board = Board()
    for move_str in moves_uci:
        move = tools.uci_to_int(move_str, board.bitboards)
        if move is None:
            raise ValueError(f"Invalid move: {move_str}")
        board.make_move(move)
    return board


def test_position(board: Board, depth: int, expected: str, accepted: list[str] | None = None) -> dict:
    """Test if the engine finds the expected move."""
    tt = TranspositionTable()
    searcher = Search(tt, depth)

    start = time.perf_counter()
    eval_score, best_move = searcher.start_search(board)
    elapsed = time.perf_counter() - start

    engine_move = tools.int_to_uci(best_move) if best_move else "none"
    valid_moves = accepted if accepted else [expected]
    solved = engine_move in valid_moves

    return {
        "engine_move": engine_move,
        "expected": expected,
        "accepted": valid_moves,
        "solved": solved,
        "eval": eval_score,
        "nodes": searcher.nodes,
        "time_s": round(elapsed, 4),
    }


def run_strength_test(depth: int = 4) -> dict:
    """Run the full strength test suite."""
    results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "depth": depth,
            "python": sys.version.split()[0],
            "engine": "Dex",
            "num_positions": len(TACTICAL_POSITIONS),
        },
        "positions": [],
        "totals": {},
    }

    solved = 0
    total = len(TACTICAL_POSITIONS)
    total_nodes = 0
    total_time = 0.0

    for pos in TACTICAL_POSITIONS:
        board = setup_board(pos["moves"])
        metrics = test_position(
            board, depth, pos["best"], pos.get("accept")
        )

        status = "PASS" if metrics["solved"] else "FAIL"
        if metrics["solved"]:
            solved += 1

        results["positions"].append({
            "name": pos["name"],
            "description": pos["description"],
            **metrics,
        })

        total_nodes += metrics["nodes"]
        total_time += metrics["time_s"]

        print(f"  [{status}] {pos['name']:35s}  "
              f"engine={metrics['engine_move']:6s}  "
              f"expected={metrics['expected']:6s}  "
              f"{metrics['time_s']:>6.2f}s")

    results["totals"] = {
        "solved": solved,
        "total": total,
        "solve_rate": round(solved / total * 100, 1),
        "total_nodes": total_nodes,
        "total_time_s": round(total_time, 4),
    }

    print(f"\n  Result: {solved}/{total} solved ({results['totals']['solve_rate']}%)")

    return results


def main():
    parser = argparse.ArgumentParser(description="Dex engine strength benchmark")
    parser.add_argument("--depth", type=int, default=4, help="Search depth (default: 4)")
    parser.add_argument("--output", "-o", type=str, help="Output JSON file path")
    args = parser.parse_args()

    print(f"Dex Strength Test — depth {args.depth}\n{'=' * 60}")
    results = run_strength_test(args.depth)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
