from __future__ import annotations

import json
import os
import threading
import time
import uuid
from typing import Any, Dict, Optional

PATH_ENV = "SPICA_TELEMETRY_PATH"
_lock = threading.Lock()


def _now_iso() -> str:
    return (
        time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        + f".{int((time.time()%1)*1000):03d}Z"
    )


def log_event(event: Dict[str, Any], path: Optional[str] = None) -> None:
    out = dict(event)
    out.setdefault("ts", _now_iso())
    out.setdefault("trace_id", uuid.uuid4().hex[:12])
    fp = path or os.environ.get(PATH_ENV) or "spica.telemetry.jsonl"
    line = json.dumps(out, ensure_ascii=False)
    with _lock:
        with open(fp, "a", encoding="utf-8") as f:
            f.write(line + "\n")
