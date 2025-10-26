from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from typing import Dict, Iterable, List, Tuple

from spica.pipelines.registry import PipelineRegistry, run_pipeline


def stream_jsonl(path: str) -> Iterable[Dict]:
    with (open(path, "r", encoding="utf-8") if path != "-" else sys.stdin) as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def group_conversations(items: Iterable[Dict]) -> Dict[str, List[Dict]]:
    convs: Dict[str, List[Dict]] = {}
    for r in items:
        convs.setdefault(r.get("conv_id", "unknown"), []).append(r)
    for v in convs.values():
        v.sort(key=lambda r: (r.get("turn") is None, r.get("turn", 0)))
    return convs


def acc_at_1(pred: str, gold: str) -> float:
    if not gold:
        return 0.0
    return 1.0 if (pred or "").strip().casefold() == gold.strip().casefold() else 0.0


def p95(values: List[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = max(0, min(len(s) - 1, int(math.ceil(0.95 * len(s)) - 1)))
    return float(s[k])


def bootstrap_ci(delta_values: List[float], iters: int = 1000, seed: int = 42) -> Tuple[float, float, float]:
    random.seed(seed)
    if not delta_values:
        return 0.0, 0.0, 0.0
    n = len(delta_values)
    means = []
    for _ in range(iters):
        sample = [delta_values[random.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / len(sample))
    means.sort()
    lo = means[int(0.025 * iters)]
    hi = means[int(0.975 * iters)]
    return (sum(delta_values) / len(delta_values), lo, hi)


def run_pipeline_for_conv(adapters, ctx_seed: Dict, turns: List[Dict]) -> Dict:
    seed = {"text": "", "candidates": [], "query": ""}
    for t in turns:
        if t.get("role") == "user":
            if "text" in t:
                seed["text"] = t["text"]
            if "candidates" in t:
                seed["candidates"] = t["candidates"]
            if "query" in t:
                seed["query"] = t["query"]
    ctx = dict(ctx_seed)
    return run_pipeline(adapters, ctx, seed)


def evaluate_file(pipeline_path: str, input_path: str, baseline_metrics_path: str | None, limit: int) -> Dict:
    reg = PipelineRegistry()
    spec = reg.load(pipeline_path)
    adapters = reg.build(spec)

    convs = group_conversations(stream_jsonl(input_path))
    accs: List[float] = []
    latencies: List[float] = []
    per_conv = []

    evaluated = 0
    for cid, turns in convs.items():
        if evaluated >= limit:
            break
        out = run_pipeline_for_conv(
            adapters,
            {
                "run_id": "shadow",
                "variant_id": "shadow_variant",
                "origin_commit": "WORKTREE",
                "domain": "qa.rag",
                "tokens_used": 0,
                "seed": 1234 + evaluated,
            },
            turns,
        )

        pred = (out.get("selected") or out.get("text") or "")
        if isinstance(pred, list):
            pred_str = pred[0] if pred else ""
        else:
            pred_str = str(pred)

        gold = None
        for t in turns[::-1]:
            if "gold" in t:
                gold = t["gold"]
                break

        a = acc_at_1(pred_str, gold or "")
        accs.append(a)
        lat_ms = 0.0
        if "_metrics" in out and isinstance(out["_metrics"], dict):
            lat_ms = sum(
                m.get("latency_ms", 0.0) for m in out["_metrics"].values() if isinstance(m, dict)
            )
        latencies.append(lat_ms)
        per_conv.append({"conv_id": cid, "acc1": a, "lat_ms": lat_ms})
        evaluated += 1

    result = {
        "n": evaluated,
        "answer_accuracy@1": sum(accs) / len(accs) if accs else 0.0,
        "latency_p95_ms": p95(latencies),
        "per_conv": per_conv,
    }

    if baseline_metrics_path and os.path.exists(baseline_metrics_path):
        with open(baseline_metrics_path, "r", encoding="utf-8") as f:
            baseline = json.load(f)
        base_by_id = {r["conv_id"]: r for r in baseline.get("per_conv", [])}
        deltas = []
        for r in per_conv:
            cid = r["conv_id"]
            if cid in base_by_id:
                deltas.append(r["acc1"] - base_by_id[cid].get("acc1", 0.0))
        if not deltas and "answer_accuracy@1" in baseline:
            deltas = [result["answer_accuracy@1"] - baseline["answer_accuracy@1"]]
        mean_delta, ci_lo, ci_hi = bootstrap_ci(deltas) if deltas else (0.0, 0.0, 0.0)
        result["delta_acc1_mean"] = mean_delta
        result["delta_acc1_ci95"] = [ci_lo, ci_hi]

    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline", required=True, help="Pipeline YAML (capability-backed)")
    ap.add_argument("--input", required=True, help="Sanitized transcripts JSONL")
    ap.add_argument("--baseline", default="", help="Path to baseline metrics JSON for delta/CI")
    ap.add_argument("--out", default="shadow.metrics.json", help="Output aggregate metrics JSON")
    ap.add_argument("--limit", type=int, default=1000)
    args = ap.parse_args(argv)

    res = evaluate_file(args.pipeline, args.input, args.baseline or None, args.limit)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(
        f"[shadow] n={res['n']} acc@1={res['answer_accuracy@1']:.3f} lat_p95_ms={res['latency_p95_ms']:.1f}"
    )
    if "delta_acc1_mean" in res:
        lo, hi = res["delta_acc1_ci95"]
        print(f"[shadow] Δacc@1={res['delta_acc1_mean']:.3f} CI95=[{lo:.3f},{hi:.3f}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

