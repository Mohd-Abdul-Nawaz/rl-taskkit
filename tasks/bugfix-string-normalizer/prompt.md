# Fix username normalization edge cases

The file `normalizer.py` exposes `normalize_username(raw)`. The docstring
documents the full contract, but the implementation is buggy. **Fix the bugs
so the function matches its documented behaviour exactly.**

## Contract

`normalize_username(raw)` must:

1. Raise `ValueError` if `raw` is not a `str`.
2. Lower-case the input and strip leading/trailing whitespace.
3. Replace every run of disallowed characters with a single `-`.
   Disallowed characters are everything except `a-z`, `0-9`, `-` and `_`
   (this includes whitespace such as spaces, tabs and newlines).
4. Collapse any resulting run of two or more hyphens into a single `-`.
5. Strip `-` from both ends of the result.
6. Raise `ValueError` if the final result is an empty string.

## Constraints

- Edit **only** `normalizer.py`. Do not modify anything under `tests/`.
- Python 3 standard library only.
- Keep the module importable without side effects.

## Example

```python
normalize_username("  Alice  ")      # "alice"
normalize_username("Bob   Smith")    # "bob-smith"
normalize_username("Ünïcode User!")  # "n-code-user"
normalize_username("")               # raises ValueError
```
