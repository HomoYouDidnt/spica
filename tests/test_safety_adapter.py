import os
import time

import pytest


def test_persona_breach_raises():
    from spica.cell_adapter import CellAdapter
    from spica.cells.echo import MANIFEST
    from spica.safety import SafetyViolation

    def ok_cell(context, text: str):
        return {"text": text}

    os.environ["SPICA_TAU_PERSONA"] = "0.02"
    try:
        c = CellAdapter(ok_cell, MANIFEST)
        with pytest.raises(SafetyViolation):
            c.run({"run_id": "t", "kl_persona": 0.5}, text="hi")
    finally:
        os.environ.pop("SPICA_TAU_PERSONA", None)


def test_task_drift_logged_not_raised():
    from spica.cell_adapter import CellAdapter
    from spica.cells.echo import MANIFEST

    def ok_cell(context, text: str):
        return {"text": text}

    os.environ["SPICA_TAU_TASK"] = "0.01"
    try:
        c = CellAdapter(ok_cell, MANIFEST)
        out = c.run({"run_id": "t", "kl_task": 0.5}, text="hello")
        assert out["text"] == "hello"
        # drift reflected in metrics bundle
        m = out["_metrics"]["echo"]
        assert m["kl_task"] >= 0.5
    finally:
        os.environ.pop("SPICA_TAU_TASK", None)


def test_time_budget_exceeded():
    from spica.cell_adapter import BudgetExceeded, CellAdapter
    from spica.cells.echo import MANIFEST

    def slow_cell(context, text: str):
        time.sleep(0.02)
        return {"text": text}

    c = CellAdapter(slow_cell, MANIFEST, budgets={"sec": 0.005})
    with pytest.raises(BudgetExceeded):
        c.run({"run_id": "t"}, text="hi")


def test_io_mismatch_raises():
    from spica.cell_adapter import CellAdapter, ValidationError
    from spica.cells.echo import MANIFEST

    def ok_cell(context, text: str):
        return {"text": text}

    c = CellAdapter(ok_cell, MANIFEST)
    with pytest.raises(ValidationError):
        c.run({"run_id": "t"}, wrong_name="hi")

