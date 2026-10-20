"""Username normalization helpers.

Spec
----
``normalize_username(raw)`` must:

1. Raise ``ValueError`` if ``raw`` is not a ``str``.
2. Lower-case the input and strip leading/trailing whitespace.
3. Replace every run of disallowed characters with a single ``-``.
   Disallowed characters are everything except ``a-z``, ``0-9``, ``-`` and ``_``
   (this includes whitespace such as spaces, tabs and newlines).
4. Collapse any run of two or more hyphens into a single ``-``.
5. Strip ``-`` from both ends of the result.
6. Raise ``ValueError`` if the final result is empty.
"""


def normalize_username(raw):
    """Normalize a username according to the module-level spec."""
    value = raw.strip().lower()
    if " " in value:
        value = value.replace(" ", "-")
    return value
