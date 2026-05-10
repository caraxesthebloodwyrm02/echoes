"""Tests for ParallelSimulationEngine outcome prediction."""

import pytest

from core_modules.parallel_simulation_engine import ParallelSimulationEngine, SimulationType


@pytest.fixture()
def engine() -> ParallelSimulationEngine:
    eng = ParallelSimulationEngine()
    yield eng
    eng.shutdown()


def test_outcome_prediction_returns_structured_outcomes(engine: ParallelSimulationEngine) -> None:
    action = "deploy the worker service"
    configs = [
        {
            "type": SimulationType.OUTCOME_PREDICTION,
            "input_data": {"action": action, "context": {}},
            "parameters": {},
        }
    ]
    results = engine.run_parallel_simulations(configs)
    assert len(results) == 1
    outcome = results[0].outcome
    predicted = outcome.get("predicted_outcomes") or []
    assert len(predicted) == 3
    assert outcome.get("most_likely", {}).get("type") == "success"
    assert outcome.get("risk_assessment") == "medium"
