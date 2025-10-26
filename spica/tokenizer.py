from __future__ import annotations

from typing import Any, Mapping

# Simple, fast heuristic: ~4 chars ≈ 1 token
CHARS_PER_TOKEN = 4


def _count_str_tokens(s: str) -> int:
    if not s:
        return 0
    return max(1, (len(s) + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN)


def estimate_tokens(obj: Any) -> int:
    """
    Rough token estimate over nested structures:
    - str → char-based estimate
    - list/tuple/set → sum estimate_tokens
    - dict → sum over keys (str) + values
    - numbers/None/bool → ~0
    """
    if isinstance(obj, str):
        return _count_str_tokens(obj)
    if isinstance(obj, Mapping):
        total = 0
        for k, v in obj.items():
            if isinstance(k, str):
                total += _count_str_tokens(k)
            total += estimate_tokens(v)
        return total
    if isinstance(obj, (list, tuple, set)):
        return sum(estimate_tokens(v) for v in obj)
    return 0
