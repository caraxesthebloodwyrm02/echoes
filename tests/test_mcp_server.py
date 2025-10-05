"""
Tests for MCP server endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from mcp_server import app


@pytest.fixture
def client():
    """Test client for MCP server."""
    return TestClient(app)


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "MCP Server is running"}


def test_favicon_endpoint(client):
    """Test the favicon endpoint."""
    response = client.get("/favicon.ico")
    assert response.status_code == 204
    assert response.content == b""


def test_echo_tool_default_repeat(client):
    """Test the echo tool with default repeat."""
    payload = {"text": "hello"}
    response = client.post("/tools/echo", json=payload)
    assert response.status_code == 200
    assert response.json() == {"echoed": "hello"}


def test_echo_tool_with_repeat(client):
    """Test the echo tool with custom repeat."""
    payload = {"text": "world", "repeat": 3}
    response = client.post("/tools/echo", json=payload)
    assert response.status_code == 200
    assert response.json() == {"echoed": "world world world"}


def test_echo_tool_zero_repeat(client):
    """Test the echo tool with zero repeat."""
    payload = {"text": "test", "repeat": 0}
    response = client.post("/tools/echo", json=payload)
    assert response.status_code == 200
    assert response.json() == {"echoed": ""}


def test_echo_tool_invalid_data(client):
    """Test the echo tool with invalid data."""
    payload = {"invalid": "data"}
    response = client.post("/tools/echo", json=payload)
    assert response.status_code == 422  # Validation error


def test_echo_tool_empty_text(client):
    """Test the echo tool with empty text."""
    payload = {"text": "", "repeat": 2}
    response = client.post("/tools/echo", json=payload)
    assert response.status_code == 200
    assert response.json() == {"echoed": " "}
