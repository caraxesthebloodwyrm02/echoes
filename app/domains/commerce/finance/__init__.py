"""
FinanceAdvisor Module - Comprehensive Financial Intelligence System

This module provides AI-driven financial advisory services for both individuals
and enterprises, covering the complete financial lifecycle from analysis to
actionable recommendations.

Phases:
1. Identification & Analysis
2. Strategy Formulation
3. Smart Prediction & Forecasting
4. Relevant Assignments & Tasks
5. Smart Allocation & Optimization
6. Clear Guidelines & Suggestions
7. Recommendations & Path to Success
"""

from .advisor import FinanceAdvisor
from .api import router as finance_router

__all__ = ["FinanceAdvisor", "finance_router"]
