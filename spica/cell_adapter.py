from typing import Any, Dict

from .contracts import ContractError, validate_manifest


class CellAdapter:
    def __init__(self, cell_impl, manifest: Dict[str, Any]):
        self.manifest = validate_manifest(manifest)
        self.impl = cell_impl

    def run(self, context: Dict[str, Any], **inputs):
        # Optional: enforce input names from manifest
        return self.impl(context=context, **inputs)

