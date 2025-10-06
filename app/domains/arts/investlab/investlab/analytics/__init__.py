#!/usr/bin/env python3
"""
InvestLab Analytics - Advanced Portfolio Analytics & Risk Assessment
AI-powered investment analytics and portfolio optimization platform
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging

# Import InvestLab components
from highway import get_highway, DataType

logger = logging.getLogger(__name__)


@dataclass
class PortfolioMetrics:
    """Comprehensive portfolio performance metrics"""

    total_value: float
    daily_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    beta: float
    alpha: float
    sortino_ratio: float
    information_ratio: float
    tracking_error: float
    calculated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment"""

    value_at_risk: float  # VaR at 95% confidence
    expected_shortfall: float  # CVaR
    stress_test_results: Dict[str, float]
    scenario_analysis: Dict[str, Dict[str, float]]
    liquidity_risk: str
    concentration_risk: float
    tail_risk: float
    systemic_risk: float
    assessed_at: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationResult:
    """Portfolio optimization results"""

    optimal_weights: Dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    efficient_frontier: List[Dict[str, float]]
    constraints_satisfied: bool
    optimization_method: str
    optimized_at: datetime = field(default_factory=datetime.now)


class PortfolioAnalytics:
    """Advanced portfolio analytics and optimization"""

    def __init__(self):
        self.highway = get_highway()
        self.risk_models = self._initialize_risk_models()
        self.optimization_engines = self._initialize_optimization_engines()
        self.performance_calculators = self._initialize_performance_calculators()

        logger.info("PortfolioAnalytics initialized with advanced analytics capabilities")

    def _initialize_risk_models(self) -> Dict[str, Any]:
        """Initialize risk assessment models"""
        return {
            "historical_simulation": {
                "method": "bootstrap",
                "confidence_levels": [0.95, 0.99],
                "lookback_periods": [252, 504],  # Trading days
            },
            "parametric_models": {
                "distributions": ["normal", "t_distribution", "skewed_normal"],
                "volatility_models": ["garch", "ewma", "historical"],
            },
            "monte_carlo": {
                "simulations": 10000,
                "time_horizon": [30, 90, 252],  # Days
                "scenarios": ["baseline", "stressed", "crisis"],
            },
            "factor_models": {
                "factors": ["market", "size", "value", "momentum", "quality"],
                "estimation_method": "robust_regression",
            },
        }

    def _initialize_optimization_engines(self) -> Dict[str, Any]:
        """Initialize portfolio optimization engines"""
        return {
            "mean_variance": {
                "method": "quadratic_programming",
                "objectives": ["max_sharpe", "min_volatility", "target_return"],
                "constraints": ["budget", "bounds", "turnover", "tracking_error"],
            },
            "black_litterman": {
                "views": "investor_views",
                "confidence_intervals": [0.1, 0.5],
                "tau": 0.05,
            },
            "risk_parity": {
                "method": "equal_risk_contribution",
                "rebalancing_frequency": "monthly",
                "risk_measure": "volatility",
            },
            "robust_optimization": {
                "method": "worst_case",
                "uncertainty_sets": ["box", "elliptical"],
                "confidence_level": 0.95,
            },
        }

    def _initialize_performance_calculators(self) -> Dict[str, Any]:
        """Initialize performance calculation methods"""
        return {
            "returns": {
                "methods": ["arithmetic", "geometric", "time_weighted"],
                "frequencies": ["daily", "weekly", "monthly", "quarterly", "annual"],
            },
            "risk_metrics": {
                "volatility_measures": ["standard_deviation", "downside_deviation"],
                "risk_adjusted_returns": ["sharpe", "sortino", "information_ratio"],
                "drawdown_measures": ["max_drawdown", "average_drawdown", "drawdown_duration"],
            },
            "benchmarking": {
                "benchmarks": ["sp500", "nasdaq", "dow_jones", "custom_index"],
                "comparison_metrics": ["alpha", "beta", "tracking_error", "information_ratio"],
            },
        }

    def calculate_portfolio_metrics(
        self, portfolio_data: Dict[str, Any], benchmark_data: Optional[Dict[str, Any]] = None
    ) -> PortfolioMetrics:
        """Calculate comprehensive portfolio performance metrics"""
        logger.info("Calculating portfolio performance metrics")

        # Route calculation request through highway
        packet = {
            "type": "portfolio_metrics_calculation",
            "portfolio_data": portfolio_data,
            "benchmark_data": benchmark_data,
            "calculation_requested_at": datetime.now().isoformat(),
        }

        packet_id = self.highway.send_to_intelligence(packet, "portfolio_analytics")

        # Extract portfolio data
        holdings = portfolio_data.get("holdings", [])
        total_value = portfolio_data.get("total_value", 0.0)

        # Calculate returns
        daily_return = self._calculate_daily_return(holdings)

        # Calculate risk metrics
        volatility = self._calculate_volatility(holdings)
        sharpe_ratio = self._calculate_sharpe_ratio(daily_return, volatility)
        max_drawdown = self._calculate_max_drawdown(holdings)

        # Calculate market sensitivity
        beta = self._calculate_beta(holdings, benchmark_data)
        alpha = self._calculate_alpha(daily_return, beta, benchmark_data)

        # Calculate additional risk-adjusted returns
        sortino_ratio = self._calculate_sortino_ratio(daily_return, holdings)
        information_ratio = self._calculate_information_ratio(daily_return, benchmark_data)
        tracking_error = self._calculate_tracking_error(daily_return, benchmark_data)

        metrics = PortfolioMetrics(
            total_value=total_value,
            daily_return=daily_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            beta=beta,
            alpha=alpha,
            sortino_ratio=sortino_ratio,
            information_ratio=information_ratio,
            tracking_error=tracking_error,
        )

        logger.info(
            f"Portfolio metrics calculated: Sharpe {sharpe_ratio:.2f}, MaxDD {max_drawdown:.2%}"
        )

        return metrics

    def assess_portfolio_risk(
        self, portfolio_data: Dict[str, Any], market_conditions: Dict[str, Any]
    ) -> RiskAssessment:
        """Perform comprehensive portfolio risk assessment"""
        logger.info("Performing comprehensive portfolio risk assessment")

        # Route risk assessment through highway
        packet = {
            "type": "portfolio_risk_assessment",
            "portfolio_data": portfolio_data,
            "market_conditions": market_conditions,
            "assessment_requested_at": datetime.now().isoformat(),
        }

        packet_id = self.highway.send_to_intelligence(packet, "portfolio_analytics")

        # Extract portfolio holdings
        holdings = portfolio_data.get("holdings", [])

        # Calculate Value at Risk (VaR)
        value_at_risk = self._calculate_var(holdings, confidence=0.95)

        # Calculate Expected Shortfall (CVaR)
        expected_shortfall = self._calculate_cvar(holdings, confidence=0.95)

        # Perform stress testing
        stress_test_results = self._perform_stress_testing(holdings, market_conditions)

        # Perform scenario analysis
        scenario_analysis = self._perform_scenario_analysis(holdings, market_conditions)

        # Assess liquidity risk
        liquidity_risk = self._assess_liquidity_risk(holdings)

        # Calculate concentration risk
        concentration_risk = self._calculate_concentration_risk(holdings)

        # Assess tail risk
        tail_risk = self._assess_tail_risk(holdings)

        # Assess systemic risk
        systemic_risk = self._assess_systemic_risk(holdings, market_conditions)

        assessment = RiskAssessment(
            value_at_risk=value_at_risk,
            expected_shortfall=expected_shortfall,
            stress_test_results=stress_test_results,
            scenario_analysis=scenario_analysis,
            liquidity_risk=liquidity_risk,
            concentration_risk=concentration_risk,
            tail_risk=tail_risk,
            systemic_risk=systemic_risk,
        )

        logger.info(
            f"Risk assessment completed: VaR {value_at_risk:.2%}, Systemic Risk {systemic_risk:.2f}"
        )

        return assessment

    def optimize_portfolio(
        self,
        portfolio_data: Dict[str, Any],
        constraints: Dict[str, Any],
        optimization_method: str = "mean_variance",
    ) -> OptimizationResult:
        """Optimize portfolio allocation using advanced algorithms"""
        logger.info(f"Optimizing portfolio using {optimization_method}")

        # Route optimization request through highway
        packet = {
            "type": "portfolio_optimization",
            "portfolio_data": portfolio_data,
            "constraints": constraints,
            "optimization_method": optimization_method,
            "optimization_requested_at": datetime.now().isoformat(),
        }

        packet_id = self.highway.send_to_intelligence(packet, "portfolio_analytics")

        # Extract portfolio and market data
        holdings = portfolio_data.get("holdings", [])
        expected_returns = self._estimate_expected_returns(holdings)
        covariance_matrix = self._estimate_covariance_matrix(holdings)

        # Perform optimization based on method
        if optimization_method == "mean_variance":
            (
                optimal_weights,
                expected_return,
                expected_volatility,
                sharpe,
            ) = self._optimize_mean_variance(expected_returns, covariance_matrix, constraints)
        elif optimization_method == "risk_parity":
            (
                optimal_weights,
                expected_return,
                expected_volatility,
                sharpe,
            ) = self._optimize_risk_parity(expected_returns, covariance_matrix, constraints)
        else:
            # Default to mean-variance
            (
                optimal_weights,
                expected_return,
                expected_volatility,
                sharpe,
            ) = self._optimize_mean_variance(expected_returns, covariance_matrix, constraints)

        # Generate efficient frontier
        efficient_frontier = self._calculate_efficient_frontier(
            expected_returns, covariance_matrix, constraints
        )

        # Check if constraints are satisfied
        constraints_satisfied = self._validate_constraints(optimal_weights, constraints)

        result = OptimizationResult(
            optimal_weights=optimal_weights,
            expected_return=expected_return,
            expected_volatility=expected_volatility,
            sharpe_ratio=sharpe,
            efficient_frontier=efficient_frontier,
            constraints_satisfied=constraints_satisfied,
            optimization_method=optimization_method,
        )

        logger.info(
            f"Portfolio optimization completed: Expected return {expected_return:.2%}, Sharpe {sharpe:.2f}"
        )

        return result

    def analyze_asset_correlations(
        self, assets: List[str], lookback_period: int = 252
    ) -> pd.DataFrame:
        """Analyze correlations between assets"""
        logger.info(f"Analyzing correlations for {len(assets)} assets")

        # Route correlation analysis through highway
        packet = {
            "type": "correlation_analysis",
            "assets": assets,
            "lookback_period": lookback_period,
            "analysis_requested_at": datetime.now().isoformat(),
        }

        packet_id = self.highway.send_to_intelligence(packet, "portfolio_analytics")

        # Simulate correlation matrix (would use real market data)
        np.random.seed(42)
        correlation_matrix = np.random.uniform(-0.5, 0.8, (len(assets), len(assets)))
        # Make it symmetric
        correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
        # Set diagonal to 1
        np.fill_diagonal(correlation_matrix, 1.0)

        # Create DataFrame
        corr_df = pd.DataFrame(correlation_matrix, index=assets, columns=assets)

        logger.info(f"Correlation analysis completed for {len(assets)} assets")

        return corr_df

    def perform_factor_analysis(
        self, portfolio_data: Dict[str, Any], factors: List[str] = None
    ) -> Dict[str, Any]:
        """Perform multi-factor risk analysis"""
        if factors is None:
            factors = ["market", "size", "value", "momentum", "quality"]

        logger.info(f"Performing factor analysis with {len(factors)} factors")

        # Route factor analysis through highway
        packet = {
            "type": "factor_analysis",
            "portfolio_data": portfolio_data,
            "factors": factors,
            "analysis_requested_at": datetime.now().isoformat(),
        }

        packet_id = self.highway.send_to_intelligence(packet, "portfolio_analytics")

        # Simulate factor analysis results
        factor_loadings = {factor: np.random.normal(0, 0.5) for factor in factors}
        factor_returns = {factor: np.random.normal(0.08, 0.15) for factor in factors}
        unexplained_variance = 0.25
        r_squared = 1 - unexplained_variance

        results = {
            "factor_loadings": factor_loadings,
            "factor_returns": factor_returns,
            "r_squared": r_squared,
            "unexplained_variance": unexplained_variance,
            "alpha": np.random.normal(0.02, 0.01),
            "factors_used": factors,
        }

        logger.info(f"Factor analysis completed: R² = {r_squared:.2f}")

        return results

    def _calculate_daily_return(self, holdings: List[Dict]) -> float:
        """Calculate portfolio daily return"""
        # Simulate calculation
        return 0.0012  # 0.12% daily return

    def _calculate_volatility(self, holdings: List[Dict]) -> float:
        """Calculate portfolio volatility"""
        # Simulate calculation
        return 0.15  # 15% annual volatility

    def _calculate_sharpe_ratio(self, daily_return: float, volatility: float) -> float:
        """Calculate Sharpe ratio"""
        risk_free_rate = 0.02  # 2% risk-free rate
        return (daily_return * 252 - risk_free_rate) / (volatility * np.sqrt(252))

    def _calculate_max_drawdown(self, holdings: List[Dict]) -> float:
        """Calculate maximum drawdown"""
        # Simulate calculation
        return -0.18  # -18% max drawdown

    def _calculate_beta(self, holdings: List[Dict], benchmark_data: Optional[Dict]) -> float:
        """Calculate portfolio beta"""
        # Simulate calculation
        return 1.05  # Slightly more volatile than market

    def _calculate_alpha(
        self, daily_return: float, beta: float, benchmark_data: Optional[Dict]
    ) -> float:
        """Calculate alpha (excess return)"""
        # Simulate calculation
        return 0.025  # 2.5% alpha

    def _calculate_sortino_ratio(self, daily_return: float, holdings: List[Dict]) -> float:
        """Calculate Sortino ratio (downside deviation)"""
        # Simulate calculation
        downside_volatility = 0.12  # Lower than total volatility
        risk_free_rate = 0.02
        return (daily_return * 252 - risk_free_rate) / (downside_volatility * np.sqrt(252))

    def _calculate_information_ratio(
        self, daily_return: float, benchmark_data: Optional[Dict]
    ) -> float:
        """Calculate information ratio"""
        # Simulate calculation
        tracking_error = 0.08
        return (daily_return * 252 - 0.08) / tracking_error  # Benchmark return 8%

    def _calculate_tracking_error(
        self, daily_return: float, benchmark_data: Optional[Dict]
    ) -> float:
        """Calculate tracking error"""
        # Simulate calculation
        return 0.08  # 8% tracking error

    def _calculate_var(self, holdings: List[Dict], confidence: float = 0.95) -> float:
        """Calculate Value at Risk"""
        # Simulate VaR calculation
        return -0.085  # -8.5% VaR at 95% confidence

    def _calculate_cvar(self, holdings: List[Dict], confidence: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        # Simulate CVaR calculation
        return -0.12  # -12% expected shortfall

    def _perform_stress_testing(
        self, holdings: List[Dict], market_conditions: Dict
    ) -> Dict[str, float]:
        """Perform stress testing under various scenarios"""
        # Simulate stress test results
        scenarios = {
            "market_crash": -0.25,
            "interest_rate_hike": -0.15,
            "geopolitical_crisis": -0.20,
            "sector_recession": -0.18,
        }
        return scenarios

    def _perform_scenario_analysis(
        self, holdings: List[Dict], market_conditions: Dict
    ) -> Dict[str, Dict[str, float]]:
        """Perform scenario analysis"""
        # Simulate scenario analysis
        scenarios = {
            "bull_market": {"return": 0.25, "volatility": 0.18},
            "bear_market": {"return": -0.15, "volatility": 0.35},
            "sideways_market": {"return": 0.05, "volatility": 0.12},
            "high_inflation": {"return": -0.08, "volatility": 0.28},
        }
        return scenarios

    def _assess_liquidity_risk(self, holdings: List[Dict]) -> str:
        """Assess portfolio liquidity risk"""
        # Simulate liquidity assessment
        return "moderate"  # Options: low, moderate, high

    def _calculate_concentration_risk(self, holdings: List[Dict]) -> float:
        """Calculate portfolio concentration risk"""
        # Simulate concentration risk calculation
        return 0.65  # 65% concentration risk score

    def _assess_tail_risk(self, holdings: List[Dict]) -> float:
        """Assess tail risk (extreme events)"""
        # Simulate tail risk assessment
        return 0.15  # 15% tail risk probability

    def _assess_systemic_risk(self, holdings: List[Dict], market_conditions: Dict) -> float:
        """Assess systemic risk exposure"""
        # Simulate systemic risk assessment
        return 0.45  # 45% systemic risk exposure

    def _estimate_expected_returns(self, holdings: List[Dict]) -> Dict[str, float]:
        """Estimate expected returns for portfolio assets"""
        # Simulate expected returns
        assets = [h.get("symbol", f"asset_{i}") for i, h in enumerate(holdings)]
        expected_returns = {asset: np.random.normal(0.10, 0.03) for asset in assets}
        return expected_returns

    def _estimate_covariance_matrix(self, holdings: List[Dict]) -> pd.DataFrame:
        """Estimate covariance matrix for portfolio assets"""
        assets = [h.get("symbol", f"asset_{i}") for i, h in enumerate(holdings)]
        n_assets = len(assets)

        # Simulate covariance matrix
        np.random.seed(42)
        cov_matrix = np.random.uniform(0.02, 0.15, (n_assets, n_assets))
        # Make it symmetric
        cov_matrix = (cov_matrix + cov_matrix.T) / 2
        # Set reasonable diagonal values (variances)
        for i in range(n_assets):
            cov_matrix[i, i] = np.random.uniform(0.04, 0.25)

        return pd.DataFrame(cov_matrix, index=assets, columns=assets)

    def _optimize_mean_variance(
        self,
        expected_returns: Dict[str, float],
        cov_matrix: pd.DataFrame,
        constraints: Dict[str, Any],
    ) -> Tuple[Dict[str, float], float, float, float]:
        """Perform mean-variance portfolio optimization"""
        assets = list(expected_returns.keys())
        n_assets = len(assets)

        # Simulate optimal weights
        weights = np.random.dirichlet(np.ones(n_assets))
        optimal_weights = {asset: weight for asset, weight in zip(assets, weights)}

        # Calculate portfolio metrics
        expected_return = sum(
            expected_returns[asset] * weight for asset, weight in optimal_weights.items()
        )
        expected_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix.values, weights)))
        sharpe_ratio = (expected_return - 0.02) / expected_volatility  # Risk-free rate = 2%

        return optimal_weights, expected_return, expected_volatility, sharpe_ratio

    def _optimize_risk_parity(
        self,
        expected_returns: Dict[str, float],
        cov_matrix: pd.DataFrame,
        constraints: Dict[str, Any],
    ) -> Tuple[Dict[str, float], float, float, float]:
        """Perform risk parity portfolio optimization"""
        assets = list(expected_returns.keys())
        n_assets = len(assets)

        # Simulate risk parity weights (equal risk contribution)
        volatilities = np.sqrt(np.diag(cov_matrix.values))
        inverse_volatilities = 1 / volatilities
        weights = inverse_volatilities / np.sum(inverse_volatilities)
        optimal_weights = {asset: weight for asset, weight in zip(assets, weights)}

        # Calculate portfolio metrics
        expected_return = sum(
            expected_returns[asset] * weight for asset, weight in optimal_weights.items()
        )
        expected_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix.values, weights)))
        sharpe_ratio = (expected_return - 0.02) / expected_volatility

        return optimal_weights, expected_return, expected_volatility, sharpe_ratio

    def _calculate_efficient_frontier(
        self,
        expected_returns: Dict[str, float],
        cov_matrix: pd.DataFrame,
        constraints: Dict[str, Any],
    ) -> List[Dict[str, float]]:
        """Calculate efficient frontier points"""
        # Simulate efficient frontier
        frontier_points = []
        for target_return in np.linspace(0.05, 0.20, 10):
            # Simulate optimal portfolio for this return target
            weights = np.random.dirichlet(np.ones(len(expected_returns)))
            volatility = np.random.uniform(0.10, 0.25)
            frontier_points.append(
                {
                    "target_return": target_return,
                    "expected_volatility": volatility,
                    "sharpe_ratio": (target_return - 0.02) / volatility,
                }
            )

        return frontier_points

    def _validate_constraints(self, weights: Dict[str, float], constraints: Dict[str, Any]) -> bool:
        """Validate that optimization constraints are satisfied"""
        # Simulate constraint validation
        total_weight = sum(weights.values())
        weight_bounds = constraints.get("weight_bounds", {})

        # Check budget constraint
        if not abs(total_weight - 1.0) < 0.01:
            return False

        # Check individual weight bounds
        for asset, weight in weights.items():
            min_weight = weight_bounds.get(asset, {}).get("min", 0.0)
            max_weight = weight_bounds.get(asset, {}).get("max", 1.0)
            if not (min_weight <= weight <= max_weight):
                return False

        return True


# Global portfolio analytics instance
portfolio_analytics = PortfolioAnalytics()


def get_portfolio_analytics() -> PortfolioAnalytics:
    """Get the global portfolio analytics instance"""
    return portfolio_analytics


# Convenience functions
def calculate_portfolio_metrics(
    portfolio_data: Dict[str, Any], benchmark_data: Optional[Dict[str, Any]] = None
) -> PortfolioMetrics:
    """Calculate portfolio performance metrics"""
    return portfolio_analytics.calculate_portfolio_metrics(portfolio_data, benchmark_data)


def assess_portfolio_risk(
    portfolio_data: Dict[str, Any], market_conditions: Dict[str, Any]
) -> RiskAssessment:
    """Assess portfolio risk"""
    return portfolio_analytics.assess_portfolio_risk(portfolio_data, market_conditions)


def optimize_portfolio(
    portfolio_data: Dict[str, Any], constraints: Dict[str, Any], method: str = "mean_variance"
) -> OptimizationResult:
    """Optimize portfolio allocation"""
    return portfolio_analytics.optimize_portfolio(portfolio_data, constraints, method)


def analyze_asset_correlations(assets: List[str], lookback_period: int = 252) -> pd.DataFrame:
    """Analyze correlations between assets"""
    return portfolio_analytics.analyze_asset_correlations(assets, lookback_period)


def perform_factor_analysis(
    portfolio_data: Dict[str, Any], factors: List[str] = None
) -> Dict[str, Any]:
    """Perform multi-factor risk analysis"""
    return portfolio_analytics.perform_factor_analysis(portfolio_data, factors)
