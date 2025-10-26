import argparse
import os
import sys

from spica.pipelines.registry import PipelineRegistry, run_pipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline", default="configs/pipelines/local.yaml")
    ap.add_argument("--variant-id", default="dev_spica")
    ap.add_argument("--domain", default="qa.rag")
    args = ap.parse_args()
    print(
        f"[TELEMETRY] → {os.environ.get('SPICA_TELEMETRY_PATH','spica.telemetry.jsonl')}"
    )
    reg = PipelineRegistry()
    spec = reg.load(args.pipeline)
    adapters = reg.build(spec)
    context = {
        "run_id": "dev",
        "variant_id": args.variant_id,
        "parent_id": None,
        "origin_commit": "WORKTREE",
        "domain": args.domain,
        "tokens_used": 0,
    }
    seed = {
        "text": "hello spica",
        "candidates": ["hello spica", "goodnight moon"],
        "query": "hello",
    }
    out = run_pipeline(adapters, context, seed)
    print(out)


if __name__ == "__main__":
    sys.exit(main())
