from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class CellManifest:
    name: str
    version: str = "0.1.0"
    inputs: List[str] = None
    outputs: List[str] = None
    risk_class: str = "low"


class ContractError(Exception): ...


def validate_manifest(m: Dict[str, Any]) -> CellManifest:
    req = ["name", "version"]
    missing = [k for k in req if k not in m]
    if missing:
        raise ContractError(f"Missing: {missing}")
    return CellManifest(
        name=m["name"],
        version=m["version"],
        inputs=m.get("inputs", []),
        outputs=m.get("outputs", []),
        risk_class=m.get("governance", {}).get("risk_class", "low"),
    )
