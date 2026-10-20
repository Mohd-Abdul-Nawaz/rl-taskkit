# Implement a least-recently-used cache

`lru.py` contains a partial `LRUCache` implementation. Complete it so that it
behaves as a proper least-recently-used (LRU) cache with O(1) average
`get`/`put`.

## Contract

`LRUCache(capacity)`

- `capacity` must be a positive `int`; otherwise raise `ValueError`.
- `get(key)` returns the stored value and marks `key` as most recently used.
  Raises `KeyError` if the key is absent.
- `put(key, value)` inserts or updates `key` and marks it as most recently
  used. When the cache exceeds capacity, the **least recently used** key is
  evicted first. Updating an existing key must not evict anything.
- `len(cache)` returns the number of stored entries.
- `key in cache` is `True` iff the key is stored, and must **not** affect
  recency.
- `keys_mru_to_lru()` returns the stored keys ordered from most to least
  recently used.

## Constraints

- Edit **only** `lru.py`. Do not modify anything under `tests/`.
- Python 3 standard library only.
- `get`, `put`, `__contains__` and `keys_mru_to_lru` should be O(1) /
  O(n) respectively (no scans inside `get`/`put`).

## Example

```python
c = LRUCache(2)
c.put("a", 1)
c.put("b", 2)
c.get("a")          # 1 — "a" is now MRU, "b" is LRU
c.put("c", 3)       # evicts "b"
b in c              # False
c.keys_mru_to_lru() # ["c", "a"]
```
