"""Extract training data from bingbangboom/stockfish-evaluation-SAN dataset.

Each line is JSON: {"fen": "...", "depth": N, "evaluation": "X.XX", "best_move": "..."}

Usage:
    python nnue/scripts/extract_stockfish_eval.py --input FILE --max-positions 1000000
"""

import sys
import os
import json
import argparse
import random
import numpy as np

try:
    import chess
except ImportError:
    print("pip install python-chess")
    sys.exit(1)


def board_to_features(fen: str) -> np.ndarray:
    """Convert FEN to 768-element feature vector."""
    board = chess.Board(fen)
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

    return features, board.turn


def parse_eval(eval_str: str) -> float | None:
    """Parse evaluation string to centipawns."""
    if eval_str.startswith('M') or eval_str.startswith('+M'):
        return 10000.0
    elif eval_str.startswith('-M'):
        return -10000.0
    elif eval_str.startswith('#'):
        mate_val = int(eval_str[1:])
        return 10000.0 if mate_val > 0 else -10000.0
    else:
        try:
            return float(eval_str) * 100  # Convert pawns to centipawns
        except ValueError:
            return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", type=str, required=True)
    parser.add_argument("--max-positions", type=int, default=1000000)
    parser.add_argument("--min-depth", type=int, default=10)
    parser.add_argument("--output", "-o", type=str,
                        default="nnue/data/stockfish_training_data.npz")
    args = parser.parse_args()

    features_list = []
    evals_list = []
    skipped = 0

    print(f"Processing {args.input}...")

    with open(args.input, 'r') as f:
        for line_num, line in enumerate(f):
            if len(features_list) >= args.max_positions:
                break

            if line_num % 100000 == 0 and line_num > 0:
                print(f"  {line_num} lines, {len(features_list)} positions extracted")

            try:
                data = json.loads(line.strip())
            except json.JSONDecodeError:
                skipped += 1
                continue

            # Filter by depth
            depth = data.get('depth', 0)
            if depth < args.min_depth:
                skipped += 1
                continue

            # Parse evaluation
            eval_cp = parse_eval(str(data.get('evaluation', '')))
            if eval_cp is None:
                skipped += 1
                continue

            # Skip extreme evals
            if abs(eval_cp) > 5000:
                skipped += 1
                continue

            # Convert FEN to features
            fen = data['fen']
            try:
                features, is_white = board_to_features(fen)
            except Exception:
                skipped += 1
                continue

            # Evaluation is from white's perspective in the dataset
            # Convert to side-to-move perspective
            if not is_white:
                eval_cp = -eval_cp

            features_list.append(features)
            evals_list.append(eval_cp)

    features = np.array(features_list)
    evals = np.array(evals_list, dtype=np.float32)

    np.savez_compressed(args.output, features=features, evals=evals)
    print(f"\nSaved {len(features)} positions to {args.output}")
    print(f"  Skipped: {skipped}")
    print(f"  Features shape: {features.shape}")
    print(f"  Evals range: [{evals.min():.0f}, {evals.max():.0f}] centipawns")
    print(f"  Evals mean: {evals.mean():.1f}, std: {evals.std():.1f}")


if __name__ == "__main__":
    main()
