"""Extract (position, evaluation) pairs from Lichess evaluated game databases.

Downloads a Lichess monthly database (PGN with Stockfish evals in comments),
extracts positions as board feature vectors with their evaluations, and saves
as a numpy array for training.

Usage:
    python nnue/scripts/extract_data.py [--max-positions N] [--output FILE]

To download data manually:
    https://database.lichess.org/ -> download a rated games file
    Or use the lichess API for evaluated games
"""

import sys
import os
import argparse
import random
import io
import struct
import numpy as np

try:
    import chess
    import chess.pgn
except ImportError:
    print("pip install python-chess")
    sys.exit(1)


def board_to_features(board: chess.Board) -> np.ndarray:
    """Convert a python-chess Board to a 768-element feature vector.

    Uses HalfKP-like encoding:
    - 12 piece types (6 per color) × 64 squares = 768 binary features
    - Feature index = piece_type * 64 + square
    - piece_type: 0-5 = white P,N,B,R,Q,K; 6-11 = black p,n,b,r,q,k
    """
    features = np.zeros(768, dtype=np.float32)

    piece_map = {
        (chess.PAWN, chess.WHITE): 0,
        (chess.KNIGHT, chess.WHITE): 1,
        (chess.BISHOP, chess.WHITE): 2,
        (chess.ROOK, chess.WHITE): 3,
        (chess.QUEEN, chess.WHITE): 4,
        (chess.KING, chess.WHITE): 5,
        (chess.PAWN, chess.BLACK): 6,
        (chess.KNIGHT, chess.BLACK): 7,
        (chess.BISHOP, chess.BLACK): 8,
        (chess.ROOK, chess.BLACK): 9,
        (chess.QUEEN, chess.BLACK): 10,
        (chess.KING, chess.BLACK): 11,
    }

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            idx = piece_map[(piece.piece_type, piece.color)]
            features[idx * 64 + square] = 1.0

    # Flip features for black to move (network always evaluates from side-to-move perspective)
    if not board.turn:
        # Swap white and black pieces, mirror squares vertically
        flipped = np.zeros(768, dtype=np.float32)
        for pt in range(6):
            for sq in range(64):
                mirror_sq = sq ^ 56  # Flip rank
                # White piece -> black piece slot, mirrored
                flipped[(pt + 6) * 64 + mirror_sq] = features[pt * 64 + sq]
                # Black piece -> white piece slot, mirrored
                flipped[pt * 64 + mirror_sq] = features[(pt + 6) * 64 + sq]
        features = flipped

    return features


def parse_eval_from_comment(comment: str) -> float | None:
    """Extract centipawn evaluation from a Lichess PGN comment.

    Lichess format: [%eval 1.23] or [%eval #5] for mate
    """
    if '[%eval' not in comment:
        return None

    try:
        eval_str = comment.split('[%eval ')[1].split(']')[0]
        if eval_str.startswith('#'):
            # Mate score: convert to large centipawn value
            mate_in = int(eval_str[1:])
            return 10000.0 if mate_in > 0 else -10000.0
        return float(eval_str) * 100  # Convert to centipawns
    except (IndexError, ValueError):
        return None


def generate_from_pgn(pgn_path: str, max_positions: int = 1000000,
                      skip_first_n_moves: int = 8,
                      sample_rate: float = 0.3):
    """Generate (features, eval) pairs from a Lichess PGN file.

    Args:
        pgn_path: Path to PGN file (can be .pgn or .pgn.zst)
        max_positions: Maximum positions to extract
        skip_first_n_moves: Skip opening moves (book positions)
        sample_rate: Probability of sampling each position (to get diversity)
    """
    features_list = []
    evals_list = []
    games_processed = 0

    if pgn_path.endswith('.zst'):
        import zstandard as zstd
        with open(pgn_path, 'rb') as fh:
            dctx = zstd.ZstdDecompressor()
            stream_reader = dctx.stream_reader(fh)
            f = io.TextIOWrapper(stream_reader, encoding='utf-8', errors='replace')
            return _parse_pgn_stream(f, features_list, evals_list,
                                     max_positions, skip_first_n_moves,
                                     sample_rate, games_processed)

    with open(pgn_path, 'r') as f:
        while len(features_list) < max_positions:
            try:
                game = chess.pgn.read_game(f)
            except Exception:
                continue
            if game is None:
                break

            games_processed += 1
            if games_processed % 1000 == 0:
                print(f"  Processed {games_processed} games, "
                      f"{len(features_list)} positions extracted",
                      file=sys.stderr)

            try:
                board = game.board()
                move_num = 0

                for node in game.mainline():
                    move_num += 1
                    board.push(node.move)

                # Skip early moves (opening book territory)
                if move_num < skip_first_n_moves * 2:
                    continue

                # Random sampling for diversity
                if random.random() > sample_rate:
                    continue

                # Extract eval from comment
                comment = node.comment
                eval_cp = parse_eval_from_comment(comment)
                if eval_cp is None:
                    continue

                # Skip extreme evaluations (likely won/lost positions)
                if abs(eval_cp) > 5000:
                    continue

                # Convert eval to side-to-move perspective
                if not board.turn:
                    eval_cp = -eval_cp

                features = board_to_features(board)
                features_list.append(features)
                evals_list.append(eval_cp)
            except Exception:
                continue

    print(f"  Done: {games_processed} games, {len(features_list)} positions",
          file=sys.stderr)

    return np.array(features_list), np.array(evals_list, dtype=np.float32)


def generate_from_self_play(num_positions: int = 100000):
    """Generate training data from self-play using the current engine.

    Fallback when no Lichess database is available.
    Uses python-chess with a simple random+greedy policy to generate
    positions, then evaluates them with Stockfish if available,
    or uses material count as a rough label.
    """
    print("Generating positions from random games...", file=sys.stderr)
    features_list = []
    evals_list = []

    while len(features_list) < num_positions:
        board = chess.Board()
        moves_made = 0

        while not board.is_game_over() and moves_made < 200:
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                break

            # Semi-random move selection (prefer captures)
            captures = [m for m in legal_moves if board.is_capture(m)]
            if captures and random.random() < 0.3:
                move = random.choice(captures)
            else:
                move = random.choice(legal_moves)

            board.push(move)
            moves_made += 1

            # Sample positions after move 8, 30% of the time
            if moves_made > 16 and random.random() < 0.3:
                if abs(material_eval(board)) < 5000:
                    features = board_to_features(board)
                    eval_cp = material_eval(board)
                    # Convert to side-to-move perspective
                    if not board.turn:
                        eval_cp = -eval_cp
                    features_list.append(features)
                    evals_list.append(eval_cp)

        if len(features_list) % 10000 == 0 and len(features_list) > 0:
            print(f"  {len(features_list)} positions generated",
                  file=sys.stderr)

    return np.array(features_list[:num_positions]), \
           np.array(evals_list[:num_positions], dtype=np.float32)


def material_eval(board: chess.Board) -> float:
    """Simple material-based evaluation for training data labels."""
    values = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
              chess.ROOK: 500, chess.QUEEN: 900}
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type != chess.KING:
            val = values.get(piece.piece_type, 0)
            score += val if piece.color == chess.WHITE else -val
    return float(score)


def main():
    parser = argparse.ArgumentParser(description="Extract NNUE training data")
    parser.add_argument("--pgn", type=str, help="Path to Lichess PGN file with evaluations")
    parser.add_argument("--max-positions", type=int, default=500000,
                        help="Maximum positions to extract (default: 500000)")
    parser.add_argument("--self-play", action="store_true",
                        help="Generate data from self-play instead of PGN")
    parser.add_argument("--output", "-o", type=str,
                        default="nnue/data/training_data.npz",
                        help="Output file path")
    args = parser.parse_args()

    if args.pgn:
        print(f"Extracting from {args.pgn}...")
        features, evals = generate_from_pgn(args.pgn, args.max_positions)
    elif args.self_play:
        print(f"Generating {args.max_positions} positions from self-play...")
        features, evals = generate_from_self_play(args.max_positions)
    else:
        print("Error: specify --pgn FILE or --self-play")
        sys.exit(1)

    np.savez_compressed(args.output, features=features, evals=evals)
    print(f"Saved {len(features)} positions to {args.output}")
    print(f"  Features shape: {features.shape}")
    print(f"  Evals range: [{evals.min():.0f}, {evals.max():.0f}] centipawns")
    print(f"  Evals mean: {evals.mean():.1f}, std: {evals.std():.1f}")


if __name__ == "__main__":
    main()
