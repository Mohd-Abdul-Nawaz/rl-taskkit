"""Document-frequency utilities (slow but mostly correct starter).

See ``prompt.md`` for the full contract. This implementation is O(V * N * L)
and re-splits every document for every term, so it cannot meet the time
budget on large inputs.
"""


def top_k_terms(docs, k):
    """Return the top-k terms by document frequency."""
    if not isinstance(k, int) or k <= 0:
        raise ValueError("k must be a positive int")

    vocab = []
    for doc in docs:
        for token in doc.lower().split():
            if token not in vocab:
                vocab.append(token)

    scores = []
    for term in vocab:
        count = 0
        for doc in docs:
            if term in doc.lower().split():
                count += 1
        scores.append((term, count))

    scores.sort(key=lambda item: (-item[1], item[0]))
    return [term for term, _ in scores[:k]]
