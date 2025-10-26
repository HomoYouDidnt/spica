from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import yaml

from spica.capability_registry import CapabilityRegistry
from spica.cell_adapter import CellAdapter


@dataclass
class StepSpec:
    name: Optional[str] = None
    id: Optional[str] = None
    select_by_tag: Optional[List[str]] = None


@dataclass
class PipelineSpec:
    steps: List[StepSpec]


class PipelineRegistry:
    def __init__(self, reg: Optional[CapabilityRegistry] = None):
        self._reg = reg or CapabilityRegistry()

    @staticmethod
    def _load_yaml(path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load(self, path: str) -> PipelineSpec:
        data = self._load_yaml(path)
        steps: List[StepSpec] = []
        for s in data.get("steps", []):
            name = s.get("name")
            tags = s.get("select_by_tag")
            if (name is None and tags is None) or (
                name is not None and tags is not None
            ):
                raise ValueError(
                    "Each step must have either 'name' or 'select_by_tag', but not both."
                )
            if tags is not None and not isinstance(tags, list):
                raise ValueError("'select_by_tag' must be a list of strings")
            steps.append(StepSpec(name=name, id=s.get("id"), select_by_tag=tags))
        return PipelineSpec(steps=steps)

    def build(self, spec: PipelineSpec, *, metrics_sink=None) -> List[CellAdapter]:
        adapters: List[CellAdapter] = []
        for s in spec.steps:
            cap_name: Optional[str] = s.name
            if cap_name is None and s.select_by_tag:
                candidates = self._reg.list(tag_filter=set(s.select_by_tag))
                if not candidates:
                    raise ValueError(f"No capability found for tags {s.select_by_tag}")
                cap_name = candidates[0]
            assert cap_name is not None
            fn, manifest, schema = self._reg.resolve(cap_name)
            budgets = schema.budgets or {}
            adapters.append(
                CellAdapter(fn, manifest, metrics_sink=metrics_sink, budgets=budgets)
            )
        return adapters


def run_pipeline(
    adapters: List[CellAdapter], context: Dict[str, Any], seed_inputs: Dict[str, Any]
) -> Dict[str, Any]:
    state: Dict[str, Any] = dict(seed_inputs or {})
    out: Dict[str, Any] = {}
    for cell in adapters:
        need = getattr(cell, "manifest").inputs or []
        call = {k: state[k] for k in need if k in state}
        out = cell.run(context, **call)
        if isinstance(out, dict):
            for k, v in out.items():
                if k != "_metrics":
                    state[k] = v
    final_state = dict(state)
    if isinstance(out, dict) and "_metrics" in out:
        final_state["_metrics"] = out["_metrics"]
    return final_state
