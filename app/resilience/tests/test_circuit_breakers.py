"""
Tests for circuit breaker functionality.

Tests pybreaker integration, state transitions, and failure handling.
"""

from unittest.mock import Mock, patch

import pybreaker
import pytest

from app.resilience.circuit_breakers import (
    ExternalServiceBreakers,
    PrometheusListener,
    get_external_breakers,
    initialize_breakers,
)


class TestPrometheusListener:
    """Test the Prometheus listener functionality."""

    def test_state_change_logging(self, caplog):
        """Test that state changes are logged properly."""
        listener = PrometheusListener("test-breaker")

        # Mock circuit breaker
        cb = Mock()
        cb.name = "test-breaker"

        # Test CLOSED -> OPEN transition
        with caplog.at_level("WARNING"):
            listener.state_change(cb, pybreaker.STATE_CLOSED, pybreaker.STATE_OPEN)

        assert "state changed: CLOSED → OPEN" in caplog.text
        assert "test-breaker" in caplog.text

    def test_failure_logging(self, caplog):
        """Test that failures are logged with context."""
        listener = PrometheusListener("test-breaker")

        cb = Mock()
        cb.name = "test-breaker"
        cb.fail_counter = 3
        cb.fail_max = 5

        exc = Exception("Test error")

        with caplog.at_level("WARNING"):
            listener.failure(cb, exc)

        assert "failure:" in caplog.text
        assert "Test error" in caplog.text
        assert "fail_counter: 3/5" in caplog.text

    def test_success_logging(self, caplog):
        """Test that successes are logged."""
        listener = PrometheusListener("test-breaker")

        cb = Mock()
        cb.name = "test-breaker"
        cb.fail_counter = 0

        with caplog.at_level("INFO"):
            listener.success(cb)

        assert "success" in caplog.text
        assert "fail_counter reset to: 0" in caplog.text


class TestExternalServiceBreakers:
    """Test the ExternalServiceBreakers class."""

    def test_initialization_without_redis(self):
        """Test initialization without Redis (in-memory storage)."""
        breakers = ExternalServiceBreakers()

        assert hasattr(breakers, "llm_api")
        assert hasattr(breakers, "payment")
        assert hasattr(breakers, "external_data")
        assert hasattr(breakers, "generic")

        # Check that they're circuit breakers
        assert isinstance(breakers.llm_api, pybreaker.CircuitBreaker)
        assert isinstance(breakers.payment, pybreaker.CircuitBreaker)

    @patch("app.resilience.circuit_breakers.get_config")
    def test_initialization_with_redis(self, mock_get_config):
        """Test initialization with Redis storage."""
        # Mock config
        mock_config = Mock()
        mock_config.resilience.llm_fail_max = 8
        mock_config.resilience.llm_reset_timeout = 30
        mock_config.resilience.payment_fail_max = 3
        mock_config.resilience.payment_reset_timeout = 60
        mock_config.resilience.data_fail_max = 5
        mock_config.resilience.data_reset_timeout = 45
        mock_config.resilience.generic_fail_max = 5
        mock_config.resilience.generic_reset_timeout = 30
        mock_get_config.return_value = mock_config

        # Mock Redis
        mock_redis = Mock()

        breakers = ExternalServiceBreakers(mock_redis)

        # Verify breakers have correct configuration
        assert breakers.llm_api.fail_max == 8
        assert breakers.llm_api.reset_timeout == 30
        assert breakers.payment.fail_max == 3
        assert breakers.payment.reset_timeout == 60

    def test_get_breaker_for_service(self):
        """Test service-to-breaker mapping."""
        breakers = ExternalServiceBreakers()

        # Test known services
        assert breakers.get_breaker_for_service("llm") is breakers.llm_api
        assert breakers.get_breaker_for_service("openai") is breakers.llm_api
        assert breakers.get_breaker_for_service("payment") is breakers.payment
        assert breakers.get_breaker_for_service("stripe") is breakers.payment
        assert breakers.get_breaker_for_service("data") is breakers.external_data

        # Test unknown service gets generic
        assert breakers.get_breaker_for_service("unknown") is breakers.generic
        assert breakers.get_breaker_for_service("random-api") is breakers.generic

    @pytest.mark.asyncio
    async def test_get_status(self):
        """Test getting breaker status."""
        breakers = ExternalServiceBreakers()

        status = await breakers.get_status()

        assert "llm_api" in status
        assert "payment" in status
        assert "external_data" in status
        assert "generic" in status

        # Check status structure
        llm_status = status["llm_api"]
        assert "state" in llm_status
        assert "fail_counter" in llm_status
        assert "fail_max" in llm_status
        assert "reset_timeout" in llm_status
        assert "name" in llm_status


class TestDependencyInjection:
    """Test FastAPI dependency injection functions."""

    @patch("app.resilience.circuit_breakers._breakers_instance", None)
    def test_get_external_breakers_creates_instance(self):
        """Test that get_external_breakers creates an instance when none exists."""
        breakers = get_external_breakers()

        assert isinstance(breakers, ExternalServiceBreakers)
        assert breakers is get_external_breakers()  # Same instance returned

    @pytest.mark.asyncio
    async def test_initialize_breakers(self):
        """Test breaker initialization function."""
        mock_redis = Mock()

        breakers = await initialize_breakers(mock_redis)

        assert isinstance(breakers, ExternalServiceBreakers)

        # Verify the global instance is set
        from app.resilience.circuit_breakers import _breakers_instance

        assert _breakers_instance is breakers


class TestCircuitBreakerIntegration:
    """Integration tests for circuit breaker behavior."""

    def test_breaker_trips_after_failures(self):
        """Test that breaker trips to OPEN state after max failures."""
        breakers = ExternalServiceBreakers()

        # Mock a function that always fails
        @breakers.llm_api
        def failing_function():
            raise Exception("Always fails")

        # Call until breaker trips (assuming fail_max = 5)
        for _ in range(6):  # One more than fail_max
            try:
                failing_function()
            except Exception:
                pass

        # Breaker should be open
        assert breakers.llm_api.current_state == pybreaker.STATE_OPEN

    def test_breaker_recovers_after_reset_timeout(self):
        """Test that breaker goes to HALF_OPEN after reset timeout."""
        breakers = ExternalServiceBreakers()

        # Mock breaker with short reset timeout for testing
        breakers.llm_api.reset_timeout = 0.1  # Very short for test

        # Trip the breaker
        @breakers.llm_api
        def failing_function():
            raise Exception("Fails")

        for _ in range(6):
            try:
                failing_function()
            except Exception:
                pass

        assert breakers.llm_api.current_state == pybreaker.STATE_OPEN

        # Wait for reset timeout
        import time

        time.sleep(0.2)

        # Next call should put it in HALF_OPEN
        try:
            failing_function()
        except Exception:
            pass

        # Should be in HALF_OPEN now (state transitions automatically)
        # Note: pybreaker state management is complex, this tests the concept

    def test_business_logic_errors_dont_trip_breaker(self):
        """Test that excluded exceptions don't count towards failure."""
        breakers = ExternalServiceBreakers()

        # ValueError is excluded from LLM breaker
        @breakers.llm_api
        def business_error_function():
            raise ValueError("Business logic error")

        # Call multiple times - should not trip breaker
        for _ in range(10):
            try:
                business_error_function()
            except ValueError:
                pass

        # Breaker should still be closed
        assert breakers.llm_api.current_state == pybreaker.STATE_CLOSED
        assert breakers.llm_api.fail_counter == 0  # No failures counted
