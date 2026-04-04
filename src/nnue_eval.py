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
        self.w1 = data['net.0.weight']  # (hidden1, 768)
        self.b1 = data['net.0.bias']    # (hidden1,)
        self.w2 = data['net.2.weight']  # (hidden2, hidden1)
        self.b2 = data['net.2.bias']    # (hidden2,)
        self.w3 = data['net.4.weight']  # (1, hidden2)
        self.b3 = data['net.4.bias']    # (1,)
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
        # Layer 1: linear + ReLU
        h1 = features @ self.w1.T + self.b1
        h1 = np.maximum(h1, 0)  # ReLU

        # Layer 2: linear + ReLU
        h2 = h1 @ self.w2.T + self.b2
        h2 = np.maximum(h2, 0)  # ReLU

        # Output layer
        out = h2 @ self.w3.T + self.b3
        return float(out[0])

    def evaluate(self, board) -> int:
        """Evaluate a position. Returns centipawns, side-to-move relative."""
        features = self._board_to_features(board)
        raw_score = self._forward(features)
        score_cp = raw_score * self.eval_scale

        # If black to move, the feature flip already handled perspective
        return int(score_cp)


# Singleton evaluator instance (loaded once, reused)
_evaluator = None


def load_nnue(weights_path: str = None):
    """Load the NNUE evaluator. Call once at startup."""
    global _evaluator
    if weights_path is None:
        # Default path relative to src/
        weights_path = os.path.join(os.path.dirname(__file__),
                                     '..', 'nnue', 'models',
                                     'dex_nnue_weights.npz')
    _evaluator = NNUEEvaluator(weights_path)
    return _evaluator


def evaluate_board_nnue(board) -> int:
    """Drop-in replacement for evaluate.evaluate_board using NNUE."""
    if _evaluator is None:
        load_nnue()
    return _evaluator.evaluate(board)
