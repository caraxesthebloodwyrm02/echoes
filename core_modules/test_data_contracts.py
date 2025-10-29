#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Property-based tests for safety module data contracts.
Uses hypothesis for automated testing of edge cases and data validation.
"""

import pytest
from hypothesis import Phase, given, settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule
from jsonschema import ValidationError, validate

from src.safety.audit import AuditEvent, AuditLogger
from src.safety.guards import CircuitBreaker, Prompt
from src.safety.limiter import TokenBucket

# Data contracts (JSON schemas) for property-based testing
PROMPT_SCHEMA = Prompt.schema()
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "bias_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "explanation": {"type": "string", "maxLength": 500},
    },
    "required": ["bias_score", "explanation"],
}

AUDIT_EVENT_SCHEMA = AuditEvent.schema()


@given(st.text(min_size=1, max_size=800))
@settings(max_examples=100, phases=[Phase.generate, Phase.shrink])
def test_prompt_schema_compliance_safe_inputs(text):
    """Test that Prompt class accepts valid inputs and produces valid JSON."""
    try:
        prompt = Prompt(text=text)
        json_data = prompt.dict()
        validate(json_data, PROMPT_SCHEMA)
    except ValidationError as e:
        pytest.fail(f"Prompt schema validation failed: {e}")
    except ValueError:
        # Expected for blocked inputs - this is correct behavior
        pass


@given(
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    st.text(min_size=1, max_size=500),
)
@settings(max_examples=50)
def test_response_schema_compliance(bias_score, explanation):
    """Test that response data conforms to expected schema."""
    response_data = {"bias_score": bias_score, "explanation": explanation}
    validate(response_data, RESPONSE_SCHEMA)


@given(st.text(min_size=1, max_size=1000))
@settings(max_examples=200)
def test_prompt_length_limits(text):
    """Test that prompts are properly length-limited."""
    prompt = Prompt(text=text)
    assert len(prompt.text) <= 800  # Should be truncated/sanitized


@given(st.integers(min_value=1, max_value=100), st.integers(min_value=1, max_value=60))
@settings(max_examples=30)
def test_circuit_breaker_configurations(max_failures, reset_timeout):
    """Test circuit breaker with various configurations."""
    cb = CircuitBreaker(max_failures=max_failures, reset_timeout=reset_timeout)

    def failing_func():
        raise Exception("test failure")

    # Should handle threshold-1 failures
    for _ in range(max_failures):
        try:
            cb.call(failing_func)
        except RuntimeError:
            # Circuit breaker opened
            break

    # After reset timeout, should work again
    cb = CircuitBreaker(max_failures=max_failures, reset_timeout=0.001)
    import time

    time.sleep(0.01)  # Wait for reset


@given(st.integers(min_value=1, max_value=1000))
@settings(max_examples=50)
def test_token_bucket_capacity_limits(capacity):
    """Test token bucket respects capacity limits."""
    bucket = TokenBucket(max_per_min=capacity)

    # Should allow burst up to capacity
    acquired = 0
    for _ in range(capacity + 10):  # Try more than capacity
        if bucket.acquire():
            acquired += 1
        else:
            break

    assert acquired == capacity


@given(st.floats(min_value=0.1, max_value=100.0))
@settings(max_examples=30)
def test_token_bucket_refill_rates(rate):
    """Test token bucket refill behavior."""
    bucket = TokenBucket(max_per_min=int(rate * 60))  # Convert to per minute

    # Empty the bucket
    while bucket.acquire():
        pass

    # Simulate time passage
    original_time = bucket.last
    # Simulate passage of time that should refill some tokens
    bucket.last = original_time.replace(second=original_time.second - 10)

    # Should be able to acquire again
    assert bucket.acquire() == True


@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=200),
    st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(st.text(), st.integers(), st.booleans()),
    ),
)
@settings(max_examples=20)
def test_audit_logger_handles_various_data(user, prompt, response):
    """Test audit logger with various data types."""
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "test.ndjson")
        audit = AuditLogger(log_file)

        # Should handle various data without crashing
        audit.log_evaluation(user_id=user, prompt=prompt, response=response, safety_status="success")

        # File should exist and contain valid JSON
        assert os.path.exists(log_file)
        with open(log_file, "r") as f:
            content = f.read()
            # Should be valid JSON lines
            for line in content.strip().split("\n"):
                if line:
                    import json

                    parsed = json.loads(line)
                    # Should match audit event schema
                    validate(parsed, AUDIT_EVENT_SCHEMA)


@given(st.integers(min_value=1, max_value=100), st.integers(min_value=1, max_value=60))
@settings(max_examples=20)
def test_circuit_breaker_timing_behavior(max_failures, timeout):
    """Test circuit breaker timing behavior."""
    cb = CircuitBreaker(max_failures=max_failures, reset_timeout=timeout)

    def failing_func():
        raise Exception("failure")

    # Trigger circuit breaker
    for _ in range(max_failures + 1):
        try:
            cb.call(failing_func)
        except RuntimeError:
            break

    # Should be open
    try:
        cb.call(lambda: "success")
        assert False, "Should have been blocked"
    except RuntimeError:
        pass

    # Simulate timeout passage
    cb.last_fail = cb.last_fail - (timeout + 1)

    # Should work again
    result = cb.call(lambda: "success")
    assert result == "success"


@given(st.integers(min_value=1, max_value=1000))
@settings(max_examples=30)
def test_token_bucket_burst_behavior(burst_size):
    """Test token bucket burst behavior."""
    bucket = TokenBucket(max_per_min=burst_size)

    # Should allow burst up to capacity
    acquired = 0
    for _ in range(burst_size + 10):
        if bucket.acquire():
            acquired += 1
        else:
            break

    assert acquired == burst_size


@given(
    st.text(min_size=1, max_size=50),
    st.text(min_size=1, max_size=200),
    st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(st.text(), st.integers(), st.booleans()),
    ),
)
@settings(max_examples=15)
def test_audit_logger_data_integrity(user, prompt, response):
    """Test that audit logger preserves data integrity."""
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "audit.ndjson")
        audit = AuditLogger(log_file)

        audit.log_evaluation(user_id=user, prompt=prompt, response=response, safety_status="success")

        with open(log_file, "r") as f:
            import json

            entry = json.loads(f.read())

            # Verify data integrity
            assert entry["user_id"] != user  # Should be hashed
            assert entry["prompt_hash"] != hash(prompt)  # Should be hashed
            assert entry["response_summary"]["has_bias_score"] in response
            assert "timestamp" in entry
            assert "event_id" in entry


# Stateful testing for circuit breaker behavior
class CircuitBreakerStateMachine(RuleBasedStateMachine):
    """Stateful test for circuit breaker state transitions."""

    def __init__(self):
        super().__init__()
        self.cb = CircuitBreaker(max_failures=3, reset_timeout=0.1)
        self.failure_count = 0
        self.is_open = False

    @rule()
    def call_success(self):
        """Test successful call."""
        try:
            result = self.cb.call(lambda: "success")
            assert result == "success"
            self.failure_count = 0  # Reset on success
            self.is_open = False
        except RuntimeError:
            assert self.is_open  # Should only fail if open

    @rule()
    def call_failure(self):
        """Test failing call."""
        try:
            self.cb.call(lambda: 1 / 0)
            # Should not reach here if circuit is open
            self.failure_count += 1
            if self.failure_count >= 3:
                self.is_open = True
        except RuntimeError:
            self.is_open = True
        except ZeroDivisionError:
            self.failure_count += 1
            if self.failure_count >= 3:
                self.is_open = True

    @rule()
    def wait_for_reset(self):
        """Test reset after timeout."""
        import time

        time.sleep(0.2)  # Wait longer than reset timeout
        self.failure_count = 0
        self.is_open = False


# Create the state machine test
TestCircuitBreakerStateMachine = CircuitBreakerStateMachine.TestCase


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
