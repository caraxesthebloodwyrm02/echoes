"""
Health check task for automation framework.
Verifies core functionality and endpoint availability.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from app.main import app
from fastapi.testclient import TestClient

logger = logging.getLogger(__name__)


async def run_health_check() -> Dict[str, Any]:
    """
    Comprehensive health check of the automation framework.
    Tests API endpoints and core functionality.
    """
    client = TestClient(app)
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {},
        "status": "operational",
    }

    # Test endpoints
    try:
        # Root endpoint check
        root_response = client.get("/")
        results["checks"]["root"] = {
            "status": "ok" if root_response.status_code == 200 else "error",
            "automation_status": root_response.json()
            .get("automation", {})
            .get("status"),
        }

        # Tasks list check
        tasks_response = client.get("/api/automation/tasks")
        results["checks"]["tasks_endpoint"] = {
            "status": "ok" if tasks_response.status_code == 200 else "error",
            "available_tasks": len(
                tasks_response.json() if tasks_response.status_code == 200 else []
            ),
        }

        # Health endpoint check
        health_response = client.get("/api/automation/health")
        results["checks"]["health_endpoint"] = {
            "status": "ok" if health_response.status_code == 200 else "error",
            "details": (
                health_response.json() if health_response.status_code == 200 else None
            ),
        }

        # Test task execution
        test_task_response = client.post("/api/automation/tasks/health_check/run")
        results["checks"]["task_execution"] = {
            "status": "ok" if test_task_response.status_code in [200, 202] else "error",
            "response_code": test_task_response.status_code,
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        results["status"] = "degraded"
        results["error"] = str(e)

    return results
