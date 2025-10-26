import json

from tools.queue_runner import QueueRunner, submit_dual_shadow_jobs


def test_dual_shadow_jobs_write_outputs(tmp_path):
    gold_out = tmp_path / "baseline.shadow.metrics.json"
    fresh_out = tmp_path / "shadow.metrics.json"
    q = QueueRunner()
    submit_dual_shadow_jobs(
        q,
        pipeline="configs/pipelines/local.yaml",
        gold_input="samples/gold.qarg.jsonl",
        fresh_input="samples/sanitized.qarg.jsonl",
        gold_out=str(gold_out),
        fresh_out=str(fresh_out),
        gold_limit=50,
        fresh_limit=50,
    )
    q.run(budget_s=90.0)
    assert gold_out.exists() and fresh_out.exists()
    g = json.loads(gold_out.read_text(encoding="utf-8"))
    f = json.loads(fresh_out.read_text(encoding="utf-8"))
    assert "answer_accuracy@1" in g and "answer_accuracy@1" in f

