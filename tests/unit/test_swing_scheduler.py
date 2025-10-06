# tests/unit/test_swing_scheduler.py
"""
Unit tests for swing_scheduler.py
"""

import pytest
from app.harmony.swing_scheduler import SamplerState


def test_sampler_state_initialization():
    """Test SamplerState initializes correctly."""
    state = SamplerState(profile="swing_default")
    assert state.profile == "swing_default"
    assert state.precision == "Q8"
    assert state.mode == "grid"
    assert state.direction == "forward"


def test_next_params_basic():
    """Test next_params returns valid parameters."""
    state = SamplerState()
    params = state.next_params(0)
    assert "temperature" in params
    assert "top_p" in params
    assert "repetition_penalty" in params
    assert "frequency_penalty" in params
    assert 0.2 <= params["temperature"] <= 1.2
    assert 0.5 <= params["top_p"] <= 0.98


def test_flip_event():
    """Test flip on event."""
    state = SamplerState()
    initial_precision = state.precision
    initial_mode = state.mode
    params = state.next_params(0, event=True)
    assert state.precision != initial_precision or state.mode != initial_mode


def test_swing_variation():
    """Test swing and variation are applied."""
    state = SamplerState()
    params1 = state.next_params(0)
    params2 = state.next_params(4)  # Different token for swing
    # Should have some variation due to swing
    assert params1["temperature"] != params2["temperature"] or params1["top_p"] != params2["top_p"]
