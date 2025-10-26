from tools.shadow_runner import evaluate_file


def test_shadow_runner_evaluate_file_works():
    res = evaluate_file(
        "configs/pipelines/local.yaml",
        "samples/sanitized.qarg.jsonl",
        baseline_metrics_path=None,
        limit=100,
    )
    assert res["n"] >= 2
    assert "answer_accuracy@1" in res and "latency_p95_ms" in res
    assert "per_conv" in res and isinstance(res["per_conv"], list)

