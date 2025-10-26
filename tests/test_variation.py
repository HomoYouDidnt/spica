import pytest

from spica.variation.operators import mutate_decoding, mutate_mode, swap_two


def test_swap_two_basic():
    assert swap_two(["a", "b", "c"], 1) == ["a", "c", "b"]
    with pytest.raises(IndexError):
        swap_two(["a"], 0)


def test_mutate_mode_in_manifest():
    m = {"name": "x", "version": "0.1.0", "resources": {"cpu": "1"}}
    m2 = mutate_mode(m, "fast")
    assert m2["resources"]["mode"] == "fast"
    assert "mode" not in m["resources"]


def test_mutate_decoding_clamps_and_tweaks():
    p = {"temperature": 1.5, "top_k": 0, "top_p": 0.05}
    m = mutate_decoding(p)
    assert 0.1 <= m["temperature"] <= 1.2
    assert 1 <= m["top_k"] <= 100
    assert 0.1 <= m["top_p"] <= 1.0
