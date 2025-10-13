#!/usr/bin/env python3
"""
Test suite for the Symphony Assistance API.
"""

import asyncio
import sys
from pathlib import Path

import pytest
from httpx import AsyncClient

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from automation.backend.assistant_api import app


@pytest.mark.asyncio
async def test_assistant_query():
    """Test the assistant query endpoint."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        payload = {
            "prompt": "Hello, can you help me understand FastAPI?",
            "temperature": 0.5,
            "max_tokens": 100
        }
        response = await client.post("/assistant/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "model" in data
        assert isinstance(data["content"], str)
        assert len(data["content"]) > 0


@pytest.mark.asyncio
async def test_list_models():
    """Test the models listing endpoint."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/assistant/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert isinstance(data["models"], list)
        # Should have some models available
        assert len(data["models"]) > 0


@pytest.mark.asyncio
async def test_switch_api_key():
    """Test switching between API keys."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Switch to secondary key
        payload = {"key_type": "SECONDARY"}
        response = await client.post("/assistant/switch-key", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["active_key"] == "SECONDARY"

        # Switch back to primary key
        payload = {"key_type": "PRIMARY"}
        response = await client.post("/assistant/switch-key", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["active_key"] == "PRIMARY"


@pytest.mark.asyncio
async def test_invalid_key_switch():
    """Test error handling for invalid key type."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        payload = {"key_type": "INVALID"}
        response = await client.post("/assistant/switch-key", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_query_validation():
    """Test request validation for queries."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Test missing prompt
        payload = {"temperature": 0.5}
        response = await client.post("/assistant/query", json=payload)
        assert response.status_code == 422  # Validation error

        # Test invalid temperature
        payload = {"prompt": "test", "temperature": 3.0}
        response = await client.post("/assistant/query", json=payload)
        assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    # Run tests directly
    print("Running Symphony Assistance API tests...")
    asyncio.run(test_list_models())
    asyncio.run(test_switch_api_key())
    asyncio.run(test_invalid_key_switch())
    asyncio.run(test_query_validation())
    print("All tests passed!")
