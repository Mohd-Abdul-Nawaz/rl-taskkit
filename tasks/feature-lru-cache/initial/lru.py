"""A least-recently-used cache.

See ``prompt.md`` for the full contract. This starter implementation is
incomplete: eviction and recency tracking are missing.
"""
from collections import OrderedDict


class LRUCache:
    """Fixed-capacity cache that evicts the least recently used key."""

    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity = capacity
        self._data = OrderedDict()

    def get(self, key):
        if key not in self._data:
            raise KeyError(key)
        return self._data[key]

    def put(self, key, value):
        self._data[key] = value

    def __len__(self):
        return len(self._data)

    def __contains__(self, key):
        return key in self._data

    def keys_mru_to_lru(self):
        return list(self._data.keys())
