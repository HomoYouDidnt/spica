import os
import time
from typing import Any, Callable, Dict, Optional

from .config import tau_task_for_domain
from .contracts import validate_manifest
from .metrics import RunMetrics, Stopwatch
from .safety import SafetyViolation, kl_persona, kl_task
from .tokenizer import estimate_tokens

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
        # choose per-domain tau_task (fallbacks internally to global/default)
        tau_t_eff = tau_task_for_domain(context.get("domain"))

        # Estimate tokens for inputs and enforce token budget by incrementing context
        in_tokens = estimate_tokens(inputs)
        tok_budget = self.budgets.get("tokens")
        if tok_budget is not None:
            used = int(context.get("tokens_used", 0))
            new_used = used + int(in_tokens)
            context["tokens_used"] = new_used
            if new_used > int(tok_budget):
                raise BudgetExceeded(
                    f"Token budget exceeded: {new_used}/{int(tok_budget)}"
                )

        t0 = time.perf_counter()
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
        # Time budget enforcement post-run
        sec_budget = self.budgets.get("sec")
        if isinstance(sec_budget, (int, float)) and sec_budget:
            elapsed_sec = time.perf_counter() - t0
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

        # Validate outputs are dict and required outputs present
        if not isinstance(out, dict):
            raise ValidationError("Cell output must be a dict")
        req_outputs = self.manifest.outputs or []
        if req_outputs:
            missing_out = [k for k in req_outputs if k not in out]
            extra_out = [k for k in out.keys() if k not in req_outputs + ["_metrics"]]
            if missing_out or extra_out:
                raise ValidationError(
                    f"Output validation failed. Missing={missing_out} Extra={extra_out}"
                )

        # Token accounting for outputs
        out_token_subset = (
            {k: out[k] for k in req_outputs}
            if req_outputs
            else {k: v for k, v in out.items() if k != "_metrics"}
        )
        out_tokens = estimate_tokens(out_token_subset)
        if tok_budget is not None:
            used = int(context.get("tokens_used", 0))
            new_used = used + int(out_tokens)
            context["tokens_used"] = new_used
            if new_used > int(tok_budget):
                raise BudgetExceeded(
                    f"Token budget exceeded: {new_used}/{int(tok_budget)}"
                )
        # fire-and-forget telemetry
        try:
            from .telemetry import log_event

            log_event(
                {
                    "variant_id": context.get("variant_id"),
                    "parent_id": context.get("parent_id"),
                    "origin_commit": context.get("origin_commit"),
                    "cell": self.manifest.name,
                    "domain": context.get("domain"),
                    "latency_ms": m.latency_ms,
                    "ok": m.ok,
                    "error": m.error,
                    "seed": context.get("seed"),
                    "kl_persona": k_persona,
                    "kl_task": k_task,
                    "tau_task": tau_t_eff,
                    "tau_persona": tau_persona,
                    "budgets_used": {
                        "tokens_used": context.get("tokens_used"),
                        "tokens_budget": self.budgets.get("tokens"),
                        "sec_budget": self.budgets.get("sec"),
                    },
                    "io_in_keys": sorted(list(inputs.keys())),
                    "io_out_keys": sorted(list(out.keys())),
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
                    "tau_persona": tau_persona,
                    "tau_task": tau_t_eff,
                    "tokens_used": context.get("tokens_used"),
                }
            )
            if isinstance(base_md, dict):
                base_md.update(md)
                merged[self.manifest.name] = base_md
            else:
                merged[self.manifest.name] = md
            out = {**out, "_metrics": merged}
        return out
