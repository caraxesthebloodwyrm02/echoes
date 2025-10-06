# tests/unit/test_diff_core.py
from app.harmony.diff_service import diff


def test_simple_add_remove():
    a = {"x": 1}
    b = {"x": 1, "y": 2}
    out = diff(a, b)
    assert any(d["path"] == "y" for d in out["added"])
    assert out["metrics"]["added_count"] == 1


def test_value_change_with_epsilon():
    a = {"n": 1.0}
    b = {"n": 1.0001}
    out = diff(a, b, {"epsilon": 0.001})
    assert out["metrics"]["modified_count"] == 0


def test_list_index_changes():
    a = {"l": [1, 2, 3]}
    b = {"l": [1, 4]}
    out = diff(a, b)
    # index 1 changed, index 2 removed
    assert any("[1]" in m["path"] for m in out["modified"])
    assert any("[2]" in r["path"] for r in out["removed"]) 
