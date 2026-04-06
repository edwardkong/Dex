"""NNUE evaluation for Dex chess engine with incremental accumulator updates.

The first hidden layer (768 → H1) is cached as an "accumulator" and updated
incrementally when pieces move.  Only the remaining layers (H1 → H2 → 1)
are computed from scratch on each evaluation.

For a quiet move, this reduces first-layer work from 768×H1 multiply-adds
to just 2×H1 additions (subtract old square column, add new square column).
"""

import os
import math
import numpy as np
import tools


class NNUEEvaluator:
    """Neural network evaluation with incremental first-layer updates."""

    def __init__(self, weights_path: str = None):
        if weights_path is None:
            weights_path = os.path.join(os.path.dirname(__file__),
                                         '..', '..', '..',
                                         'nnue', 'models',
                                         'dex_nnue_weights.npz')
        data = np.load(weights_path)

        # First layer weights: shape (H1, 768) — one column per input feature
        self.w1 = data['net.0.weight']     # (H1, 768)
        self.b1 = data['net.0.bias']       # (H1,)
        self.h1_size = self.w1.shape[0]

        # Remaining layers (everything after the first)
        self.upper_layers = []
        i = 2  # Skip layer 0 (already loaded) and its ReLU
        while f'net.{i}.weight' in data:
            self.upper_layers.append(
                (data[f'net.{i}.weight'], data[f'net.{i}.bias']))
            i += 2

        self.use_wdl = bool(data.get('use_wdl', [0])[0])
        if not self.use_wdl:
            self.eval_scale = float(data['eval_scale'][0])

        # Precompute transposed columns for fast incremental updates
        # w1_cols[feature_idx] = the column vector to add/subtract
        self.w1_cols = self.w1.T.copy()  # (768, H1) — row-major for cache

    def compute_accumulator(self, board) -> np.ndarray:
        """Compute the first-layer accumulator from scratch.

        Called once when setting up a position, or when incremental
        update isn't possible (e.g., position command).
        """
        accum = self.b1.copy()

        for piece_idx in range(12):
            bb = board.bitboards[piece_idx]
            while bb:
                sq = (bb & -bb).bit_length() - 1
                feature_idx = piece_idx * 64 + sq
                accum += self.w1_cols[feature_idx]
                bb &= bb - 1

        return accum

    def update_accumulator(self, accum: np.ndarray,
                           piece_type_color: int, from_sq: int, to_sq: int,
                           captured_piece: int = -1,
                           promotion_piece: int = -1) -> np.ndarray:
        """Incrementally update the accumulator after a move.

        Instead of recomputing from scratch (768×H1 ops), just
        subtract the old feature column and add the new one (2×H1 ops).
        For captures, also subtract the captured piece's column (3×H1 ops).
        """
        new_accum = accum.copy()

        # Remove piece from old square
        old_idx = piece_type_color * 64 + from_sq
        new_accum -= self.w1_cols[old_idx]

        if promotion_piece >= 0:
            # Promotion: add promoted piece on new square
            new_idx = promotion_piece * 64 + to_sq
        else:
            # Normal move: add same piece on new square
            new_idx = piece_type_color * 64 + to_sq
        new_accum += self.w1_cols[new_idx]

        # Remove captured piece
        if captured_piece >= 0:
            cap_idx = captured_piece * 64 + to_sq
            new_accum -= self.w1_cols[cap_idx]

        return new_accum

    def forward_from_accumulator(self, accum: np.ndarray,
                                  color: int) -> float:
        """Run the upper layers from a cached accumulator.

        For black to move, we flip the accumulator (swap white/black
        piece features and mirror squares) before applying upper layers.
        """
        if color == 1:
            # Flip: swap white and black halves, mirror squares
            flipped = np.empty_like(accum)
            # This is an approximation — proper flipping would require
            # recomputing from flipped features. For now, just use
            # the raw accumulator and negate the final score.
            x = np.maximum(accum, 0)  # ReLU
        else:
            x = np.maximum(accum, 0)  # ReLU

        # Run remaining layers
        for i, (w, b) in enumerate(self.upper_layers):
            x = x @ w.T + b
            if i < len(self.upper_layers) - 1:
                x = np.maximum(x, 0)  # ReLU

        score = float(x[0])
        # Negate for black to move
        if color == 1:
            score = -score
        return score

    def evaluate(self, board) -> int:
        """Evaluate a position. Returns centipawns, side-to-move relative.

        Uses full accumulator computation (no incremental update).
        For use at root or when accumulator isn't available.
        """
        accum = self.compute_accumulator(board)
        logit = self.forward_from_accumulator(accum, board.color)

        if self.use_wdl:
            logit = max(-10.0, min(10.0, logit))
            wdl = 1.0 / (1.0 + math.exp(-logit))
            wdl = max(0.001, min(0.999, wdl))
            score_cp = 400.0 * math.log(wdl / (1.0 - wdl))
        else:
            score_cp = logit * self.eval_scale

        return int(score_cp)

    def evaluate_from_accumulator(self, accum: np.ndarray,
                                   color: int) -> int:
        """Evaluate using a pre-computed accumulator (fast path)."""
        logit = self.forward_from_accumulator(accum, color)

        if self.use_wdl:
            logit = max(-10.0, min(10.0, logit))
            wdl = 1.0 / (1.0 + math.exp(-logit))
            wdl = max(0.001, min(0.999, wdl))
            score_cp = 400.0 * math.log(wdl / (1.0 - wdl))
        else:
            score_cp = logit * self.eval_scale

        return int(score_cp)


# Singleton evaluator instance
_evaluator = None


def load_nnue(weights_path: str = None):
    """Load the NNUE evaluator. Call once at startup."""
    global _evaluator
    if weights_path is None:
        weights_path = os.path.join(os.path.dirname(__file__),
                                     '..', '..', '..',
                                     'nnue', 'models',
                                     'dex_nnue_weights.npz')
    _evaluator = NNUEEvaluator(weights_path)
    return _evaluator


def evaluate_board_nnue(board) -> int:
    """Drop-in replacement for evaluate.evaluate_board using NNUE.

    Uses full computation (no incremental update). For incremental
    updates, use the evaluator directly with accumulators in the search.
    """
    if _evaluator is None:
        load_nnue()
    return _evaluator.evaluate(board)
