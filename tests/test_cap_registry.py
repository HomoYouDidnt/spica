from spica.capability_registry import CapabilityRegistry


def test_registry_resolve_uppercase():
    reg = CapabilityRegistry("capability_registry.json")
    fn, manifest, schema = reg.resolve("uppercase")
    assert callable(fn)
    assert manifest["name"] == "uppercase"
    assert "transform" in schema.tags

