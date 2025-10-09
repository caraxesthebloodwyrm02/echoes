from workflows.macro import macro_parallel, merge_outputs, run_macro


def test_macro_parallel_and_merge():
    def big():
        return {"summary": "big picture"}

    def medium():
        return {"details": [1, 2, 3]}

    def fast():
        return {"draft": "ok"}

    outputs = macro_parallel(
        {
            "big": big,
            "medium": medium,
            "fast": fast,
        }
    )
    assert set(outputs.keys()) == {"big", "medium", "fast"}
    merged = merge_outputs(outputs)
    assert set(merged["layers"]) == {"big", "medium", "fast"}
    assert "results" in merged and isinstance(merged["results"], dict)


def test_run_macro():
    result = run_macro()
    assert "layers" in result
    assert "results" in result
    assert "priority_map" in result
    assert set(result["layers"]) == {"A", "B", "C", "D"}
    assert all(phase in result["results"] for phase in ["A", "B", "C", "D"])
    for phase in ["A", "B", "C", "D"]:
        assert result["results"][phase]["phase"] == phase
        assert "artifacts" in result["results"][phase]
        assert "timestamp" in result["results"][phase]


def test_run_macro_subset():
    result = run_macro("AB")
    assert set(result["layers"]) == {"A", "B"}
    assert all(phase in result["results"] for phase in ["A", "B"])
    assert "C" not in result["results"]
    assert "D" not in result["results"]
