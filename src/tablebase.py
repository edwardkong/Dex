"""Syzygy tablebase probing via the Lichess API.

Provides perfect endgame play for positions with 7 or fewer pieces.
Uses the free Lichess tablebase API — no local files needed.

Usage:
    from tablebase import probe_tablebase
    result = probe_tablebase(board)  # Returns (move_uci, eval_cp) or None
"""

import tools

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

TABLEBASE_URL = "https://tablebase.lichess.ovh/standard"
MAX_PIECES = 7  # Only probe with 7 or fewer pieces on board


def _count_pieces(board) -> int:
    """Count total pieces on the board."""
    count = 0
    occ = board.occupants[2]
    while occ:
        count += 1
        occ &= occ - 1
    return count


def _board_to_fen(board) -> str:
    """Convert Dex board to FEN string for API query."""
    piece_chars = {
        0: 'P', 1: 'N', 2: 'B', 3: 'R', 4: 'Q', 5: 'K',
        6: 'p', 7: 'n', 8: 'b', 9: 'r', 10: 'q', 11: 'k',
    }

    fen_rows = []
    for rank in range(7, -1, -1):
        empty = 0
        row = ""
        for file in range(8):
            sq = rank * 8 + file
            found = False
            for piece_idx in range(12):
                if board.bitboards[piece_idx] & (1 << sq):
                    if empty > 0:
                        row += str(empty)
                        empty = 0
                    row += piece_chars[piece_idx]
                    found = True
                    break
            if not found:
                empty += 1
        if empty > 0:
            row += str(empty)
        fen_rows.append(row)

    fen = "/".join(fen_rows)
    fen += " w " if board.color == 0 else " b "
    # Castling and en passant don't matter for tablebase (few pieces)
    fen += "- - 0 1"
    return fen


def probe_tablebase(board):
    """Probe the Lichess Syzygy tablebase for the current position.

    Returns (best_move_uci, eval_centipawns) if the position is in the
    tablebase, or None if not applicable (too many pieces, no connection, etc.).

    The eval is from the side-to-move's perspective:
    - Positive = winning
    - Zero = drawn
    - Negative = losing
    """
    if not HAS_REQUESTS:
        return None

    if _count_pieces(board) > MAX_PIECES:
        return None

    fen = _board_to_fen(board)

    try:
        response = requests.get(
            TABLEBASE_URL,
            params={"fen": fen},
            timeout=2.0
        )
        if response.status_code != 200:
            return None

        data = response.json()
    except Exception:
        return None

    category = data.get("category")
    if category is None:
        return None

    # Get the best move
    moves = data.get("moves", [])
    if not moves:
        return None

    best_move = moves[0]  # Already sorted by optimality
    move_uci = best_move["uci"]

    # Convert category to centipawn score
    dtm = data.get("dtm")
    if category == "win":
        eval_cp = 10000 - (abs(dtm) if dtm else 0)
    elif category == "loss":
        eval_cp = -10000 + (abs(dtm) if dtm else 0)
    else:  # draw, cursed-win, blessed-loss
        eval_cp = 0

    return move_uci, eval_cp
