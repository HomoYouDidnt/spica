from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, Optional

ALG = "sha256"
KEY_ENV = "SPICA_PROMOTION_KEY"  # provide secret key in CI; use dev key locally


def _now_iso() -> str:
    return (
        time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        + f".{int((time.time()%1)*1000):03d}Z"
    )


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _hmac_sign(payload_bytes: bytes, key: bytes) -> str:
    return hmac.new(key, payload_bytes, hashlib.sha256).hexdigest()


def _read_key() -> bytes:
    key = os.environ.get(KEY_ENV)
    if not key:
        # Dev-only default; override in CI via secret
        key = "DEV_ONLY_NOT_SECURE_KEY_change_me"
    return key.encode("utf-8")


def normalize(obj: Any) -> bytes:
    """Deterministic JSON serialization for signing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_promotion_unit(
    *,
    variant_id: str,
    baseline_id: str,
    pipeline_path: str,
    datasets: Dict[str, str],
    metrics_path: str,
    guardrail_report: Dict[str, Any],
    repro_script: str,
    lineage: Dict[str, str],
    env_hash: str,
    out_path: str = "promotion_unit.json",
) -> str:
    # Hash referenced artifacts
    art: Dict[str, Dict[str, Optional[str]]] = {}
    for k, p in datasets.items():
        art[k] = (
            {"path": p, "sha256": _sha256_file(p)}
            if os.path.exists(p)
            else {"path": p, "sha256": None}
        )
    if os.path.exists(metrics_path):
        art["shadow_metrics"] = {
            "path": metrics_path,
            "sha256": _sha256_file(metrics_path),
        }
    if os.path.exists(pipeline_path):
        art["pipeline"] = {"path": pipeline_path, "sha256": _sha256_file(pipeline_path)}

    unit = {
        "unit_id": f"prom_{variant_id}_{int(time.time())}",
        "ts": _now_iso(),
        "variant_id": variant_id,
        "baseline_id": baseline_id,
        "pipeline_path": pipeline_path,
        "datasets": datasets,
        "artifacts": art,
        "lineage": lineage,  # {origin_commit, parent_id, mutation_vector}
        "env_hash": env_hash,
        "repro": {"script": repro_script},
        "guards": guardrail_report,  # {kl_persona, kl_task, violations, budgets}
        "algo": ALG,
    }
    payload = normalize(unit)
    sig = _hmac_sign(payload, _read_key())
    signed = {**unit, "signature": sig}

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(signed, f, ensure_ascii=False, indent=2)
    return out_path


def verify_promotion_unit(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    sig = obj.get("signature")
    if not sig:
        return False
    payload = dict(obj)
    payload.pop("signature", None)
    calc = _hmac_sign(normalize(payload), _read_key())
    # Constant-time compare
    return hmac.compare_digest(sig, calc)
