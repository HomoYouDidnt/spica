from __future__ import annotations

import argparse
import json

from spica.promotions import build_promotion_unit


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant-id", required=True)
    ap.add_argument("--baseline-id", required=True)
    ap.add_argument("--pipeline", required=True)
    ap.add_argument("--metrics", required=True)
    ap.add_argument(
        "--datasets",
        required=True,
        help='JSON mapping, e.g. "{\"gold\":\"gold.jsonl\",\"fresh\":\"fresh.jsonl\"}"',
    )
    ap.add_argument(
        "--guardrails",
        required=True,
        help='JSON object, e.g. "{\"kl_persona\":0.01,\"kl_task\":0.04,\"violations\":0}"',
    )
    ap.add_argument("--repro", default="tools/shadow_runner.py")
    ap.add_argument("--origin-commit", default="WORKTREE")
    ap.add_argument("--parent-id", default="")
    ap.add_argument("--mutation-vector", default="[]", help="JSON list string")
    ap.add_argument("--env-hash", default="unknown")
    ap.add_argument("--out", default="promotion_unit.json")
    args = ap.parse_args(argv)

    datasets = json.loads(args.datasets)
    guards = json.loads(args.guardrails)
    lineage = {
        "origin_commit": args.origin_commit,
        "parent_id": args.parent_id,
        "mutation_vector": json.loads(args.mutation_vector),
    }

    out = build_promotion_unit(
        variant_id=args.variant_id,
        baseline_id=args.baseline_id,
        pipeline_path=args.pipeline,
        datasets=datasets,
        metrics_path=args.metrics,
        guardrail_report=guards,
        repro_script=args.repro,
        lineage=lineage,
        env_hash=args.env_hash,
        out_path=args.out,
    )
    print(f"[promotion] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

