import json

from core.exporter import export_json, export_text


def test_export_text(tmp_path):
    p = tmp_path / "out.txt"
    export_text("hello", str(p))
    assert p.read_text(encoding="utf-8") == "hello"


def test_export_json(tmp_path):
    p = tmp_path / "out.json"
    data = {"a": 1}
    export_json(data, str(p))
    loaded = json.loads(p.read_text(encoding="utf-8"))
    assert loaded == data
