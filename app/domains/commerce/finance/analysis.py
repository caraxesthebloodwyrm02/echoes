"""
Phase 1: Analysis - Financial State & Goal Understanding

Components for analyzing financial state, understanding goals, contextualizing
sector information, and assessing risk tolerance.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RiskTolerance(str, Enum):
    """Risk tolerance levels"""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    VERY_AGGRESSIVE = "very_aggressive"


class FinancialGoalType(str, Enum):
    """Types of financial goals"""

    RETIREMENT = "retirement"
    DEBT_REDUCTION = "debt_reduction"
    WEALTH_BUILDING = "wealth_building"
    BUSINESS_EXPANSION = "business_expansion"
    COST_OPTIMIZATION = "cost_optimization"
    REVENUE_GROWTH = "revenue_growth"
    MARKET_EXPANSION = "market_expansion"
    EMERGENCY_FUND = "emergency_fund"
    MAJOR_PURCHASE = "major_purchase"


class FinancialGoal(BaseModel):
    """Structured financial goal"""

    goal_type: FinancialGoalType
    description: str
    target_amount: Optional[float] = None
    target_date: Optional[datetime] = None
    priority: int = Field(ge=1, le=10, description="Priority level (1-10)")
    current_progress: float = Field(default=0.0, ge=0.0, le=100.0)
    metadata: Dict = Field(default_factory=dict)


class FinancialHealthScore(BaseModel):
    """Overall financial health assessment"""

    overall_score: float = Field(ge=0.0, le=100.0)
    liquidity_score: float = Field(ge=0.0, le=100.0)
    debt_score: float = Field(ge=0.0, le=100.0)
    savings_score: float = Field(ge=0.0, le=100.0)
    investment_score: float = Field(ge=0.0, le=100.0)
    risk_score: float = Field(ge=0.0, le=100.0)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class SectorBenchmarks(BaseModel):
    """Industry-specific benchmarks"""

    industry: str
    avg_profit_margin: float
    avg_revenue_growth: float
    avg_debt_to_equity: float
    market_trends: List[str]
    regulatory_considerations: List[str]
    competitive_position: str


class GoalSettingAnalyzer:
    """
    Utilize NLP to analyze and structure user-defined financial goals.

    Transforms natural language goal descriptions into structured,
    actionable objectives.
    """

    def __init__(self):
        self.goal_patterns = self._initialize_goal_patterns()

    def analyze_goal(self, goal_description: str, context: Dict = None) -> FinancialGoal:
        """
        Analyze natural language goal and structure it.

        Args:
            goal_description: User's goal in natural language
            context: Additional context (user type, current financial state)

        Returns:
            Structured FinancialGoal object
        """
        logger.info(f"Analyzing goal: {goal_description}")

        # Extract goal type
        goal_type = self._classify_goal_type(goal_description)

        # Extract numerical targets
        target_amount = self._extract_amount(goal_description)
        target_date = self._extract_timeframe(goal_description)

        # Determine priority based on keywords and context
        priority = self._determine_priority(goal_description, context or {})

        goal = FinancialGoal(
            goal_type=goal_type,
            description=goal_description,
            target_amount=target_amount,
            target_date=target_date,
            priority=priority,
            metadata={
                "analyzed_at": datetime.utcnow().isoformat(),
                "confidence": 0.85,
                "extracted_keywords": self._extract_keywords(goal_description),
            },
        )

        logger.info(f"Structured goal: {goal.goal_type} with priority {goal.priority}")
        return goal

    def analyze_multiple_goals(self, goal_descriptions: List[str]) -> List[FinancialGoal]:
        """Analyze and prioritize multiple goals"""
        goals = [self.analyze_goal(desc) for desc in goal_descriptions]
        return sorted(goals, key=lambda g: g.priority, reverse=True)

    def _classify_goal_type(self, description: str) -> FinancialGoalType:
        """Classify goal type from description"""
        description_lower = description.lower()

        if any(word in description_lower for word in ["retire", "retirement", "pension"]):
            return FinancialGoalType.RETIREMENT
        elif any(word in description_lower for word in ["debt", "loan", "payoff", "pay off"]):
            return FinancialGoalType.DEBT_REDUCTION
        elif any(word in description_lower for word in ["expand", "growth", "scale", "new market"]):
            return FinancialGoalType.BUSINESS_EXPANSION
        elif any(
            word in description_lower for word in ["cost", "reduce", "optimize", "efficiency"]
        ):
            return FinancialGoalType.COST_OPTIMIZATION
        elif any(word in description_lower for word in ["revenue", "sales", "income", "profit"]):
            return FinancialGoalType.REVENUE_GROWTH
        elif any(word in description_lower for word in ["emergency", "safety net", "cushion"]):
            return FinancialGoalType.EMERGENCY_FUND
        elif any(word in description_lower for word in ["save", "invest", "wealth"]):
            return FinancialGoalType.WEALTH_BUILDING
        else:
            return FinancialGoalType.MAJOR_PURCHASE

    def _extract_amount(self, description: str) -> Optional[float]:
        """Extract monetary amount from goal description"""
        import re

        # Look for patterns like $1000, 1000 dollars, 1k, etc.
        patterns = [
            r"\$\s?([\d,]+\.?\d*)",
            r"([\d,]+\.?\d*)\s?(?:dollars|usd)",
            r"([\d]+)k",
        ]

        for pattern in patterns:
            match = re.search(pattern, description.lower())
            if match:
                amount_str = match.group(1).replace(",", "")
                if "k" in description.lower():
                    return float(amount_str) * 1000
                return float(amount_str)
        return None

    def _extract_timeframe(self, description: str) -> Optional[datetime]:
        """Extract target date from goal description"""
        import re

        from dateutil.relativedelta import relativedelta

        # Look for time expressions
        if "year" in description.lower():
            match = re.search(r"(\d+)\s?year", description.lower())
            if match:
                years = int(match.group(1))
                return datetime.utcnow() + relativedelta(years=years)

        if "month" in description.lower():
            match = re.search(r"(\d+)\s?month", description.lower())
            if match:
                months = int(match.group(1))
                return datetime.utcnow() + relativedelta(months=months)

        return None

    def _determine_priority(self, description: str, context: Dict) -> int:
        """Determine goal priority"""
        priority = 5  # Default medium priority

        description_lower = description.lower()

        # High priority keywords
        if any(
            word in description_lower for word in ["urgent", "critical", "immediate", "emergency"]
        ):
            priority = 9
        elif any(word in description_lower for word in ["important", "essential", "priority"]):
            priority = 7
        elif any(word in description_lower for word in ["eventually", "someday", "long-term"]):
            priority = 3

        return priority

    def _extract_keywords(self, description: str) -> List[str]:
        """Extract key financial terms from description"""
        financial_keywords = [
            "retirement",
            "debt",
            "invest",
            "save",
            "growth",
            "expand",
            "profit",
            "revenue",
            "cost",
            "risk",
            "return",
            "portfolio",
        ]
        return [kw for kw in financial_keywords if kw in description.lower()]

    def _initialize_goal_patterns(self) -> Dict:
        """Initialize NLP patterns for goal classification"""
        return {
            "retirement": ["retire", "retirement", "pension", "401k", "ira"],
            "debt": ["debt", "loan", "credit", "payoff", "refinance"],
            "investment": ["invest", "portfolio", "stocks", "bonds", "crypto"],
            "business": ["expand", "grow", "scale", "acquisition", "market"],
        }


class SectorContextualizer:
    """
    Integrate external APIs to gather industry-specific benchmarks,
    regulatory information, and economic indicators.
    """

    def __init__(self, api_integrations: Dict = None):
        self.api_integrations = api_integrations or {}
        self.benchmark_cache: Dict[str, SectorBenchmarks] = {}

    def get_sector_context(self, industry: str, company_size: str = "medium") -> SectorBenchmarks:
        """
        Get comprehensive sector context and benchmarks.

        Args:
            industry: Industry/sector name
            company_size: Size category (small, medium, large)

        Returns:
            SectorBenchmarks with industry data
        """
        logger.info(f"Fetching sector context for {industry}")

        # Check cache first
        cache_key = f"{industry}_{company_size}"
        if cache_key in self.benchmark_cache:
            return self.benchmark_cache[cache_key]

        # Fetch from APIs or use default benchmarks
        benchmarks = self._fetch_benchmarks(industry, company_size)

        # Cache results
        self.benchmark_cache[cache_key] = benchmarks

        return benchmarks

    def _fetch_benchmarks(self, industry: str, company_size: str) -> SectorBenchmarks:
        """Fetch industry benchmarks (placeholder for API integration)"""
        # In production, integrate with financial data APIs
        # For now, return realistic default benchmarks

        industry_defaults = {
            "technology": {
                "avg_profit_margin": 0.20,
                "avg_revenue_growth": 0.15,
                "avg_debt_to_equity": 0.30,
                "trends": ["AI adoption", "Cloud migration", "Cybersecurity investment"],
                "regulations": ["GDPR", "CCPA", "Data protection laws"],
            },
            "retail": {
                "avg_profit_margin": 0.08,
                "avg_revenue_growth": 0.05,
                "avg_debt_to_equity": 0.50,
                "trends": [
                    "E-commerce growth",
                    "Omnichannel strategies",
                    "Supply chain optimization",
                ],
                "regulations": ["Consumer protection", "Product safety", "Labor laws"],
            },
            "finance": {
                "avg_profit_margin": 0.25,
                "avg_revenue_growth": 0.08,
                "avg_debt_to_equity": 0.80,
                "trends": ["Fintech disruption", "Digital banking", "Regulatory technology"],
                "regulations": ["Dodd-Frank", "Basel III", "Anti-money laundering"],
            },
        }

        data = industry_defaults.get(industry.lower(), industry_defaults["technology"])

        return SectorBenchmarks(
            industry=industry,
            avg_profit_margin=data["avg_profit_margin"],
            avg_revenue_growth=data["avg_revenue_growth"],
            avg_debt_to_equity=data["avg_debt_to_equity"],
            market_trends=data["trends"],
            regulatory_considerations=data["regulations"],
            competitive_position=self._assess_competitive_position(company_size),
        )

    def _assess_competitive_position(self, company_size: str) -> str:
        """Assess competitive position based on company size"""
        positions = {
            "small": "Niche player with agility advantage",
            "medium": "Growing competitor with market presence",
            "large": "Market leader with established brand",
        }
        return positions.get(company_size, positions["medium"])


class RiskAssessmentEngine:
    """
    Evaluate individual risk tolerance and enterprise-level financial health.

    Provides comprehensive risk analysis for both personal and business contexts.
    """

    def __init__(self):
        self.risk_factors = self._initialize_risk_factors()

    def assess_personal_risk(
        self,
        age: int,
        income: float,
        savings: float,
        debt: float,
        dependents: int,
        investment_experience: str = "moderate",
    ) -> Dict:
        """
        Assess personal risk tolerance and financial health.

        Returns comprehensive risk assessment including tolerance level
        and specific risk metrics.
        """
        logger.info(f"Assessing personal risk for age {age}")

        # Calculate risk capacity
        risk_capacity_score = self._calculate_risk_capacity(income, savings, debt, dependents)

        # Determine risk tolerance
        tolerance = self._determine_personal_tolerance(age, income, savings, investment_experience)

        # Calculate specific risk metrics
        debt_to_income = (debt / income) if income > 0 else 0
        savings_ratio = (savings / (income * 12)) if income > 0 else 0

        return {
            "risk_tolerance": tolerance,
            "risk_capacity_score": risk_capacity_score,
            "debt_to_income_ratio": round(debt_to_income, 2),
            "savings_ratio": round(savings_ratio, 2),
            "recommended_allocation": self._get_asset_allocation(tolerance),
            "risk_factors": self._identify_personal_risk_factors(
                age, debt_to_income, savings_ratio
            ),
            "recommendations": self._generate_risk_recommendations(tolerance),
        }

    def assess_enterprise_risk(
        self,
        revenue: float,
        profit_margin: float,
        debt_to_equity: float,
        cash_reserves: float,
        market_volatility: float = 0.15,
    ) -> Dict:
        """
        Assess enterprise financial health and market risk.

        Returns comprehensive risk assessment for business context.
        """
        logger.info("Assessing enterprise risk")

        # Calculate financial health score
        health_score = self._calculate_enterprise_health(
            revenue, profit_margin, debt_to_equity, cash_reserves
        )

        # Assess market exposure
        market_risk_score = self._assess_market_risk(market_volatility)

        # Calculate liquidity ratio
        liquidity_score = self._assess_liquidity(cash_reserves, revenue)

        return {
            "financial_health_score": health_score,
            "market_risk_score": market_risk_score,
            "liquidity_score": liquidity_score,
            "debt_to_equity_ratio": round(debt_to_equity, 2),
            "profit_margin": round(profit_margin, 4),
            "risk_level": self._categorize_enterprise_risk(health_score),
            "risk_factors": self._identify_enterprise_risk_factors(
                debt_to_equity, profit_margin, liquidity_score
            ),
            "mitigation_strategies": self._suggest_mitigation_strategies(health_score),
        }

    def _calculate_risk_capacity(
        self, income: float, savings: float, debt: float, dependents: int
    ) -> float:
        """Calculate individual's capacity to take financial risk"""
        base_score = 50.0

        # Positive factors
        if savings > income * 6:  # 6 months emergency fund
            base_score += 20
        elif savings > income * 3:
            base_score += 10

        # Negative factors
        if debt > income * 2:
            base_score -= 20
        elif debt > income:
            base_score -= 10

        if dependents > 2:
            base_score -= 10

        return max(0.0, min(100.0, base_score))

    def _determine_personal_tolerance(
        self, age: int, income: float, savings: float, experience: str
    ) -> RiskTolerance:
        """Determine personal risk tolerance level"""
        risk_score = 0

        # Age factor (younger = higher tolerance)
        if age < 30:
            risk_score += 3
        elif age < 45:
            risk_score += 2
        elif age < 60:
            risk_score += 1

        # Income and savings factor
        if income > 100000 and savings > income:
            risk_score += 2
        elif income > 50000:
            risk_score += 1

        # Experience factor
        experience_scores = {"beginner": 0, "moderate": 1, "experienced": 2}
        risk_score += experience_scores.get(experience, 1)

        # Map score to tolerance level
        if risk_score >= 5:
            return RiskTolerance.AGGRESSIVE
        elif risk_score >= 3:
            return RiskTolerance.MODERATE
        else:
            return RiskTolerance.CONSERVATIVE

    def _calculate_enterprise_health(
        self, revenue: float, profit_margin: float, debt_to_equity: float, cash_reserves: float
    ) -> float:
        """Calculate overall enterprise financial health score"""
        health_score = 50.0

        # Profitability
        if profit_margin > 0.20:
            health_score += 20
        elif profit_margin > 0.10:
            health_score += 10
        elif profit_margin < 0:
            health_score -= 20

        # Leverage
        if debt_to_equity < 0.5:
            health_score += 15
        elif debt_to_equity > 1.5:
            health_score -= 15

        # Liquidity
        cash_ratio = cash_reserves / revenue if revenue > 0 else 0
        if cash_ratio > 0.20:
            health_score += 15
        elif cash_ratio < 0.05:
            health_score -= 15

        return max(0.0, min(100.0, health_score))

    def _assess_market_risk(self, volatility: float) -> float:
        """Assess market risk based on volatility"""
        # Higher volatility = higher risk score
        return min(100.0, volatility * 500)

    def _assess_liquidity(self, cash_reserves: float, revenue: float) -> float:
        """Assess liquidity position"""
        if revenue <= 0:
            return 0.0
        ratio = cash_reserves / revenue
        return min(100.0, ratio * 400)

    def _get_asset_allocation(self, tolerance: RiskTolerance) -> Dict:
        """Get recommended asset allocation based on risk tolerance"""
        allocations = {
            RiskTolerance.CONSERVATIVE: {"stocks": 0.30, "bonds": 0.50, "cash": 0.20},
            RiskTolerance.MODERATE: {"stocks": 0.60, "bonds": 0.30, "cash": 0.10},
            RiskTolerance.AGGRESSIVE: {"stocks": 0.80, "bonds": 0.15, "cash": 0.05},
        }
        return allocations.get(tolerance, allocations[RiskTolerance.MODERATE])

    def _identify_personal_risk_factors(
        self, age: int, debt_to_income: float, savings_ratio: float
    ) -> List[str]:
        """Identify personal financial risk factors"""
        factors = []

        if debt_to_income > 0.40:
            factors.append("High debt-to-income ratio")
        if savings_ratio < 0.25:
            factors.append("Insufficient emergency savings")
        if age > 50 and savings_ratio < 1.0:
            factors.append("Approaching retirement with low savings")

        return factors or ["No major risk factors identified"]

    def _identify_enterprise_risk_factors(
        self, debt_to_equity: float, profit_margin: float, liquidity: float
    ) -> List[str]:
        """Identify enterprise risk factors"""
        factors = []

        if debt_to_equity > 1.0:
            factors.append("High leverage ratio")
        if profit_margin < 0.05:
            factors.append("Low profit margins")
        if liquidity < 30:
            factors.append("Limited liquidity reserves")

        return factors or ["Strong financial position"]

    def _generate_risk_recommendations(self, tolerance: RiskTolerance) -> List[str]:
        """Generate personalized risk recommendations"""
        recommendations = {
            RiskTolerance.CONSERVATIVE: [
                "Focus on capital preservation",
                "Maintain diversified bond portfolio",
                "Keep 6-12 months emergency fund",
            ],
            RiskTolerance.MODERATE: [
                "Balance growth and stability",
                "Diversify across asset classes",
                "Maintain 3-6 months emergency fund",
            ],
            RiskTolerance.AGGRESSIVE: [
                "Focus on growth opportunities",
                "Consider higher-risk investments",
                "Maintain minimum 3 months emergency fund",
            ],
        }
        return recommendations.get(tolerance, recommendations[RiskTolerance.MODERATE])

    def _categorize_enterprise_risk(self, health_score: float) -> str:
        """Categorize enterprise risk level"""
        if health_score >= 75:
            return "Low Risk"
        elif health_score >= 50:
            return "Moderate Risk"
        elif health_score >= 25:
            return "Elevated Risk"
        else:
            return "High Risk"

    def _suggest_mitigation_strategies(self, health_score: float) -> List[str]:
        """Suggest risk mitigation strategies"""
        if health_score >= 75:
            return ["Maintain current practices", "Explore growth opportunities"]
        elif health_score >= 50:
            return ["Improve cash flow management", "Consider debt reduction"]
        else:
            return ["Focus on cost reduction", "Improve profitability", "Reduce leverage"]

    def _initialize_risk_factors(self) -> Dict:
        """Initialize common risk factors"""
        return {
            "market_risk": 0.15,
            "credit_risk": 0.10,
            "operational_risk": 0.05,
            "liquidity_risk": 0.08,
        }
