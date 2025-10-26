import os
from typing import Any, Callable, Dict, Optional

from .contracts import validate_manifest
from .metrics import RunMetrics, Stopwatch
from .safety import SafetyViolation, kl_persona, kl_task

MetricsSink = Optional[Callable[[str, Dict[str, Any]], None]]


class BudgetExceeded(Exception):
    pass


class ValidationError(Exception):
    pass


class CellAdapter:
    def __init__(
        self,
        cell_impl,
        manifest: Dict[str, Any],
        metrics_sink: MetricsSink = None,
        budgets: Optional[Dict[str, Any]] = None,
    ):
        self.manifest = validate_manifest(manifest)
        self.impl = cell_impl
        self.metrics_sink = metrics_sink
        self.last_metrics: Optional[RunMetrics] = None
        self.budgets = budgets or {}

    def run(self, context: Dict[str, Any], **inputs):
        # Typed I/O: validate input names
        req_inputs = self.manifest.inputs or []
        if req_inputs:
            missing = [k for k in req_inputs if k not in inputs]
            extra = [k for k in inputs.keys() if k not in req_inputs]
            if missing or extra:
                raise ValidationError(
                    f"Input validation failed. Missing={missing} Extra={extra}"
                )

        # Safety thresholds from env
        tau_persona = float(os.environ.get("SPICA_TAU_PERSONA", 0.02))
        tau_task = float(os.environ.get("SPICA_TAU_TASK", 0.08))

        # Token budget (pre-check) using a stub increment from context
        tokens_budget = self.budgets.get("tokens")
        if tokens_budget is not None and "tokens_used" in context:
            inc = int(context.get("tokens_inc", 0))
            if context["tokens_used"] + inc > int(tokens_budget):
                raise BudgetExceeded("Token budget exceeded")

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
        # Compute safety
        k_persona = kl_persona(context)
        k_task = kl_task(context)
        if k_persona > tau_persona:
            try:
                from .telemetry import log_event

                log_event(
                    {
                        "cell": self.manifest.name,
                        "event": "persona_gate_breach",
                        "kl_persona": k_persona,
                        "tau_persona": tau_persona,
                    }
                )
            except Exception:
                pass
            raise SafetyViolation(
                f"Persona KL {k_persona:.4f} exceeds tau {tau_persona:.4f}"
            )

        # Time budget enforcement
        sec_budget = self.budgets.get("sec")
        if isinstance(sec_budget, (int, float)):
            elapsed_sec = (getattr(sw, "elapsed_ms", 0.0) or 0.0) / 1000.0
            if elapsed_sec > float(sec_budget):
                try:
                    from .telemetry import log_event

                    log_event(
                        {
                            "cell": self.manifest.name,
                            "event": "time_budget_exceeded",
                            "elapsed_sec": elapsed_sec,
                            "sec_budget": float(sec_budget),
                        }
                    )
                except Exception:
                    pass
                raise BudgetExceeded(
                    f"Time budget exceeded: {elapsed_sec:.3f}s > {float(sec_budget):.3f}s"
                )

        # Token budget update after run
        if tokens_budget is not None and "tokens_used" in context:
            inc = int(context.get("tokens_inc", 0))
            context["tokens_used"] += inc
        # fire-and-forget telemetry
        try:
            from .telemetry import log_event

            log_event(
                {
                    "variant_id": context.get("variant_id"),
                    "parent_id": context.get("parent_id"),
                    "origin_commit": context.get("origin_commit"),
                    "cell": self.manifest.name,
                    "latency_ms": m.latency_ms,
                    "ok": m.ok,
                    "error": m.error,
                    "kl_persona": k_persona,
                    "kl_task": k_task,
                    "tau_task": tau_task,
                    "budgets_used": {
                        "sec": (getattr(sw, "elapsed_ms", 0.0) or 0.0) / 1000.0,
                        "tokens": context.get("tokens_used"),
                    },
                }
            )
        except Exception:
            pass
        if isinstance(out, dict):
            merged: Dict[str, Any] = {}
            if isinstance(context.get("_metrics"), dict):
                merged.update(context.get("_metrics"))
            # always refresh this cell's metrics with extended fields
            base_md = merged.get(self.manifest.name, {})
            md = m.to_dict()
            md.update(
                {
                    "kl_persona": k_persona,
                    "kl_task": k_task,
                    "tau_task": tau_task,
                    "budgets_used": {
                        "sec": (getattr(sw, "elapsed_ms", 0.0) or 0.0) / 1000.0,
                        "tokens": context.get("tokens_used"),
                    },
                }
            )
            if isinstance(base_md, dict):
                base_md.update(md)
                merged[self.manifest.name] = base_md
            else:
                merged[self.manifest.name] = md
            # validate outputs names
            req_outputs = self.manifest.outputs or []
            if req_outputs:
                missing_out = [k for k in req_outputs if k not in out]
                extra_out = [
                    k for k in out.keys() if k not in req_outputs + ["_metrics"]
                ]
                if missing_out or extra_out:
                    raise ValidationError(
                        f"Output validation failed. Missing={missing_out} Extra={extra_out}"
                    )
            out = {**out, "_metrics": merged}
        return out
