"""
Resilience package for FastAPI applications.

Provides production-grade resilience patterns including:
- Inbound rate limiting with SlowApi + Redis
- Outbound retry logic with tenacity + jitter
- Circuit breaker patterns with pybreaker
- Prometheus metrics and observability

Follows AGENTS.md architecture guidelines for 429 handling.
"""

from .circuit_breakers import ExternalServiceBreakers, PrometheusListener
from .rate_limit import setup_rate_limiting
from .retry_utils import resilient_http_call, retry_config

__all__ = [
    "ExternalServiceBreakers",
    "PrometheusListener",
    "setup_rate_limiting",
    "resilient_http_call",
    "retry_config",
]
