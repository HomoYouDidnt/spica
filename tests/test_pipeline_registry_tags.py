from spica.pipelines.registry import PipelineRegistry, run_pipeline


def test_pipeline_registry_select_by_tag():
    reg = PipelineRegistry()
    adapters = reg.build(reg.load("configs/pipelines/tags.yaml"))

    ctx = {
        "run_id": "t",
        "variant_id": "test",
        "origin_commit": "abc",
        "tokens_used": 0,
    }
    seed = {
        "text": "hello spica",
        "candidates": ["hello spica", "goodnight moon"],
        "query": "hello",
    }
    out = run_pipeline(adapters, ctx, seed)

    assert out["text"] == "HELLO SPICA"
    assert out["selected"] == ["hello spica"]
    assert "_metrics" in out

