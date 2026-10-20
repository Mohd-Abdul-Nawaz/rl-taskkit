"""Tests for normalize_username (hidden from the model being trained)."""
import pytest

from normalizer import normalize_username


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("  Alice  ", "alice"),
        ("Bob Smith", "bob-smith"),
        ("carol\t  dawn", "carol-dawn"),
        ("Erin\nO'Neil", "erin-o-neil"),
        ("a  --  b", "a-b"),
        ("_under_score_", "_under_score_"),
        ("  ---frank---  ", "frank"),
        ("grace_hopper-1959", "grace_hopper-1959"),
        ("x" * 64, "x" * 64),
        ("MiXeD CASE With Symbols #$%", "mixed-case-with-symbols"),
    ],
)
def test_normalize_username_happy_paths(raw, expected):
    assert normalize_username(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", "\t\n", "!!!", "---"])
def test_normalize_username_rejects_empty_results(raw):
    with pytest.raises(ValueError):
        normalize_username(raw)


@pytest.mark.parametrize("raw", [None, 42, 3.14, ["alice"], {"a": 1}])
def test_normalize_username_rejects_non_strings(raw):
    with pytest.raises(ValueError):
        normalize_username(raw)


def test_normalize_username_is_idempotent():
    samples = ["  Alice  ", "Bob   Smith", "a  --  b", "MiXeD CASE With Symbols #$%"]
    for raw in samples:
        once = normalize_username(raw)
        assert normalize_username(once) == once
