"""
Prometheus metrics for Glimpse performance monitoring.
"""

from typing import Optional, Dict, Any
import time
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from prometheus_client.core import REGISTRY
from prometheus_client.exposition import default_handler
import logging

logger = logging.getLogger(__name__)

# Disable default metrics (we'll only use our custom ones)
REGISTRY.unregister(REGISTRY._names_to_collectors["python_gc_objects_collected_total"])

# OpenAI API Metrics
OPENAI_REQUESTS = Counter(
    "openai_requests_total",
    "Total number of OpenAI API requests",
    ["endpoint", "status_code", "model"],
)

OPENAI_REQUEST_DURATION = Histogram(
    "openai_request_duration_seconds",
    "OpenAI API request duration in seconds",
    ["endpoint", "model"],
    buckets=(
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
        15.0,
        20.0,
        30.0,
        60.0,
        float("inf"),
    ),
)

OPENAI_TOKENS = Counter(
    "openai_tokens_total",
    "Total number of tokens processed by OpenAI API",
    ["type", "model"],
)

# Cache Metrics
CACHE_HITS = Counter("prompt_cache_hits_total", "Total number of cache hits")
CACHE_MISSES = Counter("prompt_cache_misses_total", "Total number of cache misses")
CACHE_SIZE = Gauge("prompt_cache_size", "Current number of items in the cache")

# Glimpse Glimpse Metrics
GLIMPSE_ATTEMPTS = Counter(
    "glimpse_attempts_total",
    "Total number of glimpse attempts",
    ["attempt_number", "status"],
)

GLIMPSE_ATTEMPT_DURATION = Histogram(
    "glimpse_attempt_duration_seconds",
    "Duration of glimpse attempts in seconds",
    ["attempt_number"],
    buckets=(
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
        15.0,
        30.0,
        60.0,
        float("inf"),
    ),
)

# Rate Limiting Metrics
RATE_LIMIT_DELAYS = Counter(
    "rate_limit_delays_total",
    "Total number of times requests were delayed due to rate limiting",
    ["endpoint"],
)

RATE_LIMIT_REJECTED = Counter(
    "rate_limit_rejected_total",
    "Total number of requests rejected due to rate limiting",
    ["endpoint"],
)

RATE_LIMIT_RATE = Gauge(
    "rate_limit_requests_per_minute",
    "Current allowed requests per minute",
    ["endpoint"],
)

RATE_LIMIT_TOKENS_AVAILABLE = Gauge(
    "rate_limit_tokens_available",
    "Number of tokens currently available in the rate limiter bucket",
    ["endpoint"],
)

RATE_LIMIT_BUCKET_CAPACITY = Gauge(
    "rate_limit_bucket_capacity",
    "Current capacity of the rate limiter bucket",
    ["endpoint"],
)

RATE_LIMIT_ADJUSTMENTS = Counter(
    "rate_limit_adjustments_total",
    "Total number of rate limit adjustments",
    ["direction"],
)

RATE_LIMIT_WAIT_TIME = Histogram(
    "rate_limit_wait_seconds",
    "Time spent waiting for rate limiting",
    ["endpoint"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, float("inf")),
)


def record_openai_request(
    endpoint: str, model: str, duration: float, status_code: int = 200
) -> None:
    """Record metrics for an OpenAI API request."""
    status = "success" if 200 <= status_code < 300 else "error"
    OPENAI_REQUESTS.labels(
        endpoint=endpoint, status_code=status_code, model=model
    ).inc()
    OPENAI_REQUEST_DURATION.labels(endpoint=endpoint, model=model).observe(duration)


def record_openai_tokens(
    prompt_tokens: int, completion_tokens: int, model: str
) -> None:
    """Record token usage for an OpenAI API request."""
    if prompt_tokens > 0:
        OPENAI_TOKENS.labels(type="input", model=model).inc(prompt_tokens)
    if completion_tokens > 0:
        OPENAI_TOKENS.labels(type="output", model=model).inc(completion_tokens)


def record_cache_hit() -> None:
    """Record a cache hit."""
    CACHE_HITS.inc()


def record_cache_miss() -> None:
    """Record a cache miss."""
    CACHE_MISSES.inc()


def update_cache_size(size: int) -> None:
    """Update the current cache size."""
    CACHE_SIZE.set(size)


def record_glimpse_attempt(
    attempt_number: int, duration: float, status: str = "success"
) -> None:
    """Record metrics for a glimpse attempt."""
    GLIMPSE_ATTEMPTS.labels(attempt_number=attempt_number, status=status).inc()
    GLIMPSE_ATTEMPT_DURATION.labels(attempt_number=attempt_number).observe(duration)


def record_rate_limit_delay(endpoint: str = "default") -> None:
    """Record that a request was delayed due to rate limiting."""
    RATE_LIMIT_DELAYS.labels(endpoint=endpoint).inc()


def record_rate_limit_rejection(endpoint: str = "default") -> None:
    """Record that a request was rejected due to rate limiting."""
    RATE_LIMIT_REJECTED.labels(endpoint=endpoint).inc()


def record_rate_limit_adjustment(
    old_rate: float, new_rate: float, success_rate: float, endpoint: str = "default"
) -> None:
    """Record a rate limit adjustment."""
    direction = "increase" if new_rate > old_rate else "decrease"
    RATE_LIMIT_ADJUSTMENTS.labels(direction=direction).inc()

    # Update current rate metrics
    RATE_LIMIT_RATE.labels(endpoint=endpoint).set(new_rate)

    logger.debug(
        f"Rate limit adjusted: {old_rate:.1f} -> {new_rate:.1f} RPM "
        f"(success rate: {success_rate:.1%})"
    )


def record_rate_limit_metrics(
    endpoint: str,
    tokens_available: float,
    bucket_capacity: float,
    requests_per_minute: float,
) -> None:
    """Record current rate limiter metrics."""
    RATE_LIMIT_TOKENS_AVAILABLE.labels(endpoint=endpoint).set(tokens_available)
    RATE_LIMIT_BUCKET_CAPACITY.labels(endpoint=endpoint).set(bucket_capacity)
    RATE_LIMIT_RATE.labels(endpoint=endpoint).set(requests_per_minute)


def record_rate_limit_wait_time(wait_time: float, endpoint: str = "default") -> None:
    """Record time spent waiting for rate limiting."""
    RATE_LIMIT_WAIT_TIME.labels(endpoint=endpoint).observe(wait_time)


def get_metrics() -> bytes:
    """Return the current metrics in Prometheus text format."""
    return generate_latest(REGISTRY)
