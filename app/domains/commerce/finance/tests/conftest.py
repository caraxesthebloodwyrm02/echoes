import sys
from pathlib import Path

import pytest

from app.domains.commerce.finance.api import rate_limit_storage

"""
Pytest configuration and shared fixtures for FinanceAdvisor tests
"""


# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))


@pytest.fixture
def sample_financial_data():
    """Sample financial data for testing"""
    return {
        "annual_income": 75000,
        "monthly_income": 6250,
        "savings": 25000,
        "debt": 15000,
        "expenses": {
            "housing": 1500,
            "food": 600,
            "transportation": 400,
            "entertainment": 200,
            "utilities": 150,
        },
    }


@pytest.fixture
def sample_user_info():
    """Sample user information for testing"""
    return {
        "age": 32,
        "dependents": 0,
        "education": "bachelor",
        "industry": "technology",
        "risk_tolerance": "moderate",
    }


@pytest.fixture
def sample_goals():
    """Sample financial goals for testing"""
    return [
        "Save for retirement by age 65",
        "Pay off debt in 3 years",
        "Build 6-month emergency fund",
        "Save $50,000 for house down payment",
    ]


@pytest.fixture
def sample_enterprise_data():
    """Sample enterprise financial data for testing"""
    return {
        "revenue": 5000000,
        "profit_margin": 0.15,
        "debt_to_equity": 0.50,
        "cash_reserves": 1000000,
        "available_capital": 500000,
        "current_ratio": 2.0,
        "quick_ratio": 1.5,
        "business_units": [
            {"name": "Product Development", "revenue": 2000000, "expected_roi": 0.20},
            {"name": "Marketing", "revenue": 1500000, "expected_roi": 0.15},
        ],
    }


@pytest.fixture
def sample_business_info():
    """Sample business information for testing"""
    return {
        "industry": "technology",
        "size": "medium",
        "years_in_business": 5,
        "employee_count": 50,
        "market_position": "growth",
    }


@pytest.fixture
def sample_portfolio():
    """Sample investment portfolio for testing"""
    return {"stocks": 0.70, "bonds": 0.20, "cash": 0.10}


@pytest.fixture
def sample_historical_income():
    """Sample historical income data for testing"""
    return [50000, 55000, 60000, 65000, 70000]


@pytest.fixture
def sample_scenarios():
    """Sample investment scenarios for testing"""
    return {
        "conservative": {"return_rate": 0.05, "volatility": 0.10, "probability": 0.33},
        "moderate": {"return_rate": 0.07, "volatility": 0.15, "probability": 0.34},
        "aggressive": {"return_rate": 0.10, "volatility": 0.20, "probability": 0.33},
    }


@pytest.fixture(autouse=True)
def reset_test_state():
    """Reset any global state before each test"""
    # Clear rate limiting storage if it exists
    try:
        from app.domains.commerce.finance.api import rate_limit_storage

        rate_limit_storage.clear()
    except ImportError:
        pass

    yield

    # Cleanup after test
    pass


# Pytest markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "security: mark test as a security test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


"""
Comprehensive test suite for FinanceAdvisor API endpoints

Tests security, rate limiting, input validation, and audit logging.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domains.commerce.finance.api import router

# Create test app
app = FastAPI()
app.include_router(router, prefix="/api/finance")

client = TestClient(app)


class TestAPISecurityFeatures:
    """Test API security features"""

    def setup_method(self):
        """Reset rate limit storage before each test"""
        rate_limit_storage.clear()

    def test_rate_limiting(self):
        """Test rate limiting is enforced"""
        # Make requests up to the limit
        for i in range(100):
            response = client.get("/api/finance/health")
            assert response.status_code == 200

        # Next request should be rate limited
        response = client.get("/api/finance/health")
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    def test_rate_limiting_per_ip(self):
        """Test rate limiting is per IP address"""
        rate_limit_storage.clear()

        # Simulate different IPs using headers
        headers_ip1 = {"X-Forwarded-For": "192.168.1.1"}
        headers_ip2 = {"X-Forwarded-For": "192.168.1.2"}

        # Each IP should have its own limit
        for i in range(50):
            response = client.get("/api/finance/health", headers=headers_ip1)
            assert response.status_code == 200

        for i in range(50):
            response = client.get("/api/finance/health", headers=headers_ip2)
            assert response.status_code == 200

    def test_input_validation_xss_protection(self):
        """Test XSS protection in input validation"""
        malicious_data = {
            "financial_data": {"income": 50000, "expenses": "<script>alert('xss')</script>"},
            "goals": ["Save money"],
            "user_info": {"age": 30},
        }

        response = client.post("/api/finance/personal/analyze", json=malicious_data)
        assert response.status_code == 400
        assert "malicious content detected" in response.json()["detail"].lower()

    def test_input_validation_injection_protection(self):
        """Test SQL/code injection protection"""
        malicious_data = {
            "financial_data": {"income": 50000, "query": "'; DROP TABLE users; --"},
            "goals": ["eval('malicious code')"],
            "user_info": {"age": 30},
        }

        response = client.post("/api/finance/personal/analyze", json=malicious_data)
        assert response.status_code == 400

    def test_input_validation_javascript_protection(self):
        """Test JavaScript injection protection"""
        malicious_data = {
            "financial_data": {"income": 50000, "note": "javascript:alert(1)"},
            "goals": ["Save money"],
            "user_info": {"age": 30},
        }

        response = client.post("/api/finance/personal/analyze", json=malicious_data)
        assert response.status_code == 400

    def test_input_validation_event_handler_protection(self):
        """Test event handler injection protection"""
        malicious_data = {
            "financial_data": {"income": 50000, "field": "<img onerror='alert(1)' src='x'>"},
            "goals": ["Save money"],
            "user_info": {"age": 30},
        }

        response = client.post("/api/finance/personal/analyze", json=malicious_data)
        assert response.status_code == 400

    @patch("app.domains.commerce.finance.api.security_manager")
    def test_pii_detection_logging(self, mock_security):
        """Test PII detection is logged"""
        mock_security.detect_pii.return_value = {
            "email_addresses": ["test@example.com"],
            "phone_numbers": [],
            "social_security_numbers": [],
            "credit_card_numbers": [],
            "bank_account_numbers": [],
        }

        valid_data = {
            "financial_data": {"income": 50000, "email": "test@example.com"},
            "goals": ["Save money"],
            "user_info": {"age": 30},
        }

        with patch("app.domains.commerce.finance.api.finance_advisor") as mock_advisor:
            mock_advisor.analyze_personal_finance.return_value = {"status": "success"}
            # response = client.post("/api/finance/personal/analyze", json=valid_data)  # Removed unused variable

            # Should not fail but PII should be detected
            mock_security.detect_pii.assert_called()


class TestPersonalFinanceEndpoints:
    """Test personal finance endpoints"""

    def setup_method(self):
        """Reset rate limit storage before each test"""
        rate_limit_storage.clear()

    @patch("app.domains.commerce.finance.api.finance_advisor")
    @patch("app.domains.commerce.finance.api.security_manager")
    def test_personal_analyze_success(self, mock_security, mock_advisor):
        """Test successful personal finance analysis"""
        mock_security.detect_pii.return_value = {
            "email_addresses": [],
            "phone_numbers": [],
            "social_security_numbers": [],
            "credit_card_numbers": [],
            "bank_account_numbers": [],
        }

        mock_advisor.analyze_personal_finance.return_value = {
            "risk_assessment": {"risk_tolerance": "moderate"},
            "recommendations": [],
        }

        request_data = {
            "financial_data": {"annual_income": 75000, "monthly_income": 6250, "savings": 25000},
            "goals": ["Retire by 65"],
            "user_info": {"age": 32},
        }

        response = client.post("/api/finance/personal/analyze", json=request_data)

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert "data" in response.json()

    @patch("app.domains.commerce.finance.api.finance_advisor")
    def test_personal_analyze_validation_error(self, mock_advisor):
        """Test validation error handling"""
        mock_advisor.analyze_personal_finance.side_effect = ValueError("Invalid data")

        request_data = {
            "financial_data": {"income": -1000},  # Invalid negative income
            "goals": ["Save money"],
            "user_info": {"age": 30},
        }

        response = client.post("/api/finance/personal/analyze", json=request_data)

        assert response.status_code == 500


class TestEnterpriseFinanceEndpoints:
    """Test enterprise finance endpoints"""

    def setup_method(self):
        """Reset rate limit storage before each test"""
        rate_limit_storage.clear()

    @patch("app.domains.commerce.finance.api.finance_advisor")
    @patch("app.domains.commerce.finance.api.security_manager")
    def test_enterprise_analyze_success(self, mock_security, mock_advisor):
        """Test successful enterprise finance analysis"""
        mock_security.detect_pii.return_value = {
            "email_addresses": [],
            "phone_numbers": [],
            "social_security_numbers": [],
            "credit_card_numbers": [],
            "bank_account_numbers": [],
        }

        mock_advisor.analyze_enterprise_finance.return_value = {
            "sector_benchmarking": {"industry": "technology"},
            "risk_assessment": {"financial_health_score": 85},
        }

        request_data = {
            "financial_data": {"revenue": 5000000, "profit_margin": 0.15},
            "business_info": {"industry": "technology"},
            "strategic_goals": ["Expand market share"],
        }

        response = client.post("/api/finance/enterprise/analyze", json=request_data)

        assert response.status_code == 200
        assert response.json()["status"] == "success"

    @patch("app.domains.commerce.finance.api.finance_advisor")
    @patch("app.domains.commerce.finance.api.security_manager")
    def test_enterprise_analyze_with_audit_log(self, mock_security, mock_advisor):
        """Test audit logging for enterprise analysis"""
        mock_security.detect_pii.return_value = {
            "email_addresses": [],
            "phone_numbers": [],
            "social_security_numbers": [],
            "credit_card_numbers": [],
            "bank_account_numbers": [],
        }
        mock_security.create_audit_log.return_value = {"timestamp": "2024-01-01T00:00:00"}

        mock_advisor.analyze_enterprise_finance.return_value = {"status": "success"}

        request_data = {
            "financial_data": {"revenue": 5000000},
            "business_info": {"industry": "technology"},
            "strategic_goals": ["Grow"],
        }

        response = client.post("/api/finance/enterprise/analyze", json=request_data)

        assert response.status_code == 200
        mock_security.create_audit_log.assert_called()


class TestQuickInsightsEndpoint:
    """Test quick insights endpoint"""

    def setup_method(self):
        """Reset rate limit storage before each test"""
        rate_limit_storage.clear()

    @patch("app.domains.commerce.finance.api.finance_advisor")
    @patch("app.domains.commerce.finance.api.security_manager")
    def test_quick_insights_success(self, mock_security, mock_advisor):
        """Test successful quick insights generation"""
        mock_security.detect_pii.return_value = {}
        mock_security.create_audit_log.return_value = {}

        mock_advisor.get_quick_insights.return_value = {
            "suggestions": [{"action": "Reduce dining out", "impact": 100}]
        }

        request_data = {
            "financial_snapshot": {"monthly_income": 6000, "expenses": {"dining_out": 500}}
        }

        response = client.post("/api/finance/insights/quick", json=request_data)

        assert response.status_code == 200
        assert response.json()["status"] == "success"


class TestGoalAnalysisEndpoint:
    """Test goal analysis endpoint"""

    def setup_method(self):
        """Reset rate limit storage before each test"""
        rate_limit_storage.clear()

    @patch("app.domains.commerce.finance.api.finance_advisor")
    def test_analyze_goals_success(self, mock_advisor):
        """Test successful goal analysis"""
        mock_goal = MagicMock()
        mock_goal.dict.return_value = {
            "goal_text": "Save for retirement",
            "priority": "high",
            "target_amount": 1000000,
        }

        mock_advisor.goal_analyzer.analyze_goal.return_value = mock_goal

        request_data = {
            "goals": ["Save for retirement", "Buy a house"],
            "context": {"income": 75000},
        }

        response = client.post("/api/finance/goals/analyze", json=request_data)

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert "goals" in response.json()["data"]


class TestPredictionEndpoints:
    """Test prediction endpoints"""

    def setup_method(self):
        """Reset rate limit storage before each test"""
        rate_limit_storage.clear()

    @patch("app.domains.commerce.finance.api.finance_advisor")
    def test_predict_income_success(self, mock_advisor):
        """Test successful income prediction"""
        mock_prediction = MagicMock()
        mock_prediction.dict.return_value = {
            "predicted_value": 85000,
            "confidence_interval": {"lower": 80000, "upper": 90000},
        }

        mock_advisor.prediction_engine.predict_income_growth.return_value = mock_prediction

        request_data = {"historical_income": [50000, 55000, 60000], "years_ahead": 5}

        response = client.post("/api/finance/prediction/income", json=request_data)

        assert response.status_code == 200
        assert response.json()["status"] == "success"

    @patch("app.domains.commerce.finance.api.finance_advisor")
    def test_predict_retirement_success(self, mock_advisor):
        """Test successful retirement projection"""
        mock_prediction = MagicMock()
        mock_prediction.dict.return_value = {"final_balance": 1500000, "monthly_income": 7500}

        mock_advisor.prediction_engine.project_retirement_fund.return_value = mock_prediction

        request_data = {
            "current_balance": 50000,
            "monthly_contribution": 500,
            "years_to_retirement": 30,
            "expected_return": 0.07,
        }

        response = client.post("/api/finance/prediction/retirement", json=request_data)

        assert response.status_code == 200
        assert response.json()["status"] == "success"


class TestPortfolioEndpoints:
    """Test portfolio management endpoints"""

    def setup_method(self):
        """Reset rate limit storage before each test"""
        rate_limit_storage.clear()

    @patch("app.domains.commerce.finance.api.finance_advisor")
    def test_optimize_portfolio_success(self, mock_advisor):
        """Test successful portfolio optimization"""
        mock_optimization = MagicMock()
        mock_optimization.dict.return_value = {
            "recommended_allocation": {"stocks": 0.70, "bonds": 0.25, "cash": 0.05},
            "expected_return": 0.08,
            "expected_risk": 0.12,
            "sharpe_ratio": 0.67,
        }

        mock_advisor.portfolio_optimizer.optimize_personal_portfolio.return_value = (
            mock_optimization
        )

        request_data = {
            "current_allocation": {"stocks": 0.70, "bonds": 0.20, "cash": 0.10},
            "risk_tolerance": "moderate",
            "time_horizon_years": 20,
        }

        response = client.post("/api/finance/portfolio/optimize", json=request_data)

        assert response.status_code == 200
        assert response.json()["status"] == "success"


class TestScenarioEndpoints:
    """Test scenario analysis endpoints"""

    def setup_method(self):
        """Reset rate limit storage before each test"""
        rate_limit_storage.clear()

    @patch("app.domains.commerce.finance.api.finance_advisor")
    def test_simulate_investment_scenarios_success(self, mock_advisor):
        """Test successful investment scenario simulation"""
        mock_scenario1 = MagicMock()
        mock_scenario1.dict.return_value = {
            "name": "conservative",
            "outcomes": {"final_value": 150000},
        }

        mock_scenario2 = MagicMock()
        mock_scenario2.dict.return_value = {
            "name": "aggressive",
            "outcomes": {"final_value": 200000},
        }

        mock_advisor.scenario_simulator.simulate_investment_scenario.return_value = [
            mock_scenario1,
            mock_scenario2,
        ]

        request_data = {
            "initial_investment": 10000,
            "monthly_contribution": 500,
            "years": 10,
            "scenarios": {
                "conservative": {"return_rate": 0.05, "volatility": 0.10},
                "aggressive": {"return_rate": 0.10, "volatility": 0.20},
            },
        }

        response = client.post("/api/finance/scenario/investment", json=request_data)

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert "scenarios" in response.json()["data"]


class TestHealthEndpoint:
    """Test health check endpoint"""

    def setup_method(self):
        """Reset rate limit storage before each test"""
        rate_limit_storage.clear()

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/finance/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["module"] == "FinanceAdvisor"
        assert "components" in response.json()


class TestAuditLogging:
    """Test audit logging functionality"""

    def setup_method(self):
        """Reset rate limit storage before each test"""
        rate_limit_storage.clear()

    @patch("app.domains.commerce.finance.api.finance_advisor")
    @patch("app.domains.commerce.finance.api.security_manager")
    def test_audit_log_on_success(self, mock_security, mock_advisor):
        """Test audit log is created on successful request"""
        mock_security.detect_pii.return_value = {}
        mock_security.create_audit_log.return_value = {
            "timestamp": "2024-01-01T00:00:00",
            "action": "personal_finance_analysis",
        }

        mock_advisor.analyze_personal_finance.return_value = {"status": "success"}

        request_data = {
            "financial_data": {"income": 50000},
            "goals": ["Save"],
            "user_info": {"age": 30},
        }

        response = client.post("/api/finance/personal/analyze", json=request_data)

        assert response.status_code == 200
        # Verify audit log was created
        assert mock_security.create_audit_log.called

    @patch("app.domains.commerce.finance.api.finance_advisor")
    @patch("app.domains.commerce.finance.api.security_manager")
    def test_audit_log_on_error(self, mock_security, mock_advisor):
        """Test audit log is created on error"""
        mock_security.detect_pii.return_value = {}
        mock_security.create_audit_log.return_value = {
            "timestamp": "2024-01-01T00:00:00",
            "action": "personal_finance_analysis",
            "status": "error",
        }

        mock_advisor.analyze_personal_finance.side_effect = Exception("Test error")

        request_data = {
            "financial_data": {"income": 50000},
            "goals": ["Save"],
            "user_info": {"age": 30},
        }

        response = client.post("/api/finance/personal/analyze", json=request_data)

        assert response.status_code == 500
        # Verify error was logged
        assert mock_security.create_audit_log.called


class TestErrorHandling:
    """Test error handling in API"""

    def setup_method(self):
        """Reset rate limit storage before each test"""
        rate_limit_storage.clear()

    @patch("app.domains.commerce.finance.api.finance_advisor")
    def test_internal_server_error(self, mock_advisor):
        """Test internal server error handling"""
        mock_advisor.analyze_personal_finance.side_effect = Exception("Internal error")

        request_data = {
            "financial_data": {"income": 50000},
            "goals": ["Save"],
            "user_info": {"age": 30},
        }

        response = client.post("/api/finance/personal/analyze", json=request_data)

        assert response.status_code == 500
        assert "detail" in response.json()

    def test_invalid_json(self):
        """Test invalid JSON handling"""
        response = client.post(
            "/api/finance/personal/analyze",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422  # Validation error

    def test_missing_required_fields(self):
        """Test missing required fields"""
        request_data = {
            "financial_data": {"income": 50000}
            # Missing: goals, user_info
        }

        response = client.post("/api/finance/personal/analyze", json=request_data)

        assert response.status_code == 422  # Validation error


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API"""

    def setup_method(self):
        """Reset rate limit storage before each test"""
        rate_limit_storage.clear()

    @patch("app.domains.commerce.finance.api.finance_advisor")
    @patch("app.domains.commerce.finance.api.security_manager")
    def test_full_workflow(self, mock_security, mock_advisor):
        """Test complete API workflow"""
        mock_security.detect_pii.return_value = {}
        mock_security.create_audit_log.return_value = {}

        # Configure mocks
        mock_advisor.analyze_personal_finance.return_value = {"status": "success"}
        mock_advisor.get_quick_insights.return_value = {"suggestions": []}

        # Step 1: Health check
        response = client.get("/api/finance/health")
        assert response.status_code == 200

        # Step 2: Analyze personal finance
        response = client.post(
            "/api/finance/personal/analyze",
            json={
                "financial_data": {"income": 75000},
                "goals": ["Retire by 65"],
                "user_info": {"age": 32},
            },
        )
        assert response.status_code == 200

        # Step 3: Get quick insights
        response = client.post(
            "/api/finance/insights/quick", json={"financial_snapshot": {"monthly_income": 6000}}
        )
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
Pytest configuration and shared fixtures for FinanceAdvisor tests
"""


# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))


@pytest.fixture
def sample_financial_data():
    """Sample financial data for testing"""
    return {
        "annual_income": 75000,
        "monthly_income": 6250,
        "savings": 25000,
        "debt": 15000,
        "expenses": {
            "housing": 1500,
            "food": 600,
            "transportation": 400,
            "entertainment": 200,
            "utilities": 150,
        },
    }


@pytest.fixture
def sample_user_info():
    """Sample user information for testing"""
    return {
        "age": 32,
        "dependents": 0,
        "education": "bachelor",
        "industry": "technology",
        "risk_tolerance": "moderate",
    }


@pytest.fixture
def sample_goals():
    """Sample financial goals for testing"""
    return [
        "Save for retirement by age 65",
        "Pay off debt in 3 years",
        "Build 6-month emergency fund",
        "Save $50,000 for house down payment",
    ]


@pytest.fixture
def sample_enterprise_data():
    """Sample enterprise financial data for testing"""
    return {
        "revenue": 5000000,
        "profit_margin": 0.15,
        "debt_to_equity": 0.50,
        "cash_reserves": 1000000,
        "available_capital": 500000,
        "current_ratio": 2.0,
        "quick_ratio": 1.5,
        "business_units": [
            {"name": "Product Development", "revenue": 2000000, "expected_roi": 0.20},
            {"name": "Marketing", "revenue": 1500000, "expected_roi": 0.15},
        ],
    }


@pytest.fixture
def sample_business_info():
    """Sample business information for testing"""
    return {
        "industry": "technology",
        "size": "medium",
        "years_in_business": 5,
        "employee_count": 50,
        "market_position": "growth",
    }


@pytest.fixture
def sample_portfolio():
    """Sample investment portfolio for testing"""
    return {"stocks": 0.70, "bonds": 0.20, "cash": 0.10}


@pytest.fixture
def sample_historical_income():
    """Sample historical income data for testing"""
    return [50000, 55000, 60000, 65000, 70000]


@pytest.fixture
def sample_scenarios():
    """Sample investment scenarios for testing"""
    return {
        "conservative": {"return_rate": 0.05, "volatility": 0.10, "probability": 0.33},
        "moderate": {"return_rate": 0.07, "volatility": 0.15, "probability": 0.34},
        "aggressive": {"return_rate": 0.10, "volatility": 0.20, "probability": 0.33},
    }


@pytest.fixture(autouse=True)
def reset_test_state():
    """Reset any global state before each test"""
    # Clear rate limiting storage if it exists
    try:
        rate_limit_storage.clear()
    except ImportError:
        pass

    yield

    # Cleanup after test
    pass


# Pytest markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "security: mark test as a security test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
