def test_echo_cell_smoke():
    from spica.cell_adapter import CellAdapter
    from spica.cells.echo import MANIFEST, run

    c = CellAdapter(run, MANIFEST)
    out = c.run({"run_id": "t"}, text="ok")
    assert out["text"] == "ok"
