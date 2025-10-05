"""
Async API Tests

Tests using async clients for FastAPI endpoints.
"""

import sys
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

sys.path.insert(0, "../app")

from api.routes.system import router

app = FastAPI()
app.include_router(router, prefix="/api")


@pytest.mark.asyncio
async def test_agent_execute_async():
    """Test async agent execution."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "agent_id": "async-agent-001",
            "action": "no_op",
            "params": {},
            "dry_run": True,
        }

        response = await ac.post("/api/agent/execute", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["dry_run"] is True
        assert data["success"] is True


@pytest.mark.asyncio
async def test_validate_assertion_async():
    """Test async assertion validation."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "claim": "Async test claim",
            "provenance": [
                {
                    "source": "TestSource",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

        response = await ac.post("/api/assertions/validate", json=payload)

        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_hil_feedback_async():
    """Test async HIL feedback submission."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "assertion_id": "async-assert-001",
            "label": "helpful",
        }

        response = await ac.post("/api/hil/feedback", json=payload)

        assert response.status_code == 202
        assert response.json()["status"] == "queued"


@pytest.mark.asyncio
async def test_health_check_async():
    """Test async health check."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_metrics_async():
    """Test async metrics retrieval."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "provenance_coverage" in data


@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test handling multiple concurrent requests."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create multiple concurrent requests
        tasks = []
        for i in range(10):
            payload = {
                "agent_id": f"concurrent-agent-{i}",
                "action": "no_op",
                "params": {"index": i},
            }
            tasks.append(ac.post("/api/agent/execute", json=payload))

        # Execute concurrently
        import asyncio

        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 200
            assert response.json()["dry_run"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
