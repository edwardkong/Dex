"""Opening book for Dex chess engine.

Loads a text file where each line is a sequence of UCI moves representing
an opening variation. During play, the engine looks up the current move
history and plays the book move if available, with random selection when
multiple continuations exist.

Usage:
    from book import OpeningBook
    book = OpeningBook("book.txt")
    move = book.probe(move_history)  # Returns UCI string or None
"""

import os
import random


class OpeningBook:
    def __init__(self, book_path: str = None):
        if book_path is None:
            book_path = os.path.join(os.path.dirname(__file__), 'book.txt')
        self.lines = []
        self._load(book_path)

    def _load(self, path: str):
        """Load book lines from a text file."""
        try:
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.lines.append(line.split())
        except FileNotFoundError:
            pass

    def probe(self, move_history: list[str]) -> str | None:
        """Look up the current position in the book.

        Args:
            move_history: List of UCI move strings played so far.

        Returns:
            A UCI move string if a book move exists, None otherwise.
        """
        n = len(move_history)

        # Find all book lines that match the current move history
        candidates = []
        for line in self.lines:
            if len(line) <= n:
                continue
            # Check if this line matches our history
            if line[:n] == move_history:
                candidates.append(line[n])

        if not candidates:
            return None

        # Pick randomly from available continuations
        return random.choice(candidates)
