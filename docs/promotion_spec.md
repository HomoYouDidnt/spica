% Promotion Spec (SPICA → KLoROS)

## Niche: QA / RAG

**Primary KPIs**
- `answer_accuracy@1` — semantic match of final answer to gold label.
- `tool_success_rate` — share of tool calls with `status == "ok"`.

**Secondary KPIs**
- `latency_p95` — 95th percentile per-conversation end-to-end latency (shadow replay).
- `fail_rate` — exceptions/timeouts per conversation.

**Guardrails**
- `KL_persona ≤ 0.02` (hard gate)
- `KL_task ≤ 0.08` (soft penalty; log and include in fitness)

**Promotion Thresholds**
1) **Offline Replay (Gate 2)**
   - Δ`answer_accuracy@1` ≥ **+2.5%** vs baseline
   - 95% CI for delta **excludes 0**
   - `latency_p95` not worse than **+10%**
2) **Shadow Live (Gate 3)**
   - Retain ≥ **80%** of offline delta over ≥ **1,000** conversations
   - `KL_persona` stays ≤ 0.02 in rolling windows
3) **Canary (Gate 4)**
   - Sequential test confirms uplift
   - No guardrail breaches

**Datasets**
- **Gold shard**: fixed, versioned (adversarial + long tail)
- **Fresh shard**: last 7–14 days, stratified by domain/length/difficulty

