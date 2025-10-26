import json

from spica.promotions import build_promotion_unit, verify_promotion_unit


def test_build_and_verify_promotion_unit_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("SPICA_PROMOTION_KEY", "TEST_KEY")

    gold = tmp_path / "gold.jsonl"
    gold.write_text('{"a":1}\n', encoding="utf-8")
    fresh = tmp_path / "fresh.jsonl"
    fresh.write_text('{"b":2}\n', encoding="utf-8")
    pipeline = tmp_path / "pipe.yaml"
    pipeline.write_text("steps: []\n", encoding="utf-8")
    metrics = tmp_path / "metrics.json"
    metrics.write_text('{"answer_accuracy@1": 0.5, "per_conv": []}', encoding="utf-8")

    outp = tmp_path / "promotion_unit.json"
    build_promotion_unit(
        variant_id="spica_X",
        baseline_id="prod_2025-10-20",
        pipeline_path=str(pipeline),
        datasets={"gold": str(gold), "fresh": str(fresh)},
        metrics_path=str(metrics),
        guardrail_report={"kl_persona": 0.01, "kl_task": 0.04, "violations": 0},
        repro_script="tools/shadow_runner.py",
        lineage={"origin_commit": "abc", "parent_id": "", "mutation_vector": []},
        env_hash="env123",
        out_path=str(outp),
    )

    assert outp.exists()
    obj = json.loads(outp.read_text(encoding="utf-8"))
    assert "signature" in obj

    ok = verify_promotion_unit(str(outp))
    assert ok is True


def test_verify_fails_on_tamper(tmp_path, monkeypatch):
    monkeypatch.setenv("SPICA_PROMOTION_KEY", "TEST_KEY")
    p = tmp_path / "unit.json"
    p.write_text(json.dumps({"unit_id": "x", "signature": "deadbeef"}), encoding="utf-8")
    assert verify_promotion_unit(str(p)) is False

