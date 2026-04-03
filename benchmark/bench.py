"""Performance benchmark for Dex chess engine.

Runs search on a fixed set of positions at a fixed depth,
measuring nodes searched, wall-clock time, and NPS.
Outputs results as JSON for automated comparison.

Usage: python benchmark/bench.py [--depth N] [--output FILE]
"""

import sys
import os
import json
import time
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from board import Board
from gamestate import GameState
from search import Search
from transpositiontable import TranspositionTable
import tools
import evaluate

# Fixed benchmark positions as move sequences from startpos.
# Mix of opening, middlegame, and endgame-like states.
POSITIONS = [
    {
        "name": "Starting position",
        "moves": [],
    },
    {
        "name": "After 1. e4",
        "moves": ["e2e4"],
    },
    {
        "name": "Italian Game",
        "moves": ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4"],
    },
    {
        "name": "Queen's Gambit",
        "moves": ["d2d4", "d7d5", "c2c4"],
    },
    {
        "name": "Sicilian Defense",
        "moves": ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4"],
    },
    {
        "name": "Ruy Lopez middlegame",
        "moves": [
            "e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6",
            "b5a4", "g8f6", "e1g1", "f8e7", "f1e1", "b7b5", "a4b3",
        ],
    },
    {
        "name": "Complex middlegame",
        "moves": [
            "d2d4", "g8f6", "c2c4", "e7e6", "b1c3", "f8b4",
            "e2e3", "e8g8", "f1d3", "d7d5", "g1f3", "c7c5",
        ],
    },
    {
        "name": "Open position",
        "moves": [
            "e2e4", "e7e5", "d2d4", "e5d4", "d1d4", "b8c6",
            "d4e3", "g8f6", "b1c3",
        ],
    },
    {
        "name": "Closed position",
        "moves": [
            "d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6",
            "c1g5", "f8e7", "e2e3", "e8g8", "g1f3", "b8d7",
        ],
    },
    {
        "name": "Advanced middlegame",
        "moves": [
            "e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4",
            "f3d4", "g8f6", "b1c3", "a7a6", "f1e2", "e7e5",
            "d4b3", "f8e7", "e1g1", "e8g8",
        ],
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


def bench_position(board: Board, depth: int) -> dict:
    """Run search on a position and return metrics."""
    tt = TranspositionTable()
    searcher = Search(tt, depth)

    start = time.perf_counter()
    eval_score, best_move = searcher.start_search(board)
    elapsed = time.perf_counter() - start

    nps = int(searcher.nodes / elapsed) if elapsed > 0 else 0
    best_move_uci = tools.int_to_uci(best_move) if best_move else "none"

    return {
        "nodes": searcher.nodes,
        "time_s": round(elapsed, 4),
        "nps": nps,
        "eval": eval_score,
        "best_move": best_move_uci,
        "depth": depth,
    }


def run_benchmark(depth: int = 4) -> dict:
    """Run the full benchmark suite."""
    results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "depth": depth,
            "python": sys.version.split()[0],
            "engine": "Dex",
        },
        "positions": [],
        "totals": {},
    }

    total_nodes = 0
    total_time = 0.0

    for pos in POSITIONS:
        board = setup_board(pos["moves"])
        metrics = bench_position(board, depth)

        results["positions"].append({
            "name": pos["name"],
            **metrics,
        })

        total_nodes += metrics["nodes"]
        total_time += metrics["time_s"]

        print(f"  {pos['name']:30s}  {metrics['nodes']:>10,} nodes  "
              f"{metrics['time_s']:>7.2f}s  {metrics['nps']:>8,} nps  "
              f"eval={metrics['eval']:>8}  move={metrics['best_move']}")

    total_nps = int(total_nodes / total_time) if total_time > 0 else 0
    results["totals"] = {
        "total_nodes": total_nodes,
        "total_time_s": round(total_time, 4),
        "avg_nps": total_nps,
    }

    print(f"\n  {'TOTAL':30s}  {total_nodes:>10,} nodes  "
          f"{total_time:>7.2f}s  {total_nps:>8,} nps")

    return results


def main():
    parser = argparse.ArgumentParser(description="Dex engine performance benchmark")
    parser.add_argument("--depth", type=int, default=4, help="Search depth (default: 4)")
    parser.add_argument("--output", "-o", type=str, help="Output JSON file path")
    args = parser.parse_args()

    print(f"Dex Benchmark — depth {args.depth}\n{'=' * 60}")
    results = run_benchmark(args.depth)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")
    else:
        print(f"\n{json.dumps(results, indent=2)}")


if __name__ == "__main__":
    main()
