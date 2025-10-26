import json
import os
import tempfile


def test_telemetry_enriched_fields_present():
    from spica.telemetry import log_event

    with tempfile.TemporaryDirectory() as d:
        fp = os.path.join(d, "t.jsonl")
        os.environ["SPICA_TELEMETRY_PATH"] = fp
        try:
            log_event(
                {
                    "cell": "x",
                    "ok": True,
                    "latency_ms": 1.0,
                    "seed": 123,
                    "kl_persona": 0.01,
                    "kl_task": 0.03,
                    "tau_persona": 0.02,
                    "tau_task": 0.08,
                    "budgets_used": {"tokens_used": 5, "tokens_budget": 10},
                }
            )
            with open(fp, "r", encoding="utf-8") as f:
                rec = json.loads(f.readline())
        finally:
            os.environ.pop("SPICA_TELEMETRY_PATH", None)
    assert rec["cell"] == "x"
    for k in [
        "ts",
        "trace_id",
        "seed",
        "kl_persona",
        "kl_task",
        "tau_persona",
        "tau_task",
        "budgets_used",
    ]:
        assert k in rec

