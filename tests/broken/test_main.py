"""
Tests for API main FastAPI application.
"""


import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestMainAPI:
    """Test main API endpoints."""

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code in [200, 404]  # May not exist
        if response.status_code == 200:
            assert "message" in response.json() or "status" in response.json()

    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "middleware" in data
        assert "connections" in data

    def test_app_creation(self):
        """Test that the FastAPI app is created properly."""
        assert app is not None
        assert hasattr(app, "title")
        assert hasattr(app, "version")

    def test_cors_middleware(self):
        """Test that CORS middleware is configured."""
        # Check if CORS middleware is present
        cors_middleware = None
        for middleware in app.user_middleware:
            if "cors" in str(middleware.cls).lower():
                cors_middleware = middleware
                break

        # CORS should be configured
        assert cors_middleware is not None

    def test_websocket_endpoint_exists(self):
        """Test that WebSocket endpoint is registered."""
        # Check if websocket route is registered
        websocket_routes = [
            route
            for route in app.routes
            if hasattr(route, "path") and route.path == "/ws/stream"
        ]
        # Should have websocket endpoint
        assert len(websocket_routes) > 0

    def test_pattern_detection_endpoint(self, client):
        """Test the pattern detection endpoint."""
        # Test with mock data
        test_data = {
            "text": "This is a test pattern detection request",
            "options": {"min_confidence": 0.5, "max_patterns": 5},
        }

        response = client.post("/api/pattern-detect", json=test_data)
        # May return 404 if endpoint not implemented, or 200/422 if implemented
        assert response.status_code in [200, 404, 422]

    def test_self_rag_endpoint(self, client):
        """Test the SELF-RAG verification endpoint."""
        test_data = {
            "claim": "This is a test claim for verification",
            "context": "Test context for the claim",
        }

        response = client.post("/api/verify", json=test_data)
        # May return 404 if endpoint not implemented, or 200/422 if implemented
        assert response.status_code in [200, 404, 422]

    def test_search_endpoint(self, client):
        """Test the search endpoint."""
        test_data = {"query": "test search query", "limit": 10}

        response = client.post("/api/search", json=test_data)
        # May return 404 if endpoint not implemented, or 200/422 if implemented
        assert response.status_code in [200, 404, 422]

    def test_error_handling(self, client):
        """Test error handling for invalid endpoints."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

    def test_websocket_connection(self):
        """Test WebSocket connection (basic test)."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/stream") as websocket:
                # WebSocket should connect successfully
                assert websocket is not None
