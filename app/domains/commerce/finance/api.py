"""
FinanceAdvisor API Endpoints

FastAPI routes for the FinanceAdvisor module.
"""

import logging
import time
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from .advisor import FinanceAdvisor
from .security_utils import security_manager

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize FinanceAdvisor
finance_advisor = FinanceAdvisor(enable_ml_models=False)

# Rate limiting storage (in production, use Redis)
rate_limit_storage: Dict[str, List[float]] = {}
RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds


def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host if request.client else "unknown"


def check_rate_limit(request: Request) -> None:
    """Simple rate limiting implementation"""
    client_ip = get_client_ip(request)
    current_time = time.time()

    # Initialize storage for new clients
    if client_ip not in rate_limit_storage:
        rate_limit_storage[client_ip] = []

    # Clean old requests outside the window
    rate_limit_storage[client_ip] = [
        req_time
        for req_time in rate_limit_storage[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]

    # Check if rate limit exceeded
    if len(rate_limit_storage[client_ip]) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT_REQUESTS} req/{RATE_LIMIT_WINDOW}s.",
        )

    # Add current request
    rate_limit_storage[client_ip].append(current_time)


def validate_input_data(data: Dict) -> Dict:
    """Validate and sanitize input data for security"""
    # Check for potentially malicious patterns
    data_str = str(data)

    # Basic XSS/injection detection
    dangerous_patterns = ["<script", "javascript:", "onerror=", "onclick=", "eval(", "__import__"]
    for pattern in dangerous_patterns:
        if pattern.lower() in data_str.lower():
            logger.warning(f"Potentially malicious pattern detected: {pattern}")
            raise HTTPException(
                status_code=400, detail="Invalid input data: potentially malicious content detected"
            )

    return data


def create_audit_log(request: Request, action: str, status: str, details: Dict) -> None:
    """Create audit log for API requests"""
    audit_log = security_manager.create_audit_log(
        action=action,
        user_id=request.headers.get("X-User-ID", "anonymous"),
        resource="finance_api",
        details={
            "endpoint": str(request.url.path),
            "method": request.method,
            "status": status,
            "client_ip": get_client_ip(request),
            **details,
        },
    )
    logger.info(f"API Audit Log: {audit_log}")


# Request/Response Models
class PersonalFinanceRequest(BaseModel):
    """Request for personal finance analysis"""

    financial_data: Dict
    goals: List[str]
    user_info: Dict


class EnterpriseFinanceRequest(BaseModel):
    """Request for enterprise finance analysis"""

    financial_data: Dict
    business_info: Dict
    strategic_goals: List[str]


class QuickInsightsRequest(BaseModel):
    """Request for quick financial insights"""

    financial_snapshot: Dict


# API Endpoints
@router.post("/personal/analyze", tags=["Personal Finance"])
async def analyze_personal_finance(
    request_body: PersonalFinanceRequest,
    request: Request,
    _rate_limit: None = Depends(check_rate_limit),
):
    """
    Comprehensive personal finance analysis.

    Provides:
    - Financial goal analysis
    - Risk assessment
    - Budget strategy
    - Investment recommendations
    - Success roadmap
    """
    try:
        logger.info("Processing personal finance analysis request")

        # Validate input data
        validate_input_data(request_body.financial_data)
        validate_input_data(request_body.user_info)

        # Detect PII in request
        pii_findings = security_manager.detect_pii(request_body.financial_data)
        if any(len(v) > 0 for v in pii_findings.values()):
            logger.info(f"PII detected in request: {list(pii_findings.keys())}")

        result = finance_advisor.analyze_personal_finance(
            financial_data=request_body.financial_data,
            goals=request_body.goals,
            user_info=request_body.user_info,
        )

        # Create audit log
        create_audit_log(
            request=request,
            action="personal_finance_analysis",
            status="success",
            details={"goals_count": len(request_body.goals)},
        )

        return {
            "status": "success",
            "data": result,
            "message": "Personal finance analysis completed successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in personal finance analysis: {e}")
        create_audit_log(
            request=request,
            action="personal_finance_analysis",
            status="error",
            details={"error": str(e)},
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enterprise/analyze", tags=["Enterprise Finance"])
async def analyze_enterprise_finance(
    request_body: EnterpriseFinanceRequest,
    request: Request,
    _rate_limit: None = Depends(check_rate_limit),
):
    """
    Comprehensive enterprise finance analysis.

    Provides:
    - Sector benchmarking
    - Risk assessment
    - Capital allocation strategy
    - Growth strategy
    - Revenue forecasting
    """
    try:
        logger.info("Processing enterprise finance analysis request")

        # Validate input data
        validate_input_data(request_body.financial_data)
        validate_input_data(request_body.business_info)

        result = finance_advisor.analyze_enterprise_finance(
            financial_data=request_body.financial_data,
            business_info=request_body.business_info,
            strategic_goals=request_body.strategic_goals,
        )

        # Create audit log
        create_audit_log(
            request=request,
            action="enterprise_finance_analysis",
            status="success",
            details={"industry": request_body.business_info.get("industry", "unknown")},
        )

        return {
            "status": "success",
            "data": result,
            "message": "Enterprise finance analysis completed successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enterprise finance analysis: {e}")
        create_audit_log(
            request=request,
            action="enterprise_finance_analysis",
            status="error",
            details={"error": str(e)},
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insights/quick", tags=["Quick Insights"])
async def get_quick_insights(
    request_body: QuickInsightsRequest,
    request: Request,
    _rate_limit: None = Depends(check_rate_limit),
):
    """
    Get quick financial insights and suggestions.

    Provides immediate, actionable suggestions based on current financial state.
    """
    try:
        logger.info("Processing quick insights request")

        # Validate input data
        validate_input_data(request_body.financial_snapshot)

        result = finance_advisor.get_quick_insights(request_body.financial_snapshot)

        # Create audit log
        create_audit_log(request=request, action="quick_insights", status="success", details={})

        return {
            "status": "success",
            "data": result,
            "message": "Quick insights generated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quick insights: {e}")
        create_audit_log(
            request=request, action="quick_insights", status="error", details={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/goals/analyze", tags=["Goal Analysis"])
async def analyze_goals(goals: List[str], context: Optional[Dict] = None):
    """
    Analyze and structure financial goals.

    Converts natural language goals into structured, actionable objectives.
    """
    try:
        logger.info(f"Analyzing {len(goals)} financial goals")

        structured_goals = [
            finance_advisor.goal_analyzer.analyze_goal(goal, context or {}) for goal in goals
        ]

        return {
            "status": "success",
            "data": {
                "goals": [g.dict() for g in structured_goals],
                "priority_goal": structured_goals[0].dict() if structured_goals else None,
            },
            "message": f"Analyzed {len(goals)} goals successfully",
        }

    except Exception as e:
        logger.error(f"Error analyzing goals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prediction/income", tags=["Predictions"])
async def predict_income(
    historical_income: List[float], years_ahead: int = 5, factors: Optional[Dict] = None
):
    """
    Predict future income growth.

    Uses historical data and various factors to forecast income trajectory.
    """
    try:
        logger.info(f"Predicting income for {years_ahead} years")

        prediction = finance_advisor.prediction_engine.predict_income_growth(
            historical_income=historical_income, years_ahead=years_ahead, factors=factors
        )

        return {
            "status": "success",
            "data": prediction.dict(),
            "message": "Income prediction completed successfully",
        }

    except Exception as e:
        logger.error(f"Error predicting income: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prediction/retirement", tags=["Predictions"])
async def project_retirement(
    current_balance: float,
    monthly_contribution: float,
    years_to_retirement: int,
    expected_return: float = 0.07,
):
    """
    Project retirement fund growth.

    Calculates future retirement savings based on contributions and returns.
    """
    try:
        logger.info(f"Projecting retirement fund for {years_to_retirement} years")

        prediction = finance_advisor.prediction_engine.project_retirement_fund(
            current_balance=current_balance,
            monthly_contribution=monthly_contribution,
            years_to_retirement=years_to_retirement,
            expected_return=expected_return,
        )

        return {
            "status": "success",
            "data": prediction.dict(),
            "message": "Retirement projection completed successfully",
        }

    except Exception as e:
        logger.error(f"Error projecting retirement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/portfolio/optimize", tags=["Portfolio Management"])
async def optimize_portfolio(
    current_allocation: Dict[str, float],
    risk_tolerance: str,
    time_horizon_years: int,
    goals: Optional[List[Dict]] = None,
):
    """
    Optimize investment portfolio allocation.

    Provides optimal asset allocation based on risk tolerance and goals.
    """
    try:
        logger.info("Optimizing portfolio allocation")

        optimization = finance_advisor.portfolio_optimizer.optimize_personal_portfolio(
            current_allocation=current_allocation,
            risk_tolerance=risk_tolerance,
            time_horizon_years=time_horizon_years,
            goals=goals or [],
        )

        return {
            "status": "success",
            "data": optimization.dict(),
            "message": "Portfolio optimization completed successfully",
        }

    except Exception as e:
        logger.error(f"Error optimizing portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scenario/investment", tags=["Scenario Analysis"])
async def simulate_investment_scenarios(
    initial_investment: float, monthly_contribution: float, years: int, scenarios: Dict[str, Dict]
):
    """
    Simulate different investment scenarios.

    Compare outcomes under different market conditions and return rates.
    """
    try:
        logger.info(f"Simulating {len(scenarios)} investment scenarios")

        results = finance_advisor.scenario_simulator.simulate_investment_scenario(
            initial_investment=initial_investment,
            monthly_contribution=monthly_contribution,
            years=years,
            scenarios=scenarios,
        )

        return {
            "status": "success",
            "data": {
                "scenarios": [s.dict() for s in results],
                "best_case": results[0].dict() if results else None,
                "worst_case": results[-1].dict() if results else None,
            },
            "message": f"Simulated {len(scenarios)} scenarios successfully",
        }

    except Exception as e:
        logger.error(f"Error simulating scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for FinanceAdvisor module"""
    return {
        "status": "healthy",
        "module": "FinanceAdvisor",
        "version": "1.0.0",
        "components": {
            "data_ingestion": "operational",
            "analysis": "operational",
            "strategy": "operational",
            "prediction": "operational",
            "allocation": "operational",
            "recommendations": "operational",
        },
    }
