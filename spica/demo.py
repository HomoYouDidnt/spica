import argparse
import importlib
import os
import sys
from typing import Any, Dict

import yaml


def load_cell(spec):
    mod = importlib.import_module(spec["module"])
    fn = getattr(mod, spec.get("entry", "run"))
    manifest = getattr(mod, spec.get("manifest_attr", "MANIFEST"))
    from .cell_adapter import CellAdapter

    return spec["id"], CellAdapter(fn, manifest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default="configs/cells/local.yaml")
    args = ap.parse_args()
    print(
        f"[TELEMETRY] → {os.environ.get('SPICA_TELEMETRY_PATH','spica.telemetry.jsonl')}"
    )
    with open(args.cells, "r") as f:
        cfg = yaml.safe_load(f)
    registry = dict(load_cell(c) for c in cfg["cells"])
    context = {"run_id": "dev"}
    state: Dict[str, Any] = {}
    for step in cfg["pipeline"]:
        cell = registry[step]
        # choose inputs based on manifest contract
        need = getattr(cell, "manifest").inputs or []
        call: Dict[str, Any] = {k: state[k] for k in need if k in state}
        # seed defaults when missing
        if "text" in need and "text" not in call:
            call["text"] = "hello spica"
        if "candidates" in need and "candidates" not in call:
            call["candidates"] = ["hello spica", "goodnight moon"]
        if "query" in need and "query" not in call:
            call["query"] = "hello"

        result = cell.run(context, **call)
        # Optional: echo metrics
        try:
            m = result.get("_metrics", {}).get(cell.manifest.name)  # type: ignore[attr-defined]
            if m:
                print(f"[METRICS] {cell.manifest.name}: {m}")  # type: ignore[attr-defined]
        except Exception:
            pass
        # merge outputs into state (skip _metrics)
        if isinstance(result, dict):
            for k, v in result.items():
                if k != "_metrics":
                    state[k] = v
    print(state)


if __name__ == "__main__":
    sys.exit(main())
