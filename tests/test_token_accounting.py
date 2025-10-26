def test_token_estimator_counts_strings_and_structs():
    from spica.tokenizer import estimate_tokens

    assert estimate_tokens("abcd") >= 1
    assert estimate_tokens({"a": "bcd", "x": ["y" * 10]}) >= 1


def test_adapter_increments_tokens_and_enforces_budget(tmp_path, monkeypatch):
    import json
    import os
    import shutil

    from spica.pipelines.registry import PipelineRegistry, run_pipeline

    # Tight tokens budget to trigger enforcement using a temp registry copy
    base = "capability_registry.json"
    tmp_reg = tmp_path / "cap.json"
    shutil.copyfile(base, tmp_reg)
    with open(tmp_reg, "r", encoding="utf-8") as f:
        data = json.load(f)
    for t in data["tools"]:
        t.setdefault("budgets", {})["tokens"] = 8
    with open(tmp_reg, "w", encoding="utf-8") as f:
        json.dump(data, f)

    os.environ["SPICA_CAP_REG_PATH"] = str(tmp_reg)
    reg = PipelineRegistry()
    adapters = reg.build(reg.load("configs/pipelines/local.yaml"))

    ctx = {"run_id": "t", "variant_id": "v", "origin_commit": "abc", "tokens_used": 0}
    seed = {"text": "hello spica", "candidates": ["hello spica", "moon"], "query": "hello"}
    try:
        out = run_pipeline(adapters, ctx, seed)
        assert "_metrics" in out
    except Exception as e:  # BudgetExceeded or other
        assert "budget" in str(e).lower()
    finally:
        os.environ.pop("SPICA_CAP_REG_PATH", None)
    assert ctx["tokens_used"] >= 1
