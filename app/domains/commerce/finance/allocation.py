"""
Phase 5: Smart Allocation & Optimization

Components for continuous optimization of financial allocations.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AllocationStrategy(str, Enum):
    """Portfolio allocation strategies"""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    TAX_OPTIMIZED = "tax_optimized"


class AssetClass(str, Enum):
    """Asset classes"""

    STOCKS = "stocks"
    BONDS = "bonds"
    CASH = "cash"
    REAL_ESTATE = "real_estate"
    COMMODITIES = "commodities"
    CRYPTO = "cryptocurrency"


class OptimizationResult(BaseModel):
    """Portfolio optimization result"""

    optimization_id: str
    strategy: AllocationStrategy
    allocation: Dict[str, float]
    expected_return: float
    expected_risk: float
    sharpe_ratio: float
    rebalancing_needed: bool
    recommendations: List[str]
    tax_efficiency_score: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PortfolioOptimizer:
    """
    Optimize asset allocation based on risk tolerance and goals.

    For personal investments, optimize asset allocation.
    For enterprises, optimize capital expenditure.
    """

    def __init__(self):
        self.risk_profiles = self._initialize_risk_profiles()
        self.asset_return_assumptions = self._load_return_assumptions()

    def optimize_personal_portfolio(
        self,
        current_allocation: Dict[str, float],
        risk_tolerance: str,
        time_horizon_years: int,
        goals: List[Dict],
    ) -> OptimizationResult:
        """
        Optimize personal investment portfolio.

        Args:
            current_allocation: Current asset allocation
            risk_tolerance: Risk tolerance level
            time_horizon_years: Investment time horizon
            goals: Financial goals

        Returns:
            Optimization result with recommended allocation
        """
        logger.info(f"Optimizing portfolio for {risk_tolerance} investor")

        # Get target allocation for risk profile
        target_allocation = self._get_target_allocation(risk_tolerance, time_horizon_years)

        # Calculate expected return and risk
        expected_return = self._calculate_expected_return(target_allocation)
        expected_risk = self._calculate_expected_risk(target_allocation)
        sharpe_ratio = self._calculate_sharpe_ratio(expected_return, expected_risk)

        # Check if rebalancing needed
        rebalancing_needed = self._check_rebalancing_need(current_allocation, target_allocation)

        # Generate recommendations
        recommendations = self._generate_optimization_recommendations(
            current_allocation, target_allocation, goals
        )

        # Calculate tax efficiency
        tax_efficiency = self._calculate_tax_efficiency(target_allocation)

        return OptimizationResult(
            optimization_id=self._generate_id(),
            strategy=(
                AllocationStrategy(risk_tolerance)
                if risk_tolerance in [s.value for s in AllocationStrategy]
                else AllocationStrategy.MODERATE
            ),
            allocation=target_allocation,
            expected_return=expected_return,
            expected_risk=expected_risk,
            sharpe_ratio=sharpe_ratio,
            rebalancing_needed=rebalancing_needed,
            recommendations=recommendations,
            tax_efficiency_score=tax_efficiency,
        )

    def optimize_enterprise_capital(
        self,
        capital_available: float,
        investment_opportunities: List[Dict],
        strategic_priorities: List[str],
    ) -> Dict:
        """
        Optimize enterprise capital allocation.

        Args:
            capital_available: Available capital for allocation
            investment_opportunities: List of investment opportunities
            strategic_priorities: Strategic priorities

        Returns:
            Optimized capital allocation plan
        """
        logger.info(f"Optimizing ${capital_available:,.0f} capital allocation")

        # Score and rank opportunities
        scored_opportunities = self._score_opportunities(
            investment_opportunities, strategic_priorities
        )

        # Allocate capital optimally
        allocation = self._allocate_capital(capital_available, scored_opportunities)

        # Calculate portfolio metrics
        portfolio_roi = self._calculate_portfolio_roi(allocation)
        risk_score = self._calculate_portfolio_risk(allocation)

        return {
            "optimization_id": self._generate_id(),
            "total_capital": capital_available,
            "allocation": allocation,
            "expected_portfolio_roi": portfolio_roi,
            "risk_score": risk_score,
            "diversification_score": self._calculate_diversification(allocation),
            "recommendations": self._generate_enterprise_recommendations(allocation),
        }

    def _get_target_allocation(self, risk_tolerance: str, time_horizon: int) -> Dict[str, float]:
        """Get target asset allocation"""
        # Base allocations by risk tolerance
        base_allocations = {
            "conservative": {"stocks": 0.30, "bonds": 0.55, "cash": 0.15},
            "moderate": {"stocks": 0.60, "bonds": 0.30, "cash": 0.10},
            "aggressive": {"stocks": 0.80, "bonds": 0.15, "cash": 0.05},
            "balanced": {"stocks": 0.50, "bonds": 0.40, "cash": 0.10},
        }

        allocation = base_allocations.get(risk_tolerance, base_allocations["moderate"]).copy()

        # Adjust for time horizon
        if time_horizon > 20:
            allocation["stocks"] = min(0.95, allocation["stocks"] + 0.10)
            allocation["bonds"] = max(0.05, allocation["bonds"] - 0.05)
        elif time_horizon < 5:
            allocation["stocks"] = max(0.20, allocation["stocks"] - 0.15)
            allocation["bonds"] = min(0.65, allocation["bonds"] + 0.10)
            allocation["cash"] = min(0.20, allocation["cash"] + 0.05)

        return allocation

    def _calculate_expected_return(self, allocation: Dict[str, float]) -> float:
        """Calculate expected portfolio return"""
        returns = {
            "stocks": 0.10,
            "bonds": 0.04,
            "cash": 0.02,
            "real_estate": 0.08,
            "commodities": 0.06,
        }

        expected_return = sum(
            allocation.get(asset, 0) * returns.get(asset, 0.05) for asset in allocation
        )

        return expected_return

    def _calculate_expected_risk(self, allocation: Dict[str, float]) -> float:
        """Calculate expected portfolio risk (volatility)"""
        volatilities = {
            "stocks": 0.18,
            "bonds": 0.06,
            "cash": 0.01,
            "real_estate": 0.12,
            "commodities": 0.20,
        }

        # Simplified portfolio volatility
        variance = sum(
            (allocation.get(asset, 0) ** 2) * (volatilities.get(asset, 0.10) ** 2)
            for asset in allocation
        )

        return variance**0.5

    def _calculate_sharpe_ratio(self, expected_return: float, risk: float) -> float:
        """Calculate Sharpe ratio"""
        risk_free_rate = 0.03  # 3% risk-free rate
        if risk == 0:
            return 0
        return (expected_return - risk_free_rate) / risk

    def _check_rebalancing_need(self, current: Dict[str, float], target: Dict[str, float]) -> bool:
        """Check if portfolio needs rebalancing"""
        threshold = 0.05  # 5% threshold

        for asset in target:
            current_weight = current.get(asset, 0)
            target_weight = target[asset]

            if abs(current_weight - target_weight) > threshold:
                return True

        return False

    def _generate_optimization_recommendations(
        self, current: Dict[str, float], target: Dict[str, float], goals: List[Dict]
    ) -> List[str]:
        """Generate portfolio optimization recommendations"""
        recommendations = []

        # Rebalancing recommendations
        for asset, target_weight in target.items():
            current_weight = current.get(asset, 0)
            difference = target_weight - current_weight

            if abs(difference) > 0.05:
                if difference > 0:
                    recommendations.append(
                        f"Increase {asset} allocation by {difference*100:.1f}% to reach target"
                    )
                else:
                    recommendations.append(
                        f"Decrease {asset} allocation by {abs(difference)*100:.1f}% to reach target"
                    )

        # Goal-based recommendations
        if goals:
            recommendations.append("Consider tax-loss harvesting opportunities")
            recommendations.append("Review fund expense ratios for cost optimization")

        return recommendations

    def _calculate_tax_efficiency(self, allocation: Dict[str, float]) -> float:
        """Calculate tax efficiency score"""
        # Tax efficiency scores for each asset class
        tax_efficiency = {
            "stocks": 0.85,  # Can use tax-loss harvesting, long-term gains
            "bonds": 0.60,  # Interest taxed as ordinary income
            "cash": 0.50,  # Interest fully taxable
            "real_estate": 0.70,  # Depreciation benefits
            "crypto": 0.65,  # Capital gains treatment
        }

        score = sum(
            allocation.get(asset, 0) * tax_efficiency.get(asset, 0.70) for asset in allocation
        )

        return score * 100  # Convert to 0-100 scale

    def _score_opportunities(self, opportunities: List[Dict], priorities: List[str]) -> List[Dict]:
        """Score investment opportunities"""
        scored = []

        for opp in opportunities:
            score = 0.0

            # ROI score (40% weight)
            expected_roi = opp.get("expected_roi", 0)
            score += expected_roi * 0.4

            # Strategic alignment (30% weight)
            if opp.get("category") in priorities:
                score += 0.30

            # Risk score (20% weight)
            risk_level = opp.get("risk_level", "medium")
            risk_scores = {"low": 0.20, "medium": 0.15, "high": 0.10}
            score += risk_scores.get(risk_level, 0.15)

            # Time to value (10% weight)
            time_to_value = opp.get("time_to_value_months", 12)
            if time_to_value <= 6:
                score += 0.10
            elif time_to_value <= 12:
                score += 0.05

            scored.append({**opp, "score": score})

        return sorted(scored, key=lambda x: x["score"], reverse=True)

    def _allocate_capital(self, total_capital: float, opportunities: List[Dict]) -> List[Dict]:
        """Allocate capital across opportunities"""
        allocation = []
        remaining_capital = total_capital

        for opp in opportunities:
            if remaining_capital <= 0:
                break

            # Allocate proportionally based on score
            requested_amount = opp.get("required_capital", 0)
            max_allocation = min(requested_amount, remaining_capital * 0.30)

            if max_allocation > 0:
                allocation.append(
                    {
                        "opportunity": opp["name"],
                        "category": opp.get("category", "uncategorized"),
                        "allocated_amount": max_allocation,
                        "expected_roi": opp.get("expected_roi", 0),
                        "score": opp["score"],
                    }
                )

                remaining_capital -= max_allocation

        return allocation

    def _calculate_portfolio_roi(self, allocation: List[Dict]) -> float:
        """Calculate weighted portfolio ROI"""
        total_capital = sum(a["allocated_amount"] for a in allocation)

        if total_capital == 0:
            return 0.0

        weighted_roi = (
            sum(a["allocated_amount"] * a["expected_roi"] for a in allocation) / total_capital
        )

        return weighted_roi

    def _calculate_portfolio_risk(self, allocation: List[Dict]) -> float:
        """Calculate portfolio risk score"""
        # Simplified risk calculation
        return 0.50  # Medium risk

    def _calculate_diversification(self, allocation: List[Dict]) -> float:
        """Calculate diversification score"""
        # Higher score = more diversified
        categories = set(a["category"] for a in allocation)
        return min(100.0, len(categories) * 20)

    def _generate_enterprise_recommendations(self, allocation: List[Dict]) -> List[str]:
        """Generate enterprise capital allocation recommendations"""
        recommendations = [
            "Monitor project milestones and adjust allocation if needed",
            "Maintain reserve capital for unexpected opportunities",
            "Review quarterly performance against expected ROI",
        ]

        if len(allocation) < 3:
            recommendations.append("Consider diversifying across more opportunities")

        return recommendations

    def _initialize_risk_profiles(self) -> Dict:
        """Initialize risk profiles"""
        return {
            "conservative": {"risk_score": 0.20},
            "moderate": {"risk_score": 0.50},
            "aggressive": {"risk_score": 0.80},
        }

    def _load_return_assumptions(self) -> Dict:
        """Load historical return assumptions"""
        return {
            "stocks": {"return": 0.10, "volatility": 0.18},
            "bonds": {"return": 0.04, "volatility": 0.06},
            "cash": {"return": 0.02, "volatility": 0.01},
        }

    def _generate_id(self) -> str:
        """Generate unique ID"""
        import uuid

        return f"OPT-{uuid.uuid4().hex[:10].upper()}"


class DynamicRebalancer:
    """
    Automatically suggest adjustments to portfolios or budgets based on
    market changes or performance.
    """

    def __init__(self):
        self.rebalancing_threshold = 0.05  # 5% drift threshold

    def analyze_drift(
        self, current_allocation: Dict[str, float], target_allocation: Dict[str, float]
    ) -> Dict:
        """
        Analyze portfolio drift from target allocation.

        Returns:
            Drift analysis with rebalancing recommendations
        """
        logger.info("Analyzing portfolio drift")

        drift_analysis = {}
        max_drift = 0.0

        for asset, target_weight in target_allocation.items():
            current_weight = current_allocation.get(asset, 0)
            drift = current_weight - target_weight
            drift_analysis[asset] = {
                "current_weight": current_weight,
                "target_weight": target_weight,
                "drift": drift,
                "drift_percentage": (drift / target_weight * 100) if target_weight > 0 else 0,
            }

            max_drift = max(max_drift, abs(drift))

        needs_rebalancing = max_drift > self.rebalancing_threshold

        rebalancing_actions = (
            self._generate_rebalancing_actions(drift_analysis) if needs_rebalancing else []
        )

        return {
            "needs_rebalancing": needs_rebalancing,
            "max_drift": max_drift,
            "drift_analysis": drift_analysis,
            "rebalancing_actions": rebalancing_actions,
            "estimated_transactions": len(rebalancing_actions),
            "tax_considerations": self._evaluate_tax_impact(rebalancing_actions),
        }

    def suggest_rebalancing(self, portfolio_value: float, drift_analysis: Dict) -> List[Dict]:
        """
        Suggest specific rebalancing transactions.

        Returns:
            List of buy/sell transactions
        """
        transactions = []

        for asset, analysis in drift_analysis.items():
            drift = analysis["drift"]

            if abs(drift) > self.rebalancing_threshold:
                amount = abs(drift * portfolio_value)

                transactions.append(
                    {
                        "asset": asset,
                        "action": "SELL" if drift > 0 else "BUY",
                        "amount_dollars": amount,
                        "amount_percentage": abs(drift) * 100,
                        "reason": f"Drift of {abs(drift)*100:.1f}% from target",
                    }
                )

        return transactions

    def _generate_rebalancing_actions(self, drift_analysis: Dict) -> List[str]:
        """Generate rebalancing action recommendations"""
        actions = []

        for asset, data in drift_analysis.items():
            drift = data["drift"]

            if abs(drift) > self.rebalancing_threshold:
                if drift > 0:
                    actions.append(f"Sell {abs(drift)*100:.1f}% of {asset}")
                else:
                    actions.append(f"Buy {abs(drift)*100:.1f}% more {asset}")

        return actions

    def _evaluate_tax_impact(self, actions: List[str]) -> Dict:
        """Evaluate tax impact of rebalancing"""
        return {
            "potential_taxable_events": len([a for a in actions if "Sell" in a]),
            "recommendation": "Consider tax-loss harvesting opportunities",
            "timing_suggestion": "Rebalance in tax-advantaged accounts first",
        }


class TaxEfficiencyAdvisor:
    """
    Recommend strategies to minimize tax liabilities.

    Features:
    - Tax-loss harvesting recommendations
    - Asset location optimization
    - Withdrawal strategy optimization
    """

    def __init__(self):
        self.tax_rates = self._load_tax_rates()

    def optimize_asset_location(
        self, total_portfolio: Dict[str, float], account_types: Dict[str, float]
    ) -> Dict:
        """
        Optimize asset location across account types.

        Args:
            total_portfolio: Total portfolio allocation
            account_types: Available account types and balances

        Returns:
            Optimized asset location strategy
        """
        logger.info("Optimizing asset location for tax efficiency")

        # Tax efficiency rankings
        tax_efficiency_ranking = {
            "stocks": "tax_advantaged_or_taxable",  # Long-term gains favorable
            "bonds": "tax_advantaged",  # Interest taxed as ordinary income
            "cash": "taxable",  # Low returns, flexibility needed
            "real_estate": "taxable",  # Depreciation benefits
        }

        allocation_strategy = {
            "taxable_account": {},
            "tax_deferred_account": {},
            "tax_free_account": {},
        }

        # Allocate tax-inefficient assets to tax-advantaged accounts
        for asset, preference in tax_efficiency_ranking.items():
            if asset in total_portfolio:
                if preference == "tax_advantaged":
                    allocation_strategy["tax_deferred_account"][asset] = total_portfolio[asset]
                else:
                    allocation_strategy["taxable_account"][asset] = total_portfolio[asset]

        return {
            "allocation_strategy": allocation_strategy,
            "estimated_annual_tax_savings": self._estimate_tax_savings(allocation_strategy),
            "recommendations": [
                "Hold bonds and REITs in tax-advantaged accounts",
                "Hold index funds in taxable accounts for tax-loss harvesting",
                "Consider municipal bonds for taxable accounts",
            ],
        }

    def identify_tax_loss_harvesting_opportunities(self, holdings: List[Dict]) -> List[Dict]:
        """
        Identify tax-loss harvesting opportunities.

        Args:
            holdings: Current holdings with cost basis and current value

        Returns:
            List of tax-loss harvesting opportunities
        """
        logger.info("Identifying tax-loss harvesting opportunities")

        opportunities = []

        for holding in holdings:
            cost_basis = holding.get("cost_basis", 0)
            current_value = holding.get("current_value", 0)
            loss = cost_basis - current_value

            if loss > 0 and loss > 500:  # Minimum $500 loss
                opportunities.append(
                    {
                        "asset": holding["name"],
                        "loss_amount": loss,
                        "tax_benefit": loss * 0.25,  # Assuming 25% tax rate
                        "recommendation": f"Harvest ${loss:.2f} loss, replace with similar asset",
                        "similar_assets": self._find_similar_assets(holding["name"]),
                    }
                )

        return sorted(opportunities, key=lambda x: x["loss_amount"], reverse=True)

    def optimize_withdrawal_strategy(
        self, accounts: Dict[str, float], withdrawal_amount: float, age: int
    ) -> Dict:
        """
        Optimize withdrawal strategy for tax efficiency.

        Args:
            accounts: Account balances by type
            withdrawal_amount: Annual withdrawal needed
            age: Current age

        Returns:
            Optimized withdrawal strategy
        """
        logger.info(f"Optimizing withdrawal of ${withdrawal_amount:,.0f}")

        # Withdrawal priority based on tax efficiency
        if age < 59.5:
            priority = ["taxable", "roth_ira", "traditional_ira"]
        elif age < 72:
            priority = ["taxable", "traditional_ira", "roth_ira"]
        else:
            # Must take RMDs
            priority = ["traditional_ira_rmd", "taxable", "roth_ira"]

        withdrawal_plan = []
        remaining = withdrawal_amount

        for account_type in priority:
            if remaining <= 0:
                break

            available = accounts.get(account_type, 0)
            withdraw = min(available, remaining)

            if withdraw > 0:
                withdrawal_plan.append(
                    {
                        "account": account_type,
                        "amount": withdraw,
                        "tax_treatment": self._get_tax_treatment(account_type),
                    }
                )
                remaining -= withdraw

        return {
            "withdrawal_plan": withdrawal_plan,
            "estimated_taxes": self._estimate_withdrawal_taxes(withdrawal_plan),
            "recommendations": self._generate_withdrawal_recommendations(age, accounts),
        }

    def _load_tax_rates(self) -> Dict:
        """Load current tax rates"""
        return {
            "ordinary_income": [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37],
            "long_term_capital_gains": [0.00, 0.15, 0.20],
            "qualified_dividends": [0.00, 0.15, 0.20],
        }

    def _estimate_tax_savings(self, strategy: Dict) -> float:
        """Estimate annual tax savings from optimization"""
        # Simplified calculation
        return 2500.0  # Estimated annual savings

    def _find_similar_assets(self, asset_name: str) -> List[str]:
        """Find similar assets for tax-loss harvesting"""
        # In production, use actual asset correlation data
        return [f"{asset_name} Alternative 1", f"{asset_name} Alternative 2"]

    def _get_tax_treatment(self, account_type: str) -> str:
        """Get tax treatment for account type"""
        treatments = {
            "taxable": "Ordinary income and capital gains",
            "traditional_ira": "Ordinary income on withdrawal",
            "roth_ira": "Tax-free",
            "traditional_ira_rmd": "Required minimum distribution",
        }
        return treatments.get(account_type, "Unknown")

    def _estimate_withdrawal_taxes(self, plan: List[Dict]) -> float:
        """Estimate taxes on withdrawals"""
        total_tax = 0.0

        for withdrawal in plan:
            account = withdrawal["account"]
            amount = withdrawal["amount"]

            if "traditional_ira" in account:
                total_tax += amount * 0.22  # Assuming 22% bracket
            elif account == "taxable":
                total_tax += amount * 0.15  # Long-term gains rate
            # Roth is tax-free

        return total_tax

    def _generate_withdrawal_recommendations(self, age: int, accounts: Dict) -> List[str]:
        """Generate withdrawal strategy recommendations"""
        recommendations = []

        if age < 59.5:
            recommendations.append(
                "Avoid early withdrawal penalties by withdrawing from taxable accounts first"
            )

        if age >= 72:
            recommendations.append("Ensure RMDs are taken from traditional IRA to avoid penalties")

        recommendations.append("Consider Roth conversions in low-income years")
        recommendations.append("Coordinate withdrawals with Social Security timing")

        return recommendations
