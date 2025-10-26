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


def mutate_decoding(
    params: dict,
    *,
    temp_bounds=(0.1, 1.2),
    topk_bounds=(1, 100),
    topp_bounds=(0.1, 1.0),
) -> dict:
    """Clamp-and-tweak decoding params; fields optional."""
    out = dict(params or {})
    if "temperature" in out:
        out["temperature"] = min(
            max(out["temperature"] * 0.9, temp_bounds[0]), temp_bounds[1]
        )
    if "top_k" in out:
        out["top_k"] = int(min(max(out["top_k"] + 1, topk_bounds[0]), topk_bounds[1]))
    if "top_p" in out:
        out["top_p"] = min(max(out["top_p"] + 0.05, topp_bounds[0]), topp_bounds[1])
    return out
