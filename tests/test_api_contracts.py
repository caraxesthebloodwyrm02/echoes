"""
API Contract Tests

Tests for provenance enforcement, HIL feedback, and agent safety endpoints.
"""

import sys
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, "../app")

from api.routes.system import router

# Create test app
app = FastAPI()
app.include_router(router, prefix="/api")

client = TestClient(app)


def make_provenance():
    """Helper to create valid provenance object."""
    return {
        "source": "PubMed",
        "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
        "snippet": "Study demonstrates significant reduction in symptoms",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "license": "CC-BY-4.0",
        "confidence": 0.95,
    }


class TestProvenanceValidation:
    """Tests for provenance validation endpoint."""

    def test_validate_assertion_with_provenance_succeeds(self):
        """Test that assertions with provenance pass validation."""
        payload = {
            "claim": "Treatment X reduces symptoms of disease Y",
            "provenance": [make_provenance()],
            "domain": "science",
            "confidence": 0.92,
        }

        response = client.post("/api/assertions/validate", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "validated_at" in data
        assert data["provenance_count"] == 1
        assert data["domain"] == "science"

    def test_validate_assertion_with_multiple_sources(self):
        """Test assertion with multiple provenance sources."""
        payload = {
            "claim": "Multiple studies confirm effectiveness",
            "provenance": [
                make_provenance(),
                {
                    "source": "arXiv",
                    "url": "https://arxiv.org/abs/2501.00000",
                    "snippet": "Comprehensive meta-analysis shows...",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "license": "CC-BY-SA",
                },
            ],
        }

        response = client.post("/api/assertions/validate", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["provenance_count"] == 2

    def test_validate_assertion_without_provenance_fails(self):
        """Test that assertions without provenance are rejected."""
        payload = {
            "claim": "This claim has no sources",
            "provenance": [],
        }

        response = client.post("/api/assertions/validate", json=payload)

        assert response.status_code == 400
        assert "Missing provenance" in response.json()["detail"]

    def test_validate_assertion_with_future_timestamp_fails(self):
        """Test that future timestamps are rejected."""
        future_date = datetime(2099, 12, 31, tzinfo=timezone.utc)
        payload = {
            "claim": "This has a future timestamp",
            "provenance": [
                {
                    "source": "Test",
                    "timestamp": future_date.isoformat(),
                }
            ],
        }

        response = client.post("/api/assertions/validate", json=payload)

        assert response.status_code == 400
        assert "future" in response.json()["detail"].lower()


class TestHILFeedback:
    """Tests for Human-in-the-Loop feedback endpoints."""

    def test_submit_feedback_succeeds(self):
        """Test successful feedback submission."""
        payload = {
            "assertion_id": "assert-test-001",
            "user_id": "user-123",
            "correction": "The study actually showed no significant effect",
            "label": "incorrect",
            "metadata": {"severity": "high", "domain": "science"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        response = client.post("/api/hil/feedback", json=payload)

        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "queued"
        assert data["id"] == "assert-test-001"
        assert "queue_position" in data

    def test_submit_feedback_minimal(self):
        """Test feedback with minimal required fields."""
        payload = {
            "assertion_id": "assert-test-002",
        }

        response = client.post("/api/hil/feedback", json=payload)

        assert response.status_code == 202

    def test_get_feedback_list(self):
        """Test retrieving feedback list."""
        # First submit some feedback
        for i in range(3):
            client.post(
                "/api/hil/feedback",
                json={
                    "assertion_id": f"assert-{i}",
                    "label": "helpful" if i % 2 == 0 else "incorrect",
                },
            )

        response = client.get("/api/hil/feedback?limit=10")

        assert response.status_code == 200
        data = response.json()
        assert "total_count" in data
        assert "feedback" in data
        assert isinstance(data["feedback"], list)

    def test_filter_feedback_by_label(self):
        """Test filtering feedback by label."""
        response = client.get("/api/hil/feedback?label_filter=helpful")

        assert response.status_code == 200


class TestAgentSafety:
    """Tests for agent execution and safety controls."""

    def test_agent_execute_dry_run_default(self):
        """Test that dry-run is the default mode."""
        payload = {
            "agent_id": "agent-test-001",
            "action": "search_biomedical",
            "params": {"query": "cancer immunotherapy"},
        }

        response = client.post("/api/agent/execute", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["dry_run"] is True
        assert data["success"] is True
        assert "simulated" in data["outputs"]
        assert "🔒 DRY-RUN MODE" in data["logs"][0]

    def test_agent_execute_explicit_dry_run(self):
        """Test explicit dry-run mode."""
        payload = {
            "agent_id": "agent-test-002",
            "action": "simulate_economy",
            "params": {"model": "baseline"},
            "dry_run": True,
        }

        response = client.post("/api/agent/execute", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["dry_run"] is True
        assert data["outputs"]["simulated"] is True

    def test_agent_execute_whitelisted_action(self):
        """Test execution with whitelisted action."""
        payload = {
            "agent_id": "agent-test-003",
            "action": "no_op",
            "params": {},
            "dry_run": True,
        }

        response = client.post("/api/agent/execute", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["safety_checks"]["whitelist_ok"] is True

    def test_agent_execute_non_whitelisted_action_real_mode_fails(self):
        """Test that non-whitelisted actions fail in real mode."""
        payload = {
            "agent_id": "agent-test-004",
            "action": "delete_database",  # Not whitelisted
            "params": {},
            "dry_run": False,
        }

        response = client.post("/api/agent/execute", json=payload)

        assert response.status_code == 403
        assert "not whitelisted" in response.json()["detail"]

    def test_agent_execute_includes_duration(self):
        """Test that response includes execution duration."""
        payload = {
            "agent_id": "agent-test-005",
            "action": "no_op",
            "params": {},
        }

        response = client.post("/api/agent/execute", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "duration_ms" in data
        assert data["duration_ms"] >= 0

    def test_kill_agent_succeeds(self):
        """Test kill-switch functionality."""
        # First start an agent (in dry-run for safety)
        exec_payload = {
            "agent_id": "agent-to-kill",
            "action": "no_op",
            "params": {},
            "dry_run": False,
        }
        client.post("/api/agent/execute", json=exec_payload)

        # Now kill it
        kill_payload = {
            "agent_id": "agent-to-kill",
            "reason": "test termination",
            "requested_by": "test-suite",
        }

        response = client.post("/api/agent/kill", json=kill_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "killed"
        assert data["agent_id"] == "agent-to-kill"

    def test_kill_non_existent_agent_fails(self):
        """Test killing a non-existent agent fails gracefully."""
        payload = {
            "agent_id": "non-existent-agent",
            "reason": "test",
        }

        response = client.post("/api/agent/kill", json=payload)

        assert response.status_code == 404

    def test_force_kill_agent(self):
        """Test force kill option."""
        # Start agent
        client.post(
            "/api/agent/execute",
            json={
                "agent_id": "agent-force-kill",
                "action": "no_op",
                "params": {},
                "dry_run": False,
            },
        )

        # Force kill
        response = client.post(
            "/api/agent/kill",
            json={
                "agent_id": "agent-force-kill",
                "reason": "force test",
                "force": True,
            },
        )

        assert response.status_code == 200
        assert response.json()["force"] is True

    def test_get_agent_status(self):
        """Test retrieving agent status."""
        agent_id = "agent-status-test"

        # Start agent
        client.post(
            "/api/agent/execute",
            json={
                "agent_id": agent_id,
                "action": "no_op",
                "params": {},
                "dry_run": False,
            },
        )

        # Get status
        response = client.get(f"/api/agent/status/{agent_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == agent_id
        assert "status" in data


class TestSystemEndpoints:
    """Tests for system health and metrics endpoints."""

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded", "down"]
        assert "version" in data
        assert "components" in data
        assert "timestamp" in data

    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        response = client.get("/api/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "total_assertions" in data
        assert "provenance_coverage" in data
        assert "hil_feedback_count" in data
        assert "agent_executions" in data
        assert "dry_run_percentage" in data

        # Validate ranges
        assert 0 <= data["provenance_coverage"] <= 1
        assert 0 <= data["dry_run_percentage"] <= 1


class TestSchemaValidation:
    """Tests for Pydantic schema validation."""

    def test_provenance_schema_validation(self):
        """Test provenance schema requires source and timestamp."""
        from api.routes.system import Provenance

        # Valid provenance
        prov = Provenance(source="PubMed", timestamp=datetime.now(timezone.utc))
        assert prov.source == "PubMed"

        # Missing required fields should raise error
        with pytest.raises(Exception):
            Provenance(source="Test")  # Missing timestamp

    def test_assertion_requires_provenance(self):
        """Test assertion requires at least one provenance source."""
        from api.routes.system import Assertion

        # Should raise validation error with empty provenance
        with pytest.raises(Exception):
            Assertion(claim="Test claim", provenance=[], domain="test", confidence=0.9)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
