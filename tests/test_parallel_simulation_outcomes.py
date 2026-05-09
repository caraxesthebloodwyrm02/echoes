"""Integration tests: empirical prediction meta + outcome feedback."""

from pathlib import Path

import pytest

from core_modules.parallel_simulation_engine import ParallelSimulationEngine, SimulationType


@pytest.fixture()
def isolated_engine(tmp_path: Path) -> ParallelSimulationEngine:
    log = tmp_path / "sim.jsonl"
    return ParallelSimulationEngine(outcome_log_path=log, max_jsonl_lines=500)


def test_prediction_meta_becomes_action_empirical(isolated_engine: ParallelSimulationEngine) -> None:
    action = "deploy the worker service"
    for _ in range(3):
        isolated_engine.record_outcome_feedback(action, "success")

    configs = [
        {
            "type": SimulationType.OUTCOME_PREDICTION,
            "input_data": {"action": action, "context": {}},
            "parameters": {},
        }
    ]
    results = isolated_engine.run_parallel_simulations(configs)
    assert len(results) == 1
    meta = results[0].outcome.get("prediction_meta") or {}
    assert meta.get("source") == "action_empirical"
    assert meta.get("action_samples") == 3
