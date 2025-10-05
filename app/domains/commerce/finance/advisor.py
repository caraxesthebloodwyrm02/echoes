"""
FinanceAdvisor Main Orchestrator

Coordinates all finance module components to provide comprehensive
financial intelligence from analysis to actionable recommendations.
"""

import logging
from datetime import datetime
from typing import Dict, List

from .allocation import DynamicRebalancer, PortfolioOptimizer, TaxEfficiencyAdvisor
from .analysis import GoalSettingAnalyzer, RiskAssessmentEngine, SectorContextualizer
from .data_ingestion import FinancialDataIngestor
from .prediction import PredictiveModelingEngine, ScenarioSimulator
from .recommendations import (
    EthicalAIReviewer,
    GuidelineGenerator,
    RecommendationEngine,
    SuccessPathMapper,
    SuggestionEngine,
    TaskGenerator,
)
from .strategy import ComplianceChecker, EnterpriseFinanceStrategist, PersonalFinanceStrategist

logger = logging.getLogger(__name__)


class FinanceAdvisor:
    """
    Main FinanceAdvisor orchestrator integrating all 7 phases:

    1. Identification & Analysis
    2. Strategy Formulation
    3. Smart Prediction & Forecasting
    4. Relevant Assignments & Tasks
    5. Smart Allocation & Optimization
    6. Clear Guidelines & Suggestions
    7. Recommendations & Path to Success
    """

    def __init__(self, enable_ml_models: bool = False):
        """
        Initialize FinanceAdvisor with all components.

        Args:
            enable_ml_models: Enable actual ML models for predictions
        """
        logger.info("Initializing FinanceAdvisor")

        # Phase 1: Identification & Analysis
        self.data_ingestor = FinancialDataIngestor()
        self.goal_analyzer = GoalSettingAnalyzer()
        self.sector_contextualizer = SectorContextualizer()
        self.risk_assessor = RiskAssessmentEngine()

        # Phase 2: Strategy Formulation
        self.personal_strategist = PersonalFinanceStrategist()
        self.enterprise_strategist = EnterpriseFinanceStrategist()
        self.compliance_checker = ComplianceChecker()

        # Phase 3: Prediction & Forecasting
        self.prediction_engine = PredictiveModelingEngine(enable_ml_models)
        self.scenario_simulator = ScenarioSimulator()

        # Phase 5: Allocation & Optimization
        self.portfolio_optimizer = PortfolioOptimizer()
        self.rebalancer = DynamicRebalancer()
        self.tax_advisor = TaxEfficiencyAdvisor()

        # Phases 4, 6, 7: Recommendations & Guidance
        self.guideline_generator = GuidelineGenerator()
        self.suggestion_engine = SuggestionEngine()
        self.task_generator = TaskGenerator()
        self.recommendation_engine = RecommendationEngine()
        self.success_path_mapper = SuccessPathMapper()
        self.ethical_reviewer = EthicalAIReviewer()

        logger.info("FinanceAdvisor initialized successfully")

    def analyze_personal_finance(
        self, financial_data: Dict, goals: List[str], user_info: Dict
    ) -> Dict:
        """
        Complete personal finance analysis and recommendations.

        Args:
            financial_data: User's financial data
            goals: List of financial goals in natural language
            user_info: User demographics and preferences

        Returns:
            Comprehensive financial analysis and recommendations
        """
        logger.info("Starting comprehensive personal finance analysis")

        # Phase 1: Analyze current state
        structured_goals = [self.goal_analyzer.analyze_goal(goal, user_info) for goal in goals]

        risk_assessment = self.risk_assessor.assess_personal_risk(
            age=user_info.get("age", 30),
            income=financial_data.get("annual_income", 50000),
            savings=financial_data.get("savings", 10000),
            debt=financial_data.get("debt", 5000),
            dependents=user_info.get("dependents", 0),
        )

        # Phase 2: Generate strategies
        if financial_data.get("monthly_income", 0) > 0:
            budget_strategy = self.personal_strategist.create_budget_strategy(
                monthly_income=financial_data["monthly_income"],
                expenses=financial_data.get("expenses", {}),
                financial_goals=structured_goals,
                risk_tolerance=risk_assessment["risk_tolerance"],
            )
        else:
            budget_strategy = None

        # Phase 3: Generate predictions
        income_prediction = self.prediction_engine.predict_income_growth(
            historical_income=financial_data.get(
                "historical_income", [financial_data.get("annual_income", 50000)]
            ),
            years_ahead=5,
        )

        # Phase 5: Optimize allocation
        if financial_data.get("investment_portfolio"):
            optimization = self.portfolio_optimizer.optimize_personal_portfolio(
                current_allocation=financial_data["investment_portfolio"],
                risk_tolerance=risk_assessment["risk_tolerance"].value,
                time_horizon_years=user_info.get("time_horizon", 10),
                goals=[g.dict() for g in structured_goals],
            )
        else:
            optimization = None

        # Phases 4, 6, 7: Generate recommendations
        recommendations = self.recommendation_engine.generate_recommendations(
            financial_profile=financial_data,
            goals=[g.dict() for g in structured_goals],
            risk_tolerance=risk_assessment["risk_tolerance"].value,
        )

        success_path = self.success_path_mapper.create_success_path(
            goal=structured_goals[0].description if structured_goals else "Financial stability",
            current_state={"savings": financial_data.get("savings", 0)},
            target_state={
                "savings": (
                    structured_goals[0].target_amount
                    if structured_goals and structured_goals[0].target_amount
                    else 50000
                )
            },
            timeline_months=24,
        )

        # Ethical review
        for rec in recommendations:
            ethical_review = self.ethical_reviewer.review_recommendation(rec)
            rec["ethical_review"] = ethical_review

        return {
            "user_profile": user_info,
            "goals": [g.dict() for g in structured_goals],
            "risk_assessment": risk_assessment,
            "budget_strategy": budget_strategy.dict() if budget_strategy else None,
            "income_prediction": income_prediction.dict(),
            "portfolio_optimization": optimization.dict() if optimization else None,
            "recommendations": recommendations,
            "success_path": success_path.dict(),
            "timestamp": datetime.utcnow().isoformat(),
            "advisor_version": "1.0.0",
        }

    def analyze_enterprise_finance(
        self, financial_data: Dict, business_info: Dict, strategic_goals: List[str]
    ) -> Dict:
        """
        Complete enterprise finance analysis and strategy.

        Args:
            financial_data: Company financial data
            business_info: Business information (industry, size, etc.)
            strategic_goals: Strategic business goals

        Returns:
            Comprehensive enterprise financial strategy
        """
        logger.info("Starting enterprise finance analysis")

        # Phase 1: Contextual analysis
        sector_context = self.sector_contextualizer.get_sector_context(
            industry=business_info.get("industry", "technology"),
            company_size=business_info.get("size", "medium"),
        )

        enterprise_risk = self.risk_assessor.assess_enterprise_risk(
            revenue=financial_data.get("revenue", 1000000),
            profit_margin=financial_data.get("profit_margin", 0.10),
            debt_to_equity=financial_data.get("debt_to_equity", 0.50),
            cash_reserves=financial_data.get("cash_reserves", 200000),
        )

        # Phase 2: Strategic planning
        if financial_data.get("available_capital", 0) > 0:
            capital_strategy = self.enterprise_strategist.create_capital_allocation_strategy(
                available_capital=financial_data["available_capital"],
                business_units=financial_data.get("business_units", []),
                strategic_priorities=strategic_goals,
            )
        else:
            capital_strategy = None

        growth_strategy = self.enterprise_strategist.create_growth_strategy(
            current_revenue=financial_data.get("revenue", 1000000),
            target_growth_rate=0.20,
            market_analysis={"trends": sector_context.market_trends},
        )

        # Phase 3: Forecasting
        revenue_forecast = self.prediction_engine.forecast_enterprise_revenue(
            historical_revenue=financial_data.get(
                "historical_revenue", [financial_data.get("revenue", 1000000)]
            ),
            quarters_ahead=4,
        )

        return {
            "business_profile": business_info,
            "sector_context": sector_context.dict(),
            "risk_assessment": enterprise_risk,
            "capital_strategy": capital_strategy.dict() if capital_strategy else None,
            "growth_strategy": growth_strategy.dict(),
            "revenue_forecast": revenue_forecast.dict(),
            "timestamp": datetime.utcnow().isoformat(),
            "advisor_version": "1.0.0",
        }

    def get_quick_insights(self, financial_snapshot: Dict) -> Dict:
        """
        Get quick financial insights and suggestions.

        Args:
            financial_snapshot: Current financial snapshot

        Returns:
            Quick insights and actionable suggestions
        """
        logger.info("Generating quick financial insights")

        suggestions = self.suggestion_engine.generate_suggestions(financial_snapshot)

        return {
            "suggestions": suggestions,
            "priority_actions": suggestions[:3],
            "estimated_monthly_savings": sum(s.get("monthly_impact", 0) for s in suggestions),
            "estimated_annual_impact": sum(s.get("annual_impact", 0) for s in suggestions),
        }
