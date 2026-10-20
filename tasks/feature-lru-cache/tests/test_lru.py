"""Tests for LRUCache (hidden from the model being trained)."""
import random

import pytest

from lru import LRUCache


def test_construction_and_len():
    cache = LRUCache(3)
    assert len(cache) == 0
    cache.put("a", 1)
    cache.put("b", 2)
    assert len(cache) == 2


@pytest.mark.parametrize("capacity", [0, -1, -100])
def test_non_positive_capacity_rejected(capacity):
    with pytest.raises(ValueError):
        LRUCache(capacity)


def test_get_missing_key_raises():
    cache = LRUCache(2)
    with pytest.raises(KeyError):
        cache.get("missing")


def test_put_and_get_roundtrip():
    cache = LRUCache(2)
    cache.put("a", 1)
    assert cache.get("a") == 1


def test_evicts_least_recently_used():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    assert "a" not in cache
    assert "b" in cache
    assert "c" in cache


def test_get_refreshes_recency():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    cache.put("c", 3)
    assert "b" not in cache
    assert "a" in cache


def test_update_refreshes_recency_and_does_not_evict():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("a", 10)
    assert len(cache) == 2
    assert cache.get("a") == 10
    cache.put("c", 3)
    assert "b" not in cache
    assert "a" in cache


def test_contains_does_not_refresh_recency():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert "a" in cache
    cache.put("c", 3)
    assert "a" not in cache


def test_keys_mru_to_lru_order():
    cache = LRUCache(3)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    cache.get("a")
    assert cache.keys_mru_to_lru() == ["a", "c", "b"]


def test_matches_reference_model_under_random_operations():
    rng = random.Random(7)
    capacity = 5
    cache = LRUCache(capacity)
    model = []  # keys ordered least -> most recently used
    store = {}

    for _ in range(500):
        op = rng.choice(["put", "get", "contains"])
        key = f"k{rng.randrange(8)}"
        if op == "put":
            value = rng.randrange(1000)
            cache.put(key, value)
            store[key] = value
            if key in model:
                model.remove(key)
            model.append(key)
            if len(model) > capacity:
                evicted = model.pop(0)
                del store[evicted]
        elif op == "get":
            if key in store:
                assert cache.get(key) == store[key]
                model.remove(key)
                model.append(key)
            else:
                with pytest.raises(KeyError):
                    cache.get(key)
        else:
            assert (key in cache) == (key in store)

        assert len(cache) == len(model)
        assert sorted(cache.keys_mru_to_lru()) == sorted(model)
        assert cache.keys_mru_to_lru() == list(reversed(model))
