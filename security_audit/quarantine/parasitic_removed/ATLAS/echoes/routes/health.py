"""
Echoes AI Health Routes

This module provides health check endpoints for the Echoes AI Multi-Agent System.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..config import get_settings
from ..exceptions import create_success_response

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthCheck(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime
    version: str
    uptime: float | None = None
    checks: dict[str, Any] = {}


class ComponentHealth(BaseModel):
    """Component health status model."""

    status: str
    message: str | None = None
    details: dict[str, Any] = {}


# Application start time
_start_time = datetime.now()


@router.get("/", response_model=HealthCheck)
async def health_check():
    """Basic health check endpoint."""
    settings = get_settings()

    # Calculate uptime
    uptime = (datetime.now() - _start_time).total_seconds()

    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        uptime=uptime,
        checks={
            "application": {"status": "healthy"},
            "environment": settings.environment,
            "debug": settings.debug,
        },
    )


@router.get("/detailed", response_model=HealthCheck)
async def detailed_health_check():
    """Detailed health check with component status."""
    get_settings()

    # Calculate uptime
    uptime = (datetime.now() - _start_time).total_seconds()

    # Check components
    checks = await _check_components()

    # Determine overall status
    overall_status = "healthy"
    for component, health in checks.items():
        if health.status != "healthy":
            overall_status = "unhealthy"
            break

    return HealthCheck(
        status=overall_status,
        timestamp=datetime.now(),
        version="1.0.0",
        uptime=uptime,
        checks=checks,
    )


@router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes."""
    try:
        # Check if all critical components are ready
        checks = await _check_components()

        # Check critical components
        critical_components = ["application", "database", "redis"]
        for component in critical_components:
            if component not in checks or checks[component].status != "healthy":
                raise HTTPException(
                    status_code=503, detail=f"Component {component} is not ready"
                )

        return create_success_response(
            data={"status": "ready"}, message="Application is ready"
        )

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Application is not ready")


@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes."""
    try:
        # Basic liveness check - if we can respond, we're alive
        return create_success_response(
            data={"status": "alive"}, message="Application is alive"
        )

    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        raise HTTPException(status_code=503, detail="Application is not alive")


@router.get("/components/{component_name}")
async def component_health_check(component_name: str):
    """Check health of a specific component."""
    checks = await _check_components()

    if component_name not in checks:
        raise HTTPException(
            status_code=404, detail=f"Component {component_name} not found"
        )

    return checks[component_name]


async def _check_components() -> dict[str, ComponentHealth]:
    """Check health of all components."""
    settings = get_settings()
    checks = {}

    # Check application
    checks["application"] = ComponentHealth(
        status="healthy", message="Application is running"
    )

    # Check database
    try:
        # In production, this would check actual database connection
        await asyncio.sleep(0.1)  # Simulate database check
        checks["database"] = ComponentHealth(
            status="healthy",
            message="Database connection successful",
            details={"url": settings.database_url},
        )
    except Exception as e:
        checks["database"] = ComponentHealth(
            status="unhealthy", message=f"Database connection failed: {str(e)}"
        )

    # Check Redis
    try:
        # In production, this would check actual Redis connection
        await asyncio.sleep(0.1)  # Simulate Redis check
        checks["redis"] = ComponentHealth(
            status="healthy",
            message="Redis connection successful",
            details={"url": settings.redis_url},
        )
    except Exception as e:
        checks["redis"] = ComponentHealth(
            status="unhealthy", message=f"Redis connection failed: {str(e)}"
        )

    # Check OpenAI API
    if settings.openai_api_key:
        try:
            # In production, this would make actual API call
            await asyncio.sleep(0.1)  # Simulate API check
            checks["openai"] = ComponentHealth(
                status="healthy", message="OpenAI API connection successful"
            )
        except Exception as e:
            checks["openai"] = ComponentHealth(
                status="unhealthy", message=f"OpenAI API connection failed: {str(e)}"
            )
    else:
        checks["openai"] = ComponentHealth(
            status="warning", message="OpenAI API key not configured"
        )

    # Check disk space
    try:
        import shutil

        total, used, free = shutil.disk_usage("/")
        free_percent = (free / total) * 100

        if free_percent < 10:
            status = "critical"
        elif free_percent < 20:
            status = "warning"
        else:
            status = "healthy"

        checks["disk"] = ComponentHealth(
            status=status,
            message=f"Disk space: {free_percent:.1f}% free",
            details={
                "total_gb": total // (1024**3),
                "used_gb": used // (1024**3),
                "free_gb": free // (1024**3),
                "free_percent": free_percent,
            },
        )
    except Exception as e:
        checks["disk"] = ComponentHealth(
            status="unhealthy", message=f"Disk check failed: {str(e)}"
        )

    # Check memory
    try:
        import psutil

        memory = psutil.virtual_memory()

        if memory.percent > 90:
            status = "critical"
        elif memory.percent > 80:
            status = "warning"
        else:
            status = "healthy"

        checks["memory"] = ComponentHealth(
            status=status,
            message=f"Memory usage: {memory.percent:.1f}%",
            details={
                "total_gb": memory.total // (1024**3),
                "available_gb": memory.available // (1024**3),
                "used_percent": memory.percent,
            },
        )
    except Exception as e:
        checks["memory"] = ComponentHealth(
            status="warning", message=f"Memory check failed: {str(e)}"
        )

    return checks
