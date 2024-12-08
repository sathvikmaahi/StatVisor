from backend.app.tools import TOOL_SCHEMAS, build_bar_chart_spec, compute_basic_stats


def test_compute_basic_stats():
    stats = compute_basic_stats([1.0, 2.0, 3.0])
    assert stats["mean"] == 2.0
    assert stats["median"] == 2.0
    assert stats["stdev"] > 0


def test_build_bar_chart_spec():
    spec = build_bar_chart_spec("Demo", ["a", "b"], [1, 2])
    assert spec["type"] == "bar"
    assert spec["data"]["labels"] == ["a", "b"]


def test_tool_schemas_present():
    names = {t["function"]["name"] for t in TOOL_SCHEMAS}
    assert "compute_basic_stats" in names
    assert "build_bar_chart_spec" in names
