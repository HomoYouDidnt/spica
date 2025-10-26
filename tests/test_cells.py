def test_echo_cell_smoke():
    from spica.cell_adapter import CellAdapter
    from spica.cells.echo import MANIFEST, run

    c = CellAdapter(run, MANIFEST)
    out = c.run({"run_id": "t"}, text="ok")
    assert out["text"] == "ok"


def test_uppercase_then_echo_pipeline_metrics():
    from spica.cell_adapter import CellAdapter
    from spica.cells.echo import MANIFEST as M_ECHO
    from spica.cells.echo import run as run_echo
    from spica.cells.uppercase import MANIFEST as M_UP
    from spica.cells.uppercase import run as run_upper

    metrics_log = {}

    def sink(name, mdict):
        metrics_log[name] = mdict

    upper = CellAdapter(run_upper, M_UP, metrics_sink=sink)
    echo = CellAdapter(run_echo, M_ECHO, metrics_sink=sink)

    ctx = {"run_id": "t"}
    out1 = upper.run(ctx, text="hello spica")
    out2 = echo.run(ctx, **{"text": out1["text"]})

    assert out2["text"] == "HELLO SPICA"
    assert "uppercase" in out2["_metrics"]
    assert "uppercase" in metrics_log
    assert metrics_log["uppercase"]["ok"] is True
    assert metrics_log["uppercase"]["latency_ms"] >= 0.0
