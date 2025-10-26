import json

from tools.queue_runner import QueueRunner, submit_shadow_job


def test_submit_shadow_job_runs_and_writes(tmp_path):
    outp = tmp_path / "shadow.out.json"
    pipeline = "configs/pipelines/local.yaml"
    inputp = "samples/sanitized.qarg.jsonl"

    r = QueueRunner()
    submit_shadow_job(
        r,
        name="eval:shadow@sample",
        pipeline=pipeline,
        input_path=inputp,
        out_path=str(outp),
        limit=10,
        priority=10,
    )
    r.run(budget_s=30.0)
    assert outp.exists()
    data = json.loads(outp.read_text(encoding="utf-8"))
    assert "answer_accuracy@1" in data and "n" in data

