# AGENTS.md (snippets Codex can use)

## spica_adapter (goal)
Implement/modify the SPICA Cell Adapter and ensure cell contracts pass validation.

**Key files:** `spica/cell_adapter.py`, `spica/contracts.py`, `tests/test_cells.py`  
**Constraints:** API stable; no network; do not rename public fns without tests.  
**Run:** `Tasks: lint`, `Tasks: test`

## pipeline_variation (goal)
Add a variation operator that mutates decoding params and swaps nodes in a 2-cell pipeline.

**Key files:** `spica/variation/operators.py`, `spica/pipelines/registry.py`, `tests/test_variation.py`  
**Emit:** metrics, preserve governance tags.
