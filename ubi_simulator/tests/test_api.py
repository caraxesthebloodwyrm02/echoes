"""
Tests for UBI Simulator API
"""

import pytest
from fastapi.testclient import TestClient
from ubi_simulator.api.main import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_simulate_basic():
    """Test basic UBI simulation"""
    payload = {
        "ubi_amount": 500,
        "eligibility_threshold": 50000,
        "phase_out_rate": 0.5,
        "funding_mechanism": "tax",
        "tax_rate": 0.1
    }
    response = client.post("/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total_cost" in data
    assert "poverty_reduction" in data
    assert isinstance(data["total_cost"], (int, float))


def test_predefined_scenarios():
    """Test predefined scenarios endpoint"""
    response = client.get("/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert "basic_ubi" in data
    assert "targeted_ubi" in data
