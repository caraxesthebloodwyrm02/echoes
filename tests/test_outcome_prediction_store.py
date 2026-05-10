"""Tests for outcome log aggregation and empirical probabilities."""

from pathlib import Path

import pytest

from core_modules.outcome_prediction_store import (
    DEFAULT_PRIOR,
    MIN_ACTION_SAMPLES,
    OutcomePredictionStore,
    canonical_outcome_label,
    normalize_action_key,
)


def test_normalize_action_key() -> None:
    assert normalize_action_key("  Hello   World ") == "hello world"
    assert normalize_action_key("") == "_empty"


def test_canonical_outcome_label() -> None:
    assert canonical_outcome_label("partial") == "partial_success"
    assert canonical_outcome_label("fail") == "failure"
    with pytest.raises(ValueError):
        canonical_outcome_label("maybe")


def test_default_prior_when_empty_log(tmp_path: Path) -> None:
    store = OutcomePredictionStore(log_path=tmp_path / "empty.jsonl")
    emp = store.empirical_probabilities("ship the feature")
    assert emp.source == "default_prior"
    assert emp.probs == DEFAULT_PRIOR


def test_action_empirical_when_enough_samples(tmp_path: Path) -> None:
    p = tmp_path / "o.jsonl"
    store = OutcomePredictionStore(log_path=p)
    key = normalize_action_key("same action")
    for _ in range(MIN_ACTION_SAMPLES):
        store.append_feedback(key, "success")
    emp = store.empirical_probabilities("same action")
    assert emp.source == "action_empirical"
    assert emp.probs["success"] == pytest.approx(1.0)
    assert emp.action_samples == MIN_ACTION_SAMPLES


def test_prediction_rows_have_recorded_at(tmp_path: Path) -> None:
    path = tmp_path / "x.jsonl"
    store = OutcomePredictionStore(log_path=path)
    store.append_feedback(normalize_action_key("a"), "failure")
    text = path.read_text(encoding="utf-8")
    assert "recorded_at" in text
    assert "feedback" in text


def test_jsonl_trim_keeps_last_lines(tmp_path: Path) -> None:
    path = tmp_path / "trim.jsonl"
    store = OutcomePredictionStore(log_path=path, max_jsonl_lines=5)
    for i in range(8):
        store.append_feedback(normalize_action_key(f"action-{i}"), "success")
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 5
    assert "action-7" in lines[-1]
