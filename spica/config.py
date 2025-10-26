from __future__ import annotations

import os
from typing import Optional

_DEFAULT_TAU_TASK = 0.08


def tau_task_for_domain(domain: Optional[str]) -> float:
    """
    Resolve per-domain task-KL threshold:
      1) Env override: SPICA_TAU_TASK__<DOMAIN_UPPER> (dots -> underscores)
      2) Fallback env: SPICA_TAU_TASK
      3) Default 0.08
    """
    if domain:
        key = "SPICA_TAU_TASK__" + domain.upper().replace(".", "_")
        if key in os.environ:
            try:
                return float(os.environ[key])
            except Exception:
                pass
    try:
        return float(os.environ.get("SPICA_TAU_TASK", _DEFAULT_TAU_TASK))
    except Exception:
        return _DEFAULT_TAU_TASK
