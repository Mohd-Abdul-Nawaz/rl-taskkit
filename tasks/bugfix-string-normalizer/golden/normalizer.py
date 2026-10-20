"""Username normalization helpers.

Spec
----
``normalize_username(raw)`` must:

1. Raise ``ValueError`` if ``raw`` is not a ``str``.
2. Lower-case the input and strip leading/trailing whitespace.
3. Replace every run of disallowed characters with a single ``-``.
   Disallowed characters are everything except ``a-z``, ``0-9``, ``-`` and ``_``.
4. Collapse any run of two or more hyphens into a single ``-``.
5. Strip ``-`` from both ends of the result.
6. Raise ``ValueError`` if the final result is empty.
"""
import re

_DISALLOWED = re.compile(r"[^a-z0-9_-]+")
_HYPHEN_RUNS = re.compile(r"-{2,}")


def normalize_username(raw):
    """Normalize a username according to the module-level spec."""
    if not isinstance(raw, str):
        raise ValueError("username must be a string")
    value = raw.strip().lower()
    value = _DISALLOWED.sub("-", value)
    value = _HYPHEN_RUNS.sub("-", value).strip("-")
    if not value:
        raise ValueError("username is empty after normalization")
    return value
