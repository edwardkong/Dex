"""Evaluation package for Dex chess engine.

Supports multiple evaluation backends. Set the active evaluator
by changing EVAL_TYPE below or via the DEX_EVAL environment variable.

Available types:
    "heuristic"  - Hand-tuned evaluation (default)
    "nnue"       - Neural network evaluation

Adding a new evaluator:
    1. Create a new file in eval/heuristic/ or eval/nnue/
    2. Implement evaluate_board(board) -> int (centipawns, side-to-move relative)
    3. Update the imports below
"""

import os

# Select evaluator: environment variable or default
EVAL_TYPE = os.environ.get("DEX_EVAL", "heuristic")

if EVAL_TYPE == "nnue":
    from eval.nnue.v1 import evaluate_board_nnue as evaluate_board, load_nnue
    # Auto-load the model
    load_nnue()
else:
    from eval.heuristic.v1 import evaluate_board

# Always available regardless of eval type
from eval.heuristic.v1 import is_insufficient_material, update_depth
