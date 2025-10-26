# SPICA Documentation Index

This directory provides a complete reference for **KLoROS ↔ SPICA** integration, covering structure, workflows, policies, and interpretive layers.

---

## 🧠 Core Structural Knowledge
| File | Description |
|------|--------------|
| [spica_manifest.json](../spica/spica_manifest.json) | Core system topology and purpose. |
| [spica_manifest_schema.json](../spica/spica_manifest_schema.json) | Validation schema for the manifest. |
| [capability_registry_spec.md](capability_registry_spec.md) | Defines fields and semantics of capabilities. |
| [governance_policies.yaml](governance_policies.yaml) | Defines budgets, thresholds, and promotion policies. |

---

## ⚙️ Procedural Knowledge
| File | Description |
|------|--------------|
| [workflow_graph.json](workflow_graph.json) | Directed DAG describing valid action transitions. |
| [task_reference.md](task_reference.md) | Maps VS Code tasks to functional roles. |
| [artifact_contracts.yaml](artifact_contracts.yaml) | Schema for shadow metrics and promotion bundles. |
| [telemetry_fields.json](telemetry_fields.json) | Canonical telemetry fields and meanings. |

---

## 🧬 Cognitive Integration
| File | Description |
|------|--------------|
| [cell_metadata.json](cell_metadata.json) | Describes SPICA cells, domains, and goals. |
| [domain_mappings.yaml](domain_mappings.yaml) | Maps domains to evaluation criteria. |
| [fitness_criteria.md](fitness_criteria.md) | Defines success thresholds per domain. |
| [spica_experiment_api.md](spica_experiment_api.md) | API spec for registering new experiments. |
| [mutation_policy.yaml](mutation_policy.yaml) | Allowed and forbidden mutation types. |
| [spica_context_adapter.md](spica_context_adapter.md) | Protocol for KLoROS introspection ↔ SPICA runtime. |

---

## 🔐 Meta & Governance
| File | Description |
|------|--------------|
| [epistemic_contract.md](epistemic_contract.md) | Philosophical and ethical foundation. |
| [safety_manifesto.md](safety_manifesto.md) | Defines safety constraints and reversibility rules. |
| [alignment_guidelines.md](alignment_guidelines.md) | Describes alignment drift boundaries. |
| [interpretability_notes.md](interpretability_notes.md) | Notes on explainability and traceability. |

---

## 📊 Visualization & Dashboarding
| File | Description |
|------|--------------|
| [graphviz/spica_flow.dot](graphviz/spica_flow.dot) | GraphViz pipeline flow for visualization. |
| [spica_dashboard_schema.json](spica_dashboard_schema.json) | JSON schema for dashboard UI. |
| [spica_timeline.jsonl](spica_timeline.jsonl) | Sample timeline log for KLoROS event reconstruction. |

---

### 📁 Usage Order for KLoROS Ingestion

1. **Load Structural Layer:** `spica_manifest.json`, `spica_manifest_schema.json`, `governance_policies.yaml`
2. **Map Workflow Graph:** `workflow_graph.json` and `task_reference.md`
3. **Register Capabilities & Pipelines:** via `capability_registry_spec.md` and `artifact_contracts.yaml`
4. **Integrate Cognitive Context:** `cell_metadata.json`, `fitness_criteria.md`, `domain_mappings.yaml`
5. **Apply Governance & Meta Rules:** `epistemic_contract.md`, `safety_manifesto.md`
6. **Enable Visualization:** load GraphViz and dashboard schema.

---

### 🧩 Intended KLoROS Targets
| Document Type | Consumed By |
|----------------|-------------|
| Manifest / Schema | `SystemsRegistry` |
| Workflow / Tasks | `ExperimentPlanner` |
| Telemetry / Contracts | `Evaluator` |
| Policies / Governance | `GovernanceCore` |
| Cognitive / Meta | `Introspection + XAI` |
| Visualization | `DashboardAgent` |

---

**Authored for integration between D‑REAM evolutionary engine and KLoROS’ introspective agent layer.**