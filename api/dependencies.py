from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from api.config import get_config
from app.resilience.circuit_breakers import (
    ExternalServiceBreakers,
    get_external_breakers,
)


async def get_redis() -> Redis | None:
    """Provide Redis client if configured."""
    config = get_config()
    if config.redis.url:
        return Redis.from_url(config.redis.url)
    return None


def get_breakers(
    redis: Annotated[Redis | None, Depends(get_redis)] = None,
) -> ExternalServiceBreakers:
    """Provide circuit breakers, optionally Redis-backed."""
    breakers = get_external_breakers()
    # If Redis is provided and breakers use in-memory, re-initialize is handled at startup
    return breakers
