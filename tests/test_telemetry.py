import json
import os
import tempfile

from spica.telemetry import log_event


def test_log_event_writes_jsonl():
    with tempfile.TemporaryDirectory() as d:
        fp = os.path.join(d, "t.jsonl")
        os.environ["SPICA_TELEMETRY_PATH"] = fp
        try:
            log_event({"cell": "x", "ok": True, "latency_ms": 1.23})
        finally:
            del os.environ["SPICA_TELEMETRY_PATH"]
        with open(fp, "r", encoding="utf-8") as f:
            line = f.readline().strip()
        rec = json.loads(line)
        assert rec["cell"] == "x" and rec["ok"] is True and rec["latency_ms"] == 1.23
        assert "ts" in rec and "trace_id" in rec

