# Optimize top-k document-frequency ranking

`docfreq.py` contains a working-but-slow `top_k_terms(docs, k)` function.
Refactor it so it produces identical results while running in O(total tokens)
time.

## Contract

`top_k_terms(docs, k)` must:

1. Raise `ValueError` if `k` is not a positive `int`.
2. Tokenize each document by lower-casing it and extracting maximal runs of
   `[a-z0-9]` characters (punctuation and whitespace are just separators).
3. Compute the **document frequency** of every term (the number of documents
   it appears in, counting each document at most once).
4. Return the top `k` terms ordered by descending frequency, with ties broken
   by ascending lexicographic order. Return fewer than `k` terms when fewer
   exist.

## Constraints

- Edit **only** `docfreq.py`. Do not modify anything under `tests/`.
- Python 3 standard library only.
- The hidden performance test builds 1,200 documents of 40 tokens each and
  requires the call to finish in under 1,000 ms.

## Example

```python
docs = ["alpha beta", "alpha", "gamma"]
top_k_terms(docs, 2)          # ["alpha", "beta"]
top_k_terms(["Hello, hello world!"], 5)  # ["hello", "world"]
```
