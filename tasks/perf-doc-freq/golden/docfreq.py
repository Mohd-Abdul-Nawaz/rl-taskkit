"""Document-frequency utilities."""
import re
from collections import Counter

_TOKEN = re.compile(r"[a-z0-9]+")


def top_k_terms(docs, k):
    """Return the top-k terms by document frequency."""
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ValueError("k must be a positive int")

    document_frequency: Counter = Counter()
    for doc in docs:
        document_frequency.update(set(_TOKEN.findall(doc.lower())))

    ranked = sorted(document_frequency.items(), key=lambda item: (-item[1], item[0]))
    return [term for term, _ in ranked[:k]]
