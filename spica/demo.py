import argparse
import importlib
import sys

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
    with open(args.cells, "r") as f:
        cfg = yaml.safe_load(f)
    registry = dict(load_cell(c) for c in cfg["cells"])
    context = {"run_id": "dev"}
    result = {}
    for step in cfg["pipeline"]:
        cell = registry[step]
        result = cell.run(context, **(result or {"text": "hello spica"}))
        # Optional: echo metrics
        try:
            m = result.get("_metrics", {}).get(cell.manifest.name)  # type: ignore[attr-defined]
            if m:
                print(f"[METRICS] {cell.manifest.name}: {m}")  # type: ignore[attr-defined]
        except Exception:
            pass
    print(result)


if __name__ == "__main__":
    sys.exit(main())
