"""Extract training data from Lichess puzzle CSV using Stockfish for labeling.

Uses Stockfish at depth 8 (fast, ~50ms per position) to get centipawn
evaluations for puzzle positions. The puzzle FENs provide diverse,
interesting positions that cover tactical and positional themes.

Usage:
    python nnue/scripts/extract_puzzles.py --max-positions 500000
"""

import sys
import os
import csv
import argparse
import random
import numpy as np

try:
    import chess
    import chess.engine
except ImportError:
    print("pip install python-chess")
    sys.exit(1)


def board_to_features(board: chess.Board) -> np.ndarray:
    """Convert a python-chess Board to a 768-element feature vector."""
    features = np.zeros(768, dtype=np.float32)

    piece_map = {
        (chess.PAWN, chess.WHITE): 0, (chess.KNIGHT, chess.WHITE): 1,
        (chess.BISHOP, chess.WHITE): 2, (chess.ROOK, chess.WHITE): 3,
        (chess.QUEEN, chess.WHITE): 4, (chess.KING, chess.WHITE): 5,
        (chess.PAWN, chess.BLACK): 6, (chess.KNIGHT, chess.BLACK): 7,
        (chess.BISHOP, chess.BLACK): 8, (chess.ROOK, chess.BLACK): 9,
        (chess.QUEEN, chess.BLACK): 10, (chess.KING, chess.BLACK): 11,
    }

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            idx = piece_map[(piece.piece_type, piece.color)]
            features[idx * 64 + square] = 1.0

    # Flip for black to move
    if not board.turn:
        flipped = np.zeros(768, dtype=np.float32)
        for pt in range(6):
            for sq in range(64):
                mirror_sq = sq ^ 56
                flipped[(pt + 6) * 64 + mirror_sq] = features[pt * 64 + sq]
                flipped[pt * 64 + mirror_sq] = features[(pt + 6) * 64 + sq]
        features = flipped

    return features


def main():
    parser = argparse.ArgumentParser(description="Extract puzzle training data")
    parser.add_argument("--csv", type=str,
                        default="nnue/data/lichess_puzzles.csv",
                        help="Path to Lichess puzzle CSV")
    parser.add_argument("--max-positions", type=int, default=500000)
    parser.add_argument("--stockfish-depth", type=int, default=8,
                        help="Stockfish search depth for labeling (default: 8)")
    parser.add_argument("--output", "-o", type=str,
                        default="nnue/data/puzzle_training_data.npz")
    args = parser.parse_args()

    # Find Stockfish
    stockfish_path = "stockfish"

    print(f"Opening Stockfish at depth {args.stockfish_depth}...")
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    engine.configure({"Threads": 4, "Hash": 256})

    features_list = []
    evals_list = []

    print(f"Reading puzzles from {args.csv}...")
    with open(args.csv, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if len(features_list) >= args.max_positions:
                break

            # Sample ~10% of puzzles for diversity
            if random.random() > 0.1:
                continue

            fen = row['FEN']
            try:
                board = chess.Board(fen)

                # Quick Stockfish evaluation
                info = engine.analyse(board, chess.engine.Limit(depth=args.stockfish_depth))
                score = info['score'].white()

                if score.is_mate():
                    cp = 10000 if score.mate() > 0 else -10000
                else:
                    cp = score.score()

                if abs(cp) > 5000:
                    continue

                # Convert to side-to-move perspective
                if not board.turn:
                    cp = -cp

                features = board_to_features(board)
                features_list.append(features)
                evals_list.append(float(cp))

            except Exception as e:
                continue

            if len(features_list) % 10000 == 0 and len(features_list) > 0:
                print(f"  {len(features_list)} positions extracted "
                      f"(scanned {i+1} puzzles)")

    engine.quit()

    features = np.array(features_list)
    evals = np.array(evals_list, dtype=np.float32)

    np.savez_compressed(args.output, features=features, evals=evals)
    print(f"\nSaved {len(features)} positions to {args.output}")
    print(f"  Features shape: {features.shape}")
    print(f"  Evals range: [{evals.min():.0f}, {evals.max():.0f}] centipawns")
    print(f"  Evals mean: {evals.mean():.1f}, std: {evals.std():.1f}")


if __name__ == "__main__":
    main()
