from collections import namedtuple

# Bound types for alpha-beta search
EXACT = 0
LOWERBOUND = 1  # Beta cutoff — true value is >= eval
UPPERBOUND = 2  # Failed low — true value is <= eval

# Commits used to count the number of commital (irreversible) moves.
TTEntry = namedtuple('TTEntry', ['key', 'depth', 'eval', 'commits', 'bound'])

class TranspositionTable:
    def __init__(self):
        self.entries = {}

    def clear(self):
        self.entries.clear()

    def store_eval(self, tt_entry):
        """Stores an entry in the table. If there is a collision,
        the entry that was searched to a greater depth will be stored.
        """
        existing = self.entries.get(tt_entry.key, None)
        if existing and existing.depth > tt_entry.depth:
            return None

        self.entries[tt_entry.key] = tt_entry

    def lookup_key(self, key, depth):
        """Retrieves an entry if it exists and the depth searched
        is greater than the lookup depth.
        """
        if key in self.entries:
            if self.entries.get(key).depth >= depth:
                return self.entries[key]
        return None

    def evict_obsolete(self, commital_count):
        """Evicts entries with a lesser number of
        commital moves than the current count.
        """
        obsolete_keys = [key for key, entry in self.entries.items()
                      if entry.commits < commital_count]
        for key in obsolete_keys:
            del self.entries[key]
