def test_echo_cell_smoke():
    from spica.cells.echo import MANIFEST, run
    from spica.cell_adapter import CellAdapter

    c = CellAdapter(run, MANIFEST)
    out = c.run({"run_id": "t"}, text="ok")
    assert out["text"] == "ok"

