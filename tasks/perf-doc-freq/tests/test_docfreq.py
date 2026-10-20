"""Tests for top_k_terms (hidden from the model being trained).

Includes a correctness suite plus a deterministic performance budget test.
"""
import random
import time

import pytest

from docfreq import top_k_terms

PERF_BUDGET_MS = 1000.0


def test_rejects_non_positive_k():
    with pytest.raises(ValueError):
        top_k_terms(["alpha beta"], 0)
    with pytest.raises(ValueError):
        top_k_terms(["alpha beta"], -3)


def test_counts_documents_not_occurrences():
    docs = ["alpha alpha alpha", "alpha"]
    assert top_k_terms(docs, 1) == ["alpha"]


def test_basic_ranking_with_tiebreak():
    docs = ["alpha beta", "alpha", "gamma"]
    assert top_k_terms(docs, 2) == ["alpha", "beta"]


def test_tiebreak_is_lexicographic():
    docs = ["delta", "charlie", "bravo", "alpha"]
    assert top_k_terms(docs, 4) == ["alpha", "bravo", "charlie", "delta"]


def test_tokenization_ignores_punctuation_and_case():
    assert top_k_terms(["Hello, hello world!"], 5) == ["hello", "world"]


def test_returns_fewer_terms_than_k_when_needed():
    assert top_k_terms(["one two"], 10) == ["one", "two"]


def test_top_k_subset_is_correct():
    docs = ["a b c", "a b", "a", "d"]
    assert top_k_terms(docs, 2) == ["a", "b"]
    assert top_k_terms(docs, 1) == ["a"]


def _make_large_corpus():
    rng = random.Random(20240601)
    vocab = [f"term{i:03d}" for i in range(200)]
    return [" ".join(rng.choice(vocab) for _ in range(30)) for _ in range(250)]


def test_performance_budget():
    docs = _make_large_corpus()
    started = time.perf_counter()
    result = top_k_terms(docs, 10)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    assert len(result) == 10
    assert elapsed_ms < PERF_BUDGET_MS, f"took {elapsed_ms:.0f}ms, budget is {PERF_BUDGET_MS:.0f}ms"
