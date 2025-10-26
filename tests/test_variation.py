import pytest

from spica.variation.operators import mutate_mode, swap_two


def test_swap_two_basic():
    assert swap_two(["a", "b", "c"], 1) == ["a", "c", "b"]
    with pytest.raises(IndexError):
        swap_two(["a"], 0)


def test_mutate_mode_in_manifest():
    m = {"name": "x", "version": "0.1.0", "resources": {"cpu": "1"}}
    m2 = mutate_mode(m, "fast")
    assert m2["resources"]["mode"] == "fast"
    assert "mode" not in m["resources"]

