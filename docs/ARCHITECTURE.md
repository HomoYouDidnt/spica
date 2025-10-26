# 🧠 SPICA Architecture Overview

A Safe Self-Evolving Cognitive Framework for D-REAM

## 1️⃣ Purpose

SPICA (Self-Promoting Isolated Cognitive Architecture) is a sandbox for cognitive evolution — a disposable testbed where D-REAM can safely mutate and evaluate new reasoning or planning strategies without destabilizing production KLoROS.
Every variant lives in isolation, reports telemetry, and can be promoted only through signed, evidence-based gates.

## 2️⃣ High-Level Flow
```
   ┌──────────────┐
   │ Capability    │
   │  Registry     │
   └──────┬────────┘
          │
          ▼
┌────────────────────┐
│ Pipeline Registry   │ ← YAML-defined step sequence
│  (name/tag select)  │
└──────┬──────────────┘
       │  builds
       ▼
┌────────────────────┐
│ Cell Adapter       │ ← runs each cell
│  + Metrics & KL    │
└──────┬──────────────┘
       │  emits
       ▼
┌────────────────────┐
│ Telemetry & Safety │ ← JSONL trace, budgets, tau
└──────┬──────────────┘
       │  feeds
       ▼
┌────────────────────┐
│ Shadow Runner      │ ← replay evaluation on gold/fresh logs
└──────┬──────────────┘
       │  outputs
       ▼
┌────────────────────┐
│ Promotion Builder  │ ← signed evidence bundle
└──────┬──────────────┘
       │  verified by
       ▼
┌────────────────────┐
│ CI Guard Workflow  │ ← label `promotion` required
└────────────────────┘
```

## 3️⃣ Core Modules

### 🧩 `spica/capability_registry.py`
Central directory of tools/cells. Each entry defines:
- callable (function path)
- schema (input/output names)
- tags (for tag-based selection)
- budgets (sec/tokens)

Used by: pipelines, adapters, and tests. Override with `SPICA_CAP_REG_PATH`.

### 🧠 `spica/cell_adapter.py`
Executes one “cell” in the pipeline:
- Validates typed I/O
- Tracks latency, tokens, budgets
- Computes `KL_persona` and `KL_task` (per-domain τ_t supported)
- Logs telemetry (with `tau_persona`, per-domain `tau_task`)
- Raises `SafetyViolation` or `BudgetExceeded` on breach

### 📊 `spica/metrics.py`
`RunMetrics` dataclass for latency, success flags, and error tracking. Aggregates metrics per cell and merges them into pipeline context.

### 🔒 `spica/safety.py`
KL drift calculators and `SafetyViolation` logic.
- Persona drift = hard stop
- Task drift = soft penalty in fitness
- Thresholds (τ_p, τ_t) from env; τ_t supports per-domain overrides

### ⚙️ `spica/config.py`
Per-domain configuration helpers, e.g. `tau_task_for_domain(domain)`
resolves in order:
1) `SPICA_TAU_TASK__<DOMAIN_UPPER_WITH_UNDERSCORES>`
2) `SPICA_TAU_TASK`
3) default `0.08`

### 📚 `spica/pipelines/registry.py`
Builds executable pipelines from YAML:
- Supports `name:` or `select_by_tag:` for each step
- Instantiates `CellAdapter`s with budgets, safety, telemetry wired in

### 📡 `spica/telemetry.py`
Thread-safe JSONL logger:
- Fields: `trace_id`, `variant_id`, `domain`, `latency_ms`, `kl_persona`, `kl_task`, etc.
- Default file: `spica.telemetry.jsonl` (override with `SPICA_TELEMETRY_PATH`)

### 🧮 `spica/tokenizer.py`
Lightweight character→token estimator. Ensures token budgets are enforced even without a model tokenizer.

### 🧭 `tools/shadow_runner.py`
Offline evaluator:
- Replays sanitized JSONL logs through the pipeline
- Computes `answer_accuracy@1`, `tool_success_rate`, `latency_p95_ms`
- Supports bootstrap Δ metrics and 95% confidence intervals vs baseline

### 🪶 `tools/build_promotion_unit.py` + `spica/promotions.py`
Builds an HMAC-signed `promotion_unit.json` containing:
- Dataset hashes
- Replay deltas + confidence intervals
- Guardrail report (KL, violations)
- Repro script hash

CI verifies signatures using the secret `SPICA_PROMOTION_KEY`.

### 🧩 `tools/queue_runner.py`
Priority scheduler:
- Runs eval > explore jobs under a time budget
- `submit_shadow_job` → single replay
- `submit_dual_shadow_jobs` → gold + fresh

Foundation for tournament orchestration.

### 🔄 `tools/kill_switch.py`
Ops-safe pipeline pointer switch:
- `--activate` → sets `current.yaml` to promoted pipeline
- `--deactivate` → restores baseline

### ⚙️ CI / Guardrails — `.github/workflows/promotion-guard.yml`
- Triggered on PRs labeled `promotion`
- Requires valid signed `promotion_unit.json`
- Uses `SPICA_PROMOTION_KEY` from repo secrets

## 4️⃣ Developer Experience (VS Code Tasks)

| Task                          | Action                                      |
|-------------------------------|---------------------------------------------|
| `validate`                    | ruff, black, pytest                          |
| `run demo`                    | quick pipeline sanity                        |
| `shadow (sample)`             | run replay on sanitized logs                 |
| `baseline (gold)`             | generate stable baseline                     |
| `queue: baseline+fresh`       | schedule gold + fresh replays                |
| `promotion: build (sample)`   | sign evidence bundle                         |
| `promotion: candidate (queue)`| full flow — queue replays → build bundle     |
| `pipeline: activate / rollback`| switch promoted vs baseline pipeline        |

## 5️⃣ Safety & Governance

- Isolation: Each SPICA variant runs standalone, never touching KLoROS’s state
- Evidence-Based Promotion: All changes require signed metrics + guardrails
- Auditability: Every run produces structured telemetry
- Rollback: Single command to revert to baseline

## 6️⃣ Next Evolution Steps

- Automated tournament ranking of SPICA variants via QueueRunner batches
- Integration with D-REAM’s genetic search (mutation → fitness → promotion)
- Optional small-model fine-tuning via nanochat backends
- Visualization dashboard (real-time telemetry / drift plots)

---

### Summary

SPICA provides safe cognitive evolution through reproducible experiments, measurable performance, and automated promotion gates.
It bridges research autonomy and production safety, letting KLoROS explore new reasoning architectures under controlled, fully auditable conditions.

