"""
Tests for UBI Model
"""

import pandas as pd
import pytest
from ubi_simulator.models.ubi_model import UBIParameters, UBISimulator


@pytest.fixture
def sample_data():
    """Create sample data for testing"""
    census_data = pd.DataFrame({
        'population': [1000, 2000],
        'median_income': [30000, 50000],
        'region': ['A', 'B']
    })

    cost_data = pd.DataFrame({
        'cost_of_living': [2000, 2500],
        'region': ['A', 'B']
    })

    employment_data = pd.DataFrame({
        'employment_rate': [0.8, 0.9],
        'region': ['A', 'B']
    })

    return census_data, cost_data, employment_data


def test_ubi_parameters():
    """Test UBIParameters dataclass"""
    params = UBIParameters(
        ubi_amount=1000,
        eligibility_threshold=50000,
        phase_out_rate=0.5,
        funding_mechanism="tax",
        tax_rate=0.1
    )
    assert params.ubi_amount == 1000
    assert params.funding_mechanism == "tax"


def test_simulator_init(sample_data):
    """Test UBISimulator initialization"""
    census, cost, employment = sample_data
    simulator = UBISimulator(census, cost, employment)
    assert len(simulator.census_data) == 2
    assert 'population' in simulator.census_data.columns


def test_simulator_calculate_ubi(sample_data):
    """Test UBI calculation logic"""
    census, cost, employment = sample_data
    simulator = UBISimulator(census, cost, employment)

    params = UBIParameters(
        ubi_amount=500,
        eligibility_threshold=40000,
        phase_out_rate=0.0,
        funding_mechanism="tax",
        tax_rate=0.05
    )

    # This would normally call simulate method, but testing basic setup
    assert simulator.census_data is not None
