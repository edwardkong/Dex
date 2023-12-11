from collections import namedtuple

TTEntry = namedtuple('TTEntry', ['key', 'depth', 'eval'])
    
class TranspositionTable:
    def __init__(self):
        self.entries = {}

    def clear(self):
        pass

    def store_eval(self, tt_entry):
        """Stores an entry in the table."""
        self.entries[tt_entry.key] = tt_entry
    
    def lookup_key(self, key, depth):
        """Retrieves an entry if it exists and the depth searched
        is greater than the lookup depth.
        """
        if key in self.entries:
            if self.entries.get(key).depth >= depth:
                return self.entries[key]
        return None

    def drop_old_entries(self, pawn_key):
        """As pawns cannot move backwards, if a pawn is captured
        or the pawn structure changes, any entry prior to the
        move can be dropped.
        """
        return