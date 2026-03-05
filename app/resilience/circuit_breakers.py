"""
Circuit breaker implementation for external API calls using pybreaker.

Provides distributed circuit breakers with Redis storage and Prometheus metrics.
Follows AGENTS.md architecture guidelines for 429 handling.
"""

import logging
from typing import Any

import pybreaker
from redis.asyncio import Redis

from api.config import get_config

logger = logging.getLogger(__name__)


class PrometheusListener(pybreaker.CircuitBreakerListener):
    """
    Circuit breaker listener that provides Prometheus metrics and structured logging.

    Tracks state changes, failure counts, and recovery events for observability.
    """

    def __init__(self, breaker_name: str):
        self.breaker_name = breaker_name
        # In a real implementation, you would initialize Prometheus gauges/counters here
        # self.state_gauge = Gauge(f'circuit_breaker_state', 'Circuit breaker state', ['name'])
        # self.failure_counter = Counter(f'circuit_breaker_failures', 'Circuit breaker failures', ['name'])

    def state_change(
        self, cb: pybreaker.CircuitBreaker, old_state: int, new_state: int
    ) -> None:
        """Called when circuit breaker state changes."""
        state_names = {
            pybreaker.STATE_CLOSED: "CLOSED",
            pybreaker.STATE_OPEN: "OPEN",
            pybreaker.STATE_HALF_OPEN: "HALF_OPEN",
        }

        old_name = state_names.get(old_state, f"UNKNOWN({old_state})")
        new_name = state_names.get(new_state, f"UNKNOWN({new_state})")

        logger.warning(
            f"Circuit breaker '{cb.name}' state changed: {old_name} → {new_name} "
            f"(failures: {cb.fail_counter}, reset_timeout: {cb.reset_timeout}s)"
        )

        # Update Prometheus metrics
        # self.state_gauge.labels(name=cb.name).set(new_state)

    def failure(self, cb: pybreaker.CircuitBreaker, exc: Exception) -> None:
        """Called when a call fails."""
        logger.warning(
            f"Circuit breaker '{cb.name}' failure: {type(exc).__name__}: {exc} "
            f"(fail_counter: {cb.fail_counter}/{cb.fail_max})"
        )

        # Increment Prometheus failure counter
        # self.failure_counter.labels(name=cb.name).inc()

    def success(self, cb: pybreaker.CircuitBreaker) -> None:
        """Called when a call succeeds."""
        logger.info(
            f"Circuit breaker '{cb.name}' success "
            f"(fail_counter reset to: {cb.fail_counter})"
        )


class ExternalServiceBreakers:
    """
    Collection of circuit breakers for external services.

    Each external API should have its own circuit breaker with appropriate
    failure thresholds based on the service's SLA and reliability characteristics.
    """

    def __init__(self, redis_client: Redis | None = None):
        """
        Initialize circuit breakers with Redis storage for distributed state.

        Args:
            redis_client: Redis client for distributed storage. If None, uses in-memory storage.
        """
        config = get_config()

        # Use Redis storage if available, otherwise in-memory
        if redis_client:
            storage = pybreaker.CircuitRedisStorage(
                pybreaker.STATE_CLOSED, redis_client
            )
            logger.info("Circuit breakers using Redis storage for distributed state")
        else:
            storage = pybreaker.CircuitMemoryStorage(pybreaker.STATE_CLOSED)
            logger.warning(
                "Circuit breakers using in-memory storage - not suitable for production"
            )

        # LLM API breaker - higher tolerance for flaky AI services
        self.llm_api = pybreaker.CircuitBreaker(
            fail_max=config.resilience.llm_fail_max,  # e.g., 8 failures
            reset_timeout=config.resilience.llm_reset_timeout,  # e.g., 30 seconds
            state_storage=storage,
            name="external-llm",
            exclude=[ValueError, TypeError],  # Don't trip on business logic errors
            listeners=[PrometheusListener("external-llm")],
        )

        # Payment service breaker - stricter for financial operations
        self.payment = pybreaker.CircuitBreaker(
            fail_max=config.resilience.payment_fail_max,  # e.g., 3 failures
            reset_timeout=config.resilience.payment_reset_timeout,  # e.g., 60 seconds
            state_storage=storage,
            name="payment-service",
            exclude=[ValueError],  # Don't trip on validation errors
            listeners=[PrometheusListener("payment-service")],
        )

        # External data API breaker - moderate tolerance
        self.external_data = pybreaker.CircuitBreaker(
            fail_max=config.resilience.data_fail_max,  # e.g., 5 failures
            reset_timeout=config.resilience.data_reset_timeout,  # e.g., 45 seconds
            state_storage=storage,
            name="external-data",
            exclude=[ValueError, KeyError],  # Don't trip on data parsing errors
            listeners=[PrometheusListener("external-data")],
        )

        # Generic breaker for unknown external services
        self.generic = pybreaker.CircuitBreaker(
            fail_max=config.resilience.generic_fail_max,  # e.g., 5 failures
            reset_timeout=config.resilience.generic_reset_timeout,  # e.g., 30 seconds
            state_storage=storage,
            name="generic-external",
            listeners=[PrometheusListener("generic-external")],
        )

        logger.info("External service circuit breakers initialized")
        logger.info(
            f"LLM breaker: {self.llm_api.fail_max} fails, {self.llm_api.reset_timeout}s reset"
        )
        logger.info(
            f"Payment breaker: {self.payment.fail_max} fails, {self.payment.reset_timeout}s reset"
        )
        logger.info(
            f"Data breaker: {self.external_data.fail_max} fails, {self.external_data.reset_timeout}s reset"
        )

    def get_breaker_for_service(self, service_name: str) -> pybreaker.CircuitBreaker:
        """
        Get the appropriate circuit breaker for a service.

        Args:
            service_name: Name of the external service

        Returns:
            CircuitBreaker instance for the service
        """
        service_breakers = {
            "llm": self.llm_api,
            "openai": self.llm_api,
            "anthropic": self.llm_api,
            "groq": self.llm_api,
            "gemini": self.llm_api,
            "payment": self.payment,
            "stripe": self.payment,
            "data": self.external_data,
            "api": self.external_data,
        }

        return service_breakers.get(service_name.lower(), self.generic)

    async def get_status(self) -> dict[str, dict[str, Any]]:
        """
        Get status of all circuit breakers for monitoring.

        Returns:
            Dict with breaker names and their current status
        """
        status = {}
        for name, breaker in [
            ("llm_api", self.llm_api),
            ("payment", self.payment),
            ("external_data", self.external_data),
            ("generic", self.generic),
        ]:
            status[name] = {
                "state": breaker.current_state,
                "fail_counter": breaker.fail_counter,
                "fail_max": breaker.fail_max,
                "reset_timeout": breaker.reset_timeout,
                "name": breaker.name,
            }

        return status


# Global breaker instance - will be initialized in dependencies
_breakers_instance: ExternalServiceBreakers | None = None


def get_external_breakers() -> ExternalServiceBreakers:
    """Dependency injection function for FastAPI."""
    global _breakers_instance
    if _breakers_instance is None:
        # This would typically be initialized with Redis in production
        _breakers_instance = ExternalServiceBreakers()
    return _breakers_instance


async def initialize_breakers(
    redis_client: Redis | None = None,
) -> ExternalServiceBreakers:
    """
    Initialize circuit breakers with Redis client.

    Call this during app startup to ensure proper Redis integration.
    """
    global _breakers_instance
    _breakers_instance = ExternalServiceBreakers(redis_client)
    return _breakers_instance
