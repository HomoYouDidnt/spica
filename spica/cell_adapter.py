from typing import Any, Callable, Dict, Optional

from .contracts import validate_manifest
from .metrics import RunMetrics, Stopwatch

MetricsSink = Optional[Callable[[str, Dict[str, Any]], None]]


class CellAdapter:
    def __init__(
        self, cell_impl, manifest: Dict[str, Any], metrics_sink: MetricsSink = None
    ):
        self.manifest = validate_manifest(manifest)
        self.impl = cell_impl
        self.metrics_sink = metrics_sink
        self.last_metrics: Optional[RunMetrics] = None

    def run(self, context: Dict[str, Any], **inputs):
        with Stopwatch() as sw:
            try:
                out = self.impl(context=context, **inputs)
                m = RunMetrics(latency_ms=getattr(sw, "elapsed_ms", 0.0), ok=True)
            except Exception as e:
                m = RunMetrics(
                    latency_ms=getattr(sw, "elapsed_ms", 0.0), ok=False, error=repr(e)
                )
                if self.metrics_sink:
                    self.metrics_sink(self.manifest.name, m.to_dict())
                raise
        self.last_metrics = m
        # accumulate into shared context for downstream cells
        try:
            ctx_metrics = context.setdefault("_metrics", {})
            if isinstance(ctx_metrics, dict):
                ctx_metrics[self.manifest.name] = m.to_dict()
        except Exception:
            pass
        if self.metrics_sink:
            self.metrics_sink(self.manifest.name, m.to_dict())
        if isinstance(out, dict):
            merged = {}
            if isinstance(context.get("_metrics"), dict):
                merged.update(context.get("_metrics"))
            if self.manifest.name not in merged:
                merged[self.manifest.name] = m.to_dict()
            out = {**out, "_metrics": merged}
        return out
