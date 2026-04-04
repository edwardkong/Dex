"""Extract training data from Fishtest PGN files.

Fishtest games have Stockfish evaluations in comments: {-0.91/21 1.749s}
meaning eval=-0.91 pawns, depth=21, time=1.749s.
These are the highest-quality evaluations available.

Usage:
    python nnue/scripts/extract_fishtest.py --pgn FILE --max-positions 500000
"""

import sys
import os
import re
import gzip
import argparse
import random
import numpy as np

try:
    import chess
    import chess.pgn
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


# Fishtest comment format: {+0.91/21 1.749s} or {-0.91/21 1.749s} or {M5/21 1.0s}
# python-chess strips curly braces from comments
FISHTEST_EVAL_RE = re.compile(r'([+-]?\d+\.\d+|[+-]?M\d+)/(\d+)\s')


def parse_fishtest_comment(comment: str):
    """Extract eval from Fishtest comment. Returns (centipawns, depth) or None."""
    match = FISHTEST_EVAL_RE.search(comment)
    if not match:
        return None

    eval_str = match.group(1)
    depth = int(match.group(2))
    # Strip leading + sign
    eval_str = eval_str.lstrip('+')

    if 'M' in eval_str:
        # Mate score
        sign = -1 if eval_str.startswith('-') else 1
        return sign * 10000.0, depth
    else:
        return float(eval_str) * 100, depth  # Convert to centipawns


def main():
    parser = argparse.ArgumentParser(description="Extract Fishtest training data")
    parser.add_argument("--pgn", type=str, required=True,
                        help="Path to Fishtest PGN file (.pgn or .pgn.gz)")
    parser.add_argument("--max-positions", type=int, default=500000)
    parser.add_argument("--min-depth", type=int, default=10,
                        help="Minimum Stockfish depth to accept (default: 10)")
    parser.add_argument("--sample-rate", type=float, default=0.3,
                        help="Fraction of positions to sample (default: 0.3)")
    parser.add_argument("--output", "-o", type=str,
                        default="nnue/data/fishtest_training_data.npz")
    args = parser.parse_args()

    features_list = []
    evals_list = []
    games_processed = 0

    print(f"Extracting from {args.pgn}...")

    if args.pgn.endswith('.gz'):
        f = gzip.open(args.pgn, 'rt', encoding='utf-8', errors='replace')
    else:
        f = open(args.pgn, 'r')

    try:
        while len(features_list) < args.max_positions:
            try:
                game = chess.pgn.read_game(f)
            except Exception:
                continue
            if game is None:
                break

            games_processed += 1
            if games_processed % 1000 == 0:
                print(f"  Processed {games_processed} games, "
                      f"{len(features_list)} positions extracted")

            try:
                board = game.board()
                move_num = 0

                for node in game.mainline():
                    move_num += 1
                    board.push(node.move)

                    # Skip early moves
                    if move_num < 16:
                        continue

                    # Random sampling
                    if random.random() > args.sample_rate:
                        continue

                    comment = node.comment
                    result = parse_fishtest_comment(comment)
                    if result is None:
                        continue

                    eval_cp, depth = result

                    # Skip shallow evals and extreme values
                    if depth < args.min_depth:
                        continue
                    if abs(eval_cp) > 5000:
                        continue

                    # Convert to side-to-move perspective
                    if not board.turn:
                        eval_cp = -eval_cp

                    features = board_to_features(board)
                    features_list.append(features)
                    evals_list.append(eval_cp)

            except Exception:
                continue
    finally:
        f.close()

    features = np.array(features_list)
    evals = np.array(evals_list, dtype=np.float32)

    np.savez_compressed(args.output, features=features, evals=evals)
    print(f"\nDone: {games_processed} games, {len(features)} positions")
    print(f"Saved to {args.output}")
    print(f"  Features shape: {features.shape}")
    print(f"  Evals range: [{evals.min():.0f}, {evals.max():.0f}] centipawns")
    print(f"  Evals mean: {evals.mean():.1f}, std: {evals.std():.1f}")


if __name__ == "__main__":
    main()
