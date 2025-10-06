#!/usr/bin/env python3
"""
InvestLab Portfolio - Advanced Portfolio Management & Tracking
AI-powered portfolio management, rebalancing, and performance tracking
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from decimal import Decimal
import logging

# Import InvestLab components
from highway import get_highway, DataType
from analytics import get_portfolio_analytics

logger = logging.getLogger(__name__)

@dataclass
class PortfolioHolding:
    """Represents a single portfolio holding"""
    symbol: str
    name: str
    asset_class: str  # stocks, bonds, crypto, commodities, real_estate
    quantity: Decimal
    average_cost: Decimal
    current_price: Decimal
    market_value: Decimal
    unrealized_gain_loss: Decimal
    weight: float
    sector: Optional[str] = None
    country: Optional[str] = None
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class Portfolio:
    """Represents a complete investment portfolio"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    owner_id: str
    account_type: str  # taxable, traditional_ira, roth_ira, 401k, etc.
    holdings: List[PortfolioHolding] = field(default_factory=list)
    total_value: Decimal = Decimal('0.00')
    cash_balance: Decimal = Decimal('0.00')
    day_change: Decimal = Decimal('0.00')
    day_change_percent: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_rebalanced: Optional[datetime] = None
    target_allocation: Dict[str, float] = field(default_factory=dict)
    risk_profile: str = "moderate"  # conservative, moderate, aggressive
    investment_objective: str = "long_term_growth"

@dataclass
class RebalancingRecommendation:
    """Portfolio rebalancing recommendation"""
    portfolio_id: str
    current_allocation: Dict[str, float]
    target_allocation: Dict[str, float]
    trades_required: List[Dict[str, Any]]
    expected_impact: Dict[str, Any]
    tax_implications: Dict[str, Any]
    confidence_score: float
    generated_at: datetime = field(default_factory=datetime.now)

@dataclass
class PerformanceReport:
    """Portfolio performance report"""
    portfolio_id: str
    report_period: str  # 1M, 3M, 6M, 1Y, YTD, etc.
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    benchmark_comparison: Dict[str, float]
    sector_performance: Dict[str, float]
    top_performers: List[Dict[str, Any]]
    underperformers: List[Dict[str, Any]]
    generated_at: datetime = field(default_factory=datetime.now)

class PortfolioManager:
    """Advanced portfolio management and tracking system"""

    def __init__(self):
        self.highway = get_highway()
        self.analytics = get_portfolio_analytics()
        self.portfolios: Dict[str, Portfolio] = {}
        self.price_feeds = self._initialize_price_feeds()
        self.rebalancing_strategies = self._initialize_rebalancing_strategies()

        logger.info("PortfolioManager initialized with advanced portfolio capabilities")

    def _initialize_price_feeds(self) -> Dict[str, Any]:
        """Initialize price data feeds"""
        return {
            'yahoo_finance': {
                'provider': 'Yahoo Finance',
                'asset_types': ['stocks', 'etfs', 'mutual_funds'],
                'real_time': True,
                'historical': True
            },
            'alpha_vantage': {
                'provider': 'Alpha Vantage',
                'asset_types': ['stocks', 'crypto', 'forex'],
                'real_time': True,
                'historical': True
            },
            'polygon': {
                'provider': 'Polygon.io',
                'asset_types': ['stocks', 'options', 'crypto'],
                'real_time': True,
                'historical': True
            },
            'coinbase': {
                'provider': 'Coinbase',
                'asset_types': ['crypto'],
                'real_time': True,
                'historical': True
            }
        }

    def _initialize_rebalancing_strategies(self) -> Dict[str, Any]:
        """Initialize portfolio rebalancing strategies"""
        return {
            'periodic': {
                'frequency': 'quarterly',  # daily, weekly, monthly, quarterly, annually
                'threshold': 0.05,  # 5% deviation trigger
                'method': 'proportional'
            },
            'constant_mix': {
                'frequency': 'monthly',
                'threshold': 0.03,
                'method': 'buy_and_hold'
            },
            'constant_weight': {
                'frequency': 'weekly',
                'threshold': 0.10,
                'method': 'rebalance_to_target'
            },
            'smart_rebalancing': {
                'frequency': 'adaptive',  # AI-driven timing
                'threshold': 0.02,
                'method': 'tax_aware_optimization'
            }
        }

    def create_portfolio(self, name: str, description: str, owner_id: str,
                        account_type: str = "taxable",
                        risk_profile: str = "moderate",
                        initial_deposit: Decimal = Decimal('0.00')) -> Portfolio:
        """Create a new investment portfolio"""
        logger.info(f"Creating portfolio for {owner_id}: {name}")

        # Route portfolio creation through highway
        packet = {
            'type': 'portfolio_creation',
            'name': name,
            'description': description,
            'owner_id': owner_id,
            'account_type': account_type,
            'risk_profile': risk_profile,
            'initial_deposit': float(initial_deposit),
            'creation_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'portfolio_manager')

        # Create portfolio object
        portfolio = Portfolio(
            name=name,
            description=description,
            owner_id=owner_id,
            account_type=account_type,
            risk_profile=risk_profile,
            cash_balance=initial_deposit
        )

        # Set default target allocation based on risk profile
        portfolio.target_allocation = self._get_default_allocation(risk_profile)

        self.portfolios[portfolio.id] = portfolio

        logger.info(f"Portfolio created: {portfolio.id} for {owner_id}")

        return portfolio

    def add_holding(self, portfolio_id: str, symbol: str, quantity: Decimal,
                   purchase_price: Decimal, asset_class: str = "stocks") -> bool:
        """Add a holding to a portfolio"""
        if portfolio_id not in self.portfolios:
            logger.error(f"Portfolio {portfolio_id} not found")
            return False

        portfolio = self.portfolios[portfolio_id]

        # Route holding addition through highway
        packet = {
            'type': 'holding_addition',
            'portfolio_id': portfolio_id,
            'symbol': symbol,
            'quantity': float(quantity),
            'purchase_price': float(purchase_price),
            'asset_class': asset_class,
            'addition_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'portfolio_manager')

        # Get current price (simulated)
        current_price = self._get_current_price(symbol, asset_class)

        # Create holding
        market_value = quantity * current_price
        unrealized_gain_loss = market_value - (quantity * purchase_price)

        holding = PortfolioHolding(
            symbol=symbol,
            name=self._get_asset_name(symbol),
            asset_class=asset_class,
            quantity=quantity,
            average_cost=purchase_price,
            current_price=current_price,
            market_value=market_value,
            unrealized_gain_loss=unrealized_gain_loss,
            weight=0.0  # Will be calculated when portfolio is updated
        )

        portfolio.holdings.append(holding)

        # Update portfolio totals
        self._update_portfolio_totals(portfolio)

        logger.info(f"Holding added to portfolio {portfolio_id}: {symbol} ({quantity} shares)")

        return True

    def update_portfolio_prices(self, portfolio_id: str) -> bool:
        """Update all holdings with latest market prices"""
        if portfolio_id not in self.portfolios:
            logger.error(f"Portfolio {portfolio_id} not found")
            return False

        portfolio = self.portfolios[portfolio_id]

        # Route price update through highway
        packet = {
            'type': 'portfolio_price_update',
            'portfolio_id': portfolio_id,
            'symbols': [h.symbol for h in portfolio.holdings],
            'update_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'portfolio_manager')

        # Update each holding
        total_value = portfolio.cash_balance

        for holding in portfolio.holdings:
            # Get latest price (simulated)
            current_price = self._get_current_price(holding.symbol, holding.asset_class)
            holding.current_price = current_price
            holding.market_value = holding.quantity * current_price
            holding.unrealized_gain_loss = holding.market_value - (holding.quantity * holding.average_cost)
            holding.last_updated = datetime.now()

            total_value += holding.market_value

        # Update portfolio totals
        self._update_portfolio_totals(portfolio)

        logger.info(f"Portfolio {portfolio_id} prices updated")

        return True

    def generate_rebalancing_recommendations(self, portfolio_id: str) -> RebalancingRecommendation:
        """Generate portfolio rebalancing recommendations"""
        if portfolio_id not in self.portfolios:
            raise ValueError(f"Portfolio {portfolio_id} not found")

        portfolio = self.portfolios[portfolio_id]

        # Route rebalancing analysis through highway
        packet = {
            'type': 'rebalancing_analysis',
            'portfolio_id': portfolio_id,
            'current_holdings': [{'symbol': h.symbol, 'weight': h.weight, 'asset_class': h.asset_class}
                               for h in portfolio.holdings],
            'target_allocation': portfolio.target_allocation,
            'analysis_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'portfolio_manager')

        # Calculate current allocation
        current_allocation = self._calculate_asset_allocation(portfolio)

        # Generate trades needed
        trades_required = self._calculate_rebalancing_trades(
            current_allocation, portfolio.target_allocation, portfolio.total_value
        )

        # Estimate impact
        expected_impact = self._estimate_rebalancing_impact(trades_required, portfolio)

        # Assess tax implications
        tax_implications = self._assess_tax_implications(trades_required, portfolio.account_type)

        # Calculate confidence score
        confidence_score = self._calculate_rebalancing_confidence(current_allocation, portfolio.target_allocation)

        recommendation = RebalancingRecommendation(
            portfolio_id=portfolio_id,
            current_allocation=current_allocation,
            target_allocation=portfolio.target_allocation,
            trades_required=trades_required,
            expected_impact=expected_impact,
            tax_implications=tax_implications,
            confidence_score=confidence_score
        )

        logger.info(f"Rebalancing recommendations generated for portfolio {portfolio_id}")

        return recommendation

    def execute_rebalancing(self, portfolio_id: str, recommendation: RebalancingRecommendation) -> Dict[str, Any]:
        """Execute portfolio rebalancing based on recommendations"""
        if portfolio_id not in self.portfolios:
            raise ValueError(f"Portfolio {portfolio_id} not found")

        portfolio = self.portfolios[portfolio_id]

        # Route rebalancing execution through highway
        packet = {
            'type': 'rebalancing_execution',
            'portfolio_id': portfolio_id,
            'recommendation': {
                'trades_required': recommendation.trades_required,
                'expected_impact': recommendation.expected_impact
            },
            'execution_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'portfolio_manager')

        # Simulate trade execution
        executed_trades = []
        total_cost = Decimal('0.00')

        for trade in recommendation.trades_required:
            # Simulate trade execution
            executed_trade = {
                'symbol': trade['symbol'],
                'action': trade['action'],
                'quantity': trade['quantity'],
                'price': trade['estimated_price'],
                'total_value': trade['quantity'] * trade['estimated_price'],
                'executed_at': datetime.now().isoformat()
            }

            executed_trades.append(executed_trade)
            total_cost += executed_trade['total_value']

            # Update portfolio holdings (simplified)
            self._update_holding_after_trade(portfolio, executed_trade)

        # Update portfolio
        portfolio.last_rebalanced = datetime.now()
        self._update_portfolio_totals(portfolio)

        execution_result = {
            'portfolio_id': portfolio_id,
            'executed_trades': executed_trades,
            'total_cost': float(total_cost),
            'execution_time': datetime.now().isoformat(),
            'packet_id': packet_id
        }

        logger.info(f"Portfolio rebalancing executed for {portfolio_id}: {len(executed_trades)} trades")

        return execution_result

    def generate_performance_report(self, portfolio_id: str, period: str = "1Y") -> PerformanceReport:
        """Generate comprehensive portfolio performance report"""
        if portfolio_id not in self.portfolios:
            raise ValueError(f"Portfolio {portfolio_id} not found")

        portfolio = self.portfolios[portfolio_id]

        # Route performance analysis through highway
        packet = {
            'type': 'performance_analysis',
            'portfolio_id': portfolio_id,
            'report_period': period,
            'analysis_requested_at': datetime.now().isoformat()
        }

        packet_id = self.highway.send_to_intelligence(packet, 'portfolio_manager')

        # Calculate performance metrics (simulated)
        total_return = 0.145  # 14.5% total return
        annualized_return = 0.125  # 12.5% annualized
        volatility = 0.18  # 18% volatility
        sharpe_ratio = 1.45  # Sharpe ratio
        max_drawdown = -0.15  # -15% max drawdown

        # Benchmark comparison
        benchmark_comparison = {
            'sp500': -0.02,  # Portfolio outperformed S&P 500 by 2%
            'nasdaq': 0.03,  # Underperformed Nasdaq by 3%
            'dow_jones': -0.01  # Outperformed Dow by 1%
        }

        # Sector performance
        sector_performance = {
            'technology': 0.18,
            'healthcare': 0.12,
            'financials': 0.08,
            'consumer': 0.15,
            'energy': -0.05
        }

        # Top performers and underperformers
        top_performers = [
            {'symbol': 'AAPL', 'return': 0.25, 'contribution': 0.035},
            {'symbol': 'MSFT', 'return': 0.22, 'contribution': 0.028},
            {'symbol': 'NVDA', 'return': 0.35, 'contribution': 0.042}
        ]

        underperformers = [
            {'symbol': 'XOM', 'return': -0.08, 'contribution': -0.012},
            {'symbol': 'GE', 'return': -0.05, 'contribution': -0.008}
        ]

        report = PerformanceReport(
            portfolio_id=portfolio_id,
            report_period=period,
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            benchmark_comparison=benchmark_comparison,
            sector_performance=sector_performance,
            top_performers=top_performers,
            underperformers=underperformers
        )

        logger.info(f"Performance report generated for portfolio {portfolio_id} ({period})")

        return report

    def _get_default_allocation(self, risk_profile: str) -> Dict[str, float]:
        """Get default asset allocation based on risk profile"""
        allocations = {
            'conservative': {
                'bonds': 0.60,
                'stocks': 0.30,
                'cash': 0.10
            },
            'moderate': {
                'stocks': 0.60,
                'bonds': 0.30,
                'international': 0.10
            },
            'aggressive': {
                'stocks': 0.80,
                'international': 0.15,
                'alternatives': 0.05
            }
        }

        return allocations.get(risk_profile, allocations['moderate'])

    def _get_current_price(self, symbol: str, asset_class: str) -> Decimal:
        """Get current market price for a symbol"""
        # Simulate price retrieval
        base_price = Decimal('100.00')

        # Add some random variation
        import random
        variation = Decimal(str(random.uniform(-0.05, 0.05)))
        current_price = base_price * (Decimal('1.0') + variation)

        return current_price.quantize(Decimal('0.01'))

    def _get_asset_name(self, symbol: str) -> str:
        """Get asset name from symbol"""
        # Simulate name lookup
        name_map = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'NVDA': 'NVIDIA Corporation'
        }

        return name_map.get(symbol, f"{symbol} Corporation")

    def _update_portfolio_totals(self, portfolio: Portfolio):
        """Update portfolio totals after changes"""
        total_value = portfolio.cash_balance

        for holding in portfolio.holdings:
            total_value += holding.market_value

        portfolio.total_value = total_value

        # Update holding weights
        for holding in portfolio.holdings:
            holding.weight = float(holding.market_value / total_value) if total_value > 0 else 0.0

    def _calculate_asset_allocation(self, portfolio: Portfolio) -> Dict[str, float]:
        """Calculate current asset allocation"""
        allocation = {}
        total_value = float(portfolio.total_value)

        if total_value == 0:
            return allocation

        for holding in portfolio.holdings:
            asset_class = holding.asset_class
            weight = holding.weight

            if asset_class in allocation:
                allocation[asset_class] += weight
            else:
                allocation[asset_class] = weight

        # Add cash allocation
        cash_weight = float(portfolio.cash_balance / portfolio.total_value)
        if cash_weight > 0:
            allocation['cash'] = cash_weight

        return allocation

    def _calculate_rebalancing_trades(self, current_allocation: Dict[str, float],
                                    target_allocation: Dict[str, float],
                                    total_value: Decimal) -> List[Dict[str, Any]]:
        """Calculate trades needed for rebalancing"""
        trades = []

        for asset_class, target_weight in target_allocation.items():
            current_weight = current_allocation.get(asset_class, 0.0)
            weight_difference = target_weight - current_weight

            if abs(weight_difference) > 0.02:  # Only trade if difference > 2%
                trade_value = weight_difference * float(total_value)

                # Find holdings in this asset class
                relevant_holdings = [h for h in self.portfolios[list(self.portfolios.keys())[0]].holdings
                                   if h.asset_class == asset_class]

                if relevant_holdings:
                    # Use first holding as representative
                    symbol = relevant_holdings[0].symbol
                    estimated_price = float(relevant_holdings[0].current_price)

                    if trade_value > 0:
                        # Buy
                        quantity = trade_value / estimated_price
                        trades.append({
                            'symbol': symbol,
                            'action': 'buy',
                            'quantity': quantity,
                            'estimated_price': estimated_price,
                            'estimated_total': trade_value
                        })
                    else:
                        # Sell
                        quantity = abs(trade_value) / estimated_price
                        trades.append({
                            'symbol': symbol,
                            'action': 'sell',
                            'quantity': quantity,
                            'estimated_price': estimated_price,
                            'estimated_total': abs(trade_value)
                        })

        return trades

    def _estimate_rebalancing_impact(self, trades: List[Dict[str, Any]], portfolio: Portfolio) -> Dict[str, Any]:
        """Estimate the impact of rebalancing trades"""
        total_cost = sum(trade['estimated_total'] for trade in trades)
        expected_risk_change = -0.02  # Slight risk reduction
        expected_return_change = 0.005  # Slight return improvement

        return {
            'total_trading_cost': total_cost,
            'expected_risk_change': expected_risk_change,
            'expected_return_change': expected_return_change,
            'estimated_completion_time': '2-3 business days',
            'market_impact_assessment': 'minimal'
        }

    def _assess_tax_implications(self, trades: List[Dict[str, Any]], account_type: str) -> Dict[str, Any]:
        """Assess tax implications of rebalancing trades"""
        if account_type in ['traditional_ira', 'roth_ira', '401k']:
            # Tax-deferred or tax-free accounts
            return {
                'tax_liability': 0.0,
                'capital_gains_tax': 0.0,
                'tax_efficiency_score': 1.0,
                'recommendation': 'No tax implications in tax-advantaged account'
            }
        else:
            # Taxable account
            estimated_gains = sum(trade['estimated_total'] * 0.15 for trade in trades if trade['action'] == 'sell')
            return {
                'tax_liability': estimated_gains,
                'capital_gains_tax': 0.15,  # Assumed 15% rate
                'tax_efficiency_score': 0.85,
                'recommendation': 'Consider tax-loss harvesting opportunities'
            }

    def _calculate_rebalancing_confidence(self, current: Dict[str, float], target: Dict[str, float]) -> float:
        """Calculate confidence score for rebalancing recommendations"""
        # Simple confidence calculation based on allocation differences
        total_difference = sum(abs(current.get(k, 0) - v) for k, v in target.items())
        confidence = max(0.0, 1.0 - total_difference)  # Higher difference = lower confidence

        return round(confidence, 2)

    def _update_holding_after_trade(self, portfolio: Portfolio, trade: Dict[str, Any]):
        """Update portfolio holdings after trade execution"""
        symbol = trade['symbol']
        action = trade['action']
        quantity = trade['quantity']
        price = trade['price']

        # Find or create holding
        holding = None
        for h in portfolio.holdings:
            if h.symbol == symbol:
                holding = h
                break

        if not holding:
            # Create new holding for buy orders
            holding = PortfolioHolding(
                symbol=symbol,
                name=self._get_asset_name(symbol),
                asset_class='stocks',  # Assume stocks for simplicity
                quantity=Decimal('0'),
                average_cost=Decimal('0'),
                current_price=Decimal(str(price)),
                market_value=Decimal('0'),
                unrealized_gain_loss=Decimal('0'),
                weight=0.0
            )
            portfolio.holdings.append(holding)

        if action == 'buy':
            # Update average cost and quantity
            total_cost = (holding.quantity * holding.average_cost) + (Decimal(str(quantity)) * Decimal(str(price)))
            holding.quantity += Decimal(str(quantity))
            if holding.quantity > 0:
                holding.average_cost = total_cost / holding.quantity

        elif action == 'sell':
            # Reduce quantity (simplified - doesn't handle cost basis properly)
            holding.quantity -= Decimal(str(quantity))
            if holding.quantity <= 0:
                # Remove holding if fully sold
                portfolio.holdings.remove(holding)

        # Update portfolio totals
        self._update_portfolio_totals(portfolio)

# Global portfolio manager instance
portfolio_manager = PortfolioManager()

def get_portfolio_manager() -> PortfolioManager:
    """Get the global portfolio manager instance"""
    return portfolio_manager

# Convenience functions
def create_portfolio(name: str, description: str, owner_id: str, account_type: str = "taxable", risk_profile: str = "moderate") -> Portfolio:
    """Create a new investment portfolio"""
    return portfolio_manager.create_portfolio(name, description, owner_id, account_type, risk_profile)

def add_portfolio_holding(portfolio_id: str, symbol: str, quantity: Decimal, purchase_price: Decimal, asset_class: str = "stocks") -> bool:
    """Add a holding to a portfolio"""
    return portfolio_manager.add_holding(portfolio_id, symbol, quantity, purchase_price, asset_class)

def update_portfolio_prices(portfolio_id: str) -> bool:
    """Update portfolio with latest prices"""
    return portfolio_manager.update_portfolio_prices(portfolio_id)

def get_rebalancing_recommendations(portfolio_id: str) -> RebalancingRecommendation:
    """Get portfolio rebalancing recommendations"""
    return portfolio_manager.generate_rebalancing_recommendations(portfolio_id)

def execute_portfolio_rebalancing(portfolio_id: str, recommendation: RebalancingRecommendation) -> Dict[str, Any]:
    """Execute portfolio rebalancing"""
    return portfolio_manager.execute_rebalancing(portfolio_id, recommendation)

def generate_portfolio_report(portfolio_id: str, period: str = "1Y") -> PerformanceReport:
    """Generate portfolio performance report"""
    return portfolio_manager.generate_performance_report(portfolio_id, period)
