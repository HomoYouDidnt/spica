from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class RunMetrics:
    latency_ms: float
    ok: bool
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Stopwatch:
    def __enter__(self):
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed_ms = (time.perf_counter() - self._t0) * 1000.0
