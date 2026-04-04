"""NNUE evaluation for Dex chess engine.

Loads pre-trained weights (numpy format) and runs inference without PyTorch.
This module is designed to work with PyPy (no torch dependency at runtime).

Usage in the engine:
    from nnue_eval import NNUEEvaluator
    evaluator = NNUEEvaluator("nnue/models/dex_nnue_weights.npz")
    score = evaluator.evaluate(board)  # returns centipawns, side-to-move relative
"""

import os
import numpy as np
import tools


class NNUEEvaluator:
    """Neural network evaluation using pre-trained weights."""

    def __init__(self, weights_path: str):
        data = np.load(weights_path)
        # Load layers dynamically (supports 2 or 3 hidden layers)
        self.layers = []
        i = 0
        while f'net.{i}.weight' in data:
            self.layers.append((data[f'net.{i}.weight'], data[f'net.{i}.bias']))
            i += 2  # Skip ReLU layers (no weights)
        self.use_wdl = bool(data.get('use_wdl', [0])[0])
        if not self.use_wdl:
            self.eval_scale = float(data['eval_scale'][0])

    def _board_to_features(self, board) -> np.ndarray:
        """Convert a Dex Board to a 768-element feature vector.

        Piece indices in Dex: 0-5 = WP,WN,WB,WR,WQ,WK; 6-11 = BP,BN,BB,BR,BQ,BK
        """
        features = np.zeros(768, dtype=np.float32)

        for piece_idx in range(12):
            bb = board.bitboards[piece_idx]
            while bb:
                sq = tools.bitscan_lsb(bb)
                features[piece_idx * 64 + sq] = 1.0
                bb &= bb - 1

        # Flip for black to move (network always evaluates from white's perspective,
        # then we negate for black)
        if board.color == 1:
            flipped = np.zeros(768, dtype=np.float32)
            for pt in range(6):
                for sq in range(64):
                    mirror_sq = sq ^ 56  # Flip rank
                    flipped[(pt + 6) * 64 + mirror_sq] = features[pt * 64 + sq]
                    flipped[pt * 64 + mirror_sq] = features[(pt + 6) * 64 + sq]
            features = flipped

        return features

    def _forward(self, features: np.ndarray) -> float:
        """Run the neural network forward pass."""
        x = features
        for i, (w, b) in enumerate(self.layers):
            x = x @ w.T + b
            # ReLU on all layers except the last
            if i < len(self.layers) - 1:
                x = np.maximum(x, 0)
        return float(x[0])

    def evaluate(self, board) -> int:
        """Evaluate a position. Returns centipawns, side-to-move relative."""
        features = self._board_to_features(board)
        logit = self._forward(features)

        if self.use_wdl:
            # Convert logit -> sigmoid -> centipawns
            # sigmoid(logit) gives WDL probability, convert back to cp
            # Clamp logit to avoid overflow
            logit = max(-10.0, min(10.0, logit))
            wdl = 1.0 / (1.0 + np.exp(-logit))
            wdl = max(0.001, min(0.999, wdl))
            score_cp = 400.0 * np.log(wdl / (1.0 - wdl))
        else:
            score_cp = logit * self.eval_scale

        return int(score_cp)


# Singleton evaluator instance (loaded once, reused)
_evaluator = None


def load_nnue(weights_path: str = None):
    """Load the NNUE evaluator. Call once at startup."""
    global _evaluator
    if weights_path is None:
        # Default path relative to src/
        weights_path = os.path.join(os.path.dirname(__file__),
                                     '..', '..', '..',
                                     'nnue', 'models',
                                     'dex_nnue_weights.npz')
    _evaluator = NNUEEvaluator(weights_path)
    return _evaluator


def evaluate_board_nnue(board) -> int:
    """Drop-in replacement for evaluate.evaluate_board using NNUE."""
    if _evaluator is None:
        load_nnue()
    return _evaluator.evaluate(board)
