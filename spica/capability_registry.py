from __future__ import annotations

import importlib
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

REG_PATH_ENV = "SPICA_CAP_REG_PATH"


@dataclass
class ToolSchema:
    name: str
    module: str
    entry: str = "run"
    manifest_attr: str = "MANIFEST"
    tags: tuple[str, ...] = ()
    risk_class: str = "low"
    budgets: Dict[str, Any] = None


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class CapabilityRegistry:
    def __init__(self, path: Optional[str] = None):
        self.path = path or os.environ.get(REG_PATH_ENV) or "capability_registry.json"
        self._raw = _load_json(self.path)
        self._tools = {
            t["name"]: ToolSchema(
                name=t["name"],
                module=t["module"],
                entry=t.get("entry", "run"),
                manifest_attr=t.get("manifest_attr", "MANIFEST"),
                tags=tuple(t.get("tags", [])),
                risk_class=t.get("risk_class", "low"),
                budgets=t.get("budgets", {}),
            )
            for t in self._raw.get("tools", [])
        }

    def list(self, tag_filter: Optional[set[str]] = None) -> list[str]:
        if not tag_filter:
            return list(self._tools.keys())
        return [n for n, s in self._tools.items() if tag_filter & set(s.tags)]

    def resolve(self, name: str):
        s = self._tools[name]
        mod = importlib.import_module(s.module)
        fn = getattr(mod, s.entry)
        manifest = getattr(mod, s.manifest_attr)
        return fn, manifest, s
