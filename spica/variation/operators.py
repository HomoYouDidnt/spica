from __future__ import annotations

from typing import Dict, List


def swap_two(pipeline: List[str], i: int) -> List[str]:
    """Swap adjacent steps i and i+1; raises if out of bounds."""
    if i < 0 or i >= len(pipeline) - 1:
        raise IndexError("swap_two index out of range")
    pip = list(pipeline)
    pip[i], pip[i + 1] = pip[i + 1], pip[i]
    return pip


def mutate_mode(manifest: Dict, new_mode: str) -> Dict:
    """
    Example structural/behavioral mutation for simple cells that expose a 'mode'
    inside manifest['resources'] or manifest['metrics'] etc. No-op if absent.
    """
    m = {**manifest}
    res = dict(m.get("resources", {}))
    res["mode"] = new_mode
    m["resources"] = res
    return m
