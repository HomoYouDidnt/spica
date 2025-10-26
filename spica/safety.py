from __future__ import annotations

from typing import Any, Dict


class SafetyViolation(Exception):
    """Raised when a hard safety gate is violated (e.g., persona drift)."""


def kl_persona(context: Dict[str, Any]) -> float:
    """
    Placeholder KL computation for persona drift. In this stub, we expect callers
    to optionally place a numeric override at context["kl_persona"]. Defaults to 0.0.
    """
    try:
        return float(context.get("kl_persona", 0.0))
    except Exception:
        return 0.0


def kl_task(context: Dict[str, Any]) -> float:
    """
    Placeholder KL computation for task drift. In this stub, we expect callers
    to optionally place a numeric override at context["kl_task"]. Defaults to 0.0.
    """
    try:
        return float(context.get("kl_task", 0.0))
    except Exception:
        return 0.0
