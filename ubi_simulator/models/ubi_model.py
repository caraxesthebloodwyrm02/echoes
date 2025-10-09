"""
UBI Simulation Engine: Economic modeling framework
Core insight: Flexible simulation allowing policy-makers to explore UBI scenarios
"""

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd


@dataclass
class UBIParameters:
    """Universal Basic Income policy parameters"""

    ubi_amount: float  # Monthly UBI amount per person
    eligibility_threshold: float  # Income threshold for full UBI
    phase_out_rate: float  # Rate at which UBI decreases with income
    funding_mechanism: str  # 'tax', 'deficit', 'reallocation'
    tax_rate: float  # Additional tax rate for funding (if applicable)


@dataclass
class SimulationResults:
    """Comprehensive simulation results"""

    total_cost: float
    avg_ubi_received: float
    employment_change: float
    gdp_impact: float
    poverty_reduction: float
    gini_coefficient: float
    regional_breakdown: Dict[str, Dict[str, float]]


class UBISimulator:
    """
    Economic modeling engine for UBI policy simulation.
    Core capability: Explore "what if" scenarios across demographics and regions.
    """

    def __init__(
        self,
        census_data: pd.DataFrame,
        cost_data: pd.DataFrame,
        employment_data: pd.DataFrame,
    ):
        self.census_data = census_data.copy()
        self.cost_data = cost_data.copy()
        self.employment_data = employment_data.copy()
        self.baseline_metrics = self._calculate_baseline_metrics()

    def simulate_ubi(self, params: UBIParameters) -> SimulationResults:
        """
        Run comprehensive UBI simulation with behavioral and economic effects.
        This is the core engine - where policy parameters meet economic reality.
        """

        # Calculate UBI payments for each household
        ubi_payments = self._calculate_ubi_payments(params)

        # Calculate total program cost
        total_cost = ubi_payments.sum()

        # Model behavioral effects (employment changes)
        employment_change = self._calculate_employment_effects(params, ubi_payments)

        # Calculate macroeconomic impacts
        gdp_impact = self._calculate_gdp_impact(ubi_payments, employment_change)

        # Assess distributional effects
        poverty_reduction = self._calculate_poverty_reduction(ubi_payments)
        gini_coefficient = self._calculate_gini_coefficient(ubi_payments)

        # Regional analysis
        regional_breakdown = self._calculate_regional_breakdown(ubi_payments)

        # Average UBI received
        avg_ubi_received = ubi_payments.mean()

        return SimulationResults(
            total_cost=total_cost,
            avg_ubi_received=avg_ubi_received,
            employment_change=employment_change,
            gdp_impact=gdp_impact,
            poverty_reduction=poverty_reduction,
            gini_coefficient=gini_coefficient,
            regional_breakdown=regional_breakdown,
        )

    def _calculate_baseline_metrics(self) -> Dict:
        """Calculate baseline economic metrics before UBI"""
        median_income = self.census_data["income"].median()
        return {
            "baseline_gini": self._gini(self.census_data["income"].values),
            "baseline_poverty_rate": self._calculate_poverty_rate_static(
                self.census_data["income"], median_income
            ),
            "total_population": len(self.census_data),
            "median_income": median_income,
            "mean_income": self.census_data["income"].mean(),
        }

    def _calculate_poverty_rate_static(
        self, income_series: pd.Series, median_income: float
    ) -> float:
        """Helper: Calculate poverty rate with explicit median income"""
        poverty_line = median_income * 0.6
        poverty_count = (income_series < poverty_line).sum()
        return poverty_count / len(income_series)

    def _calculate_ubi_payments(self, params: UBIParameters) -> pd.Series:
        """
        Calculate UBI payments with progressive phase-out.
        Core logic: UBI amount decreases as income increases.
        """

        def calculate_payment(income: float, household_size: int) -> float:
            # Adjust for household size (simplified - could be more sophisticated)
            adjusted_income = income / np.sqrt(household_size)

            if adjusted_income <= params.eligibility_threshold:
                # Full UBI for low-income households
                return params.ubi_amount * household_size
            else:
                # Phase out UBI based on income above threshold
                excess_income = adjusted_income - params.eligibility_threshold
                reduction = excess_income * params.phase_out_rate
                payment = max(0, params.ubi_amount - reduction)
                return payment * household_size

        # Calculate payments for each household
        payments = self.census_data.apply(
            lambda row: calculate_payment(row["income"], row["household_size"]), axis=1
        )

        return payments

    def _calculate_employment_effects(
        self, params: UBIParameters, ubi_payments: pd.Series
    ) -> float:
        """
        Estimate employment effects using labor supply elasticity.
        Core insight: UBI may reduce work incentives, but effects vary by income level.
        """

        # Simplified model: Higher UBI amounts and lower phase-out rates reduce work more
        base_employment = len(
            self.census_data[self.census_data["employment_status"] == "Employed"]
        )

        # Calculate average UBI as % of median income
        avg_ubi_annual = ubi_payments.mean() * 12
        ubi_to_income_ratio = avg_ubi_annual / self.baseline_metrics["median_income"]

        # Employment elasticity: 2% reduction per 10% of median income in UBI
        employment_reduction_rate = ubi_to_income_ratio * 0.2

        # Phase-out rate effect: Higher phase-out = less work disincentive
        phase_out_effect = (1 - params.phase_out_rate) * 0.5

        total_reduction_rate = employment_reduction_rate * (1 + phase_out_effect)

        # Cap at 5% maximum reduction (realistic upper bound)
        total_reduction_rate = min(total_reduction_rate, 0.05)

        employment_change = -base_employment * total_reduction_rate

        return employment_change  # Negative = reduction in employment

    def _calculate_gdp_impact(
        self, ubi_payments: pd.Series, employment_change: float
    ) -> float:
        """
        Calculate GDP impact through spending multiplier and employment effects.
        Core equation: Direct spending + employment effect on productivity.
        """

        # Multiplier effect: UBI spending generates economic activity
        annual_ubi_spending = ubi_payments.sum() * 12

        # Conservative multiplier (each $1 of UBI generates $1.50 of economic activity)
        spending_multiplier = 1.5
        direct_gdp_impact = annual_ubi_spending * (spending_multiplier - 1)

        # Employment effect: Lost productivity from reduced work
        avg_productivity_per_worker = (
            self.baseline_metrics["mean_income"] * 0.8
        )  # 80% of income is productivity
        employment_gdp_loss = abs(employment_change) * avg_productivity_per_worker

        total_gdp_impact = direct_gdp_impact - employment_gdp_loss

        return total_gdp_impact

    def _calculate_poverty_reduction(self, ubi_payments: pd.Series) -> float:
        """
        Calculate poverty reduction effect.
        Core metric: Percentage point reduction in poverty rate.
        """

        # Define poverty line (60% of median income - EU standard)
        poverty_line = self.baseline_metrics["median_income"] * 0.6

        # Calculate baseline poverty
        baseline_poverty_count = (self.census_data["income"] < poverty_line).sum()
        baseline_poverty_rate = baseline_poverty_count / len(self.census_data)

        # Calculate poverty after UBI (annualize UBI)
        new_income = self.census_data["income"] + (ubi_payments * 12)
        new_poverty_count = (new_income < poverty_line).sum()
        new_poverty_rate = new_poverty_count / len(self.census_data)

        # Return percentage point reduction
        poverty_reduction = (baseline_poverty_rate - new_poverty_rate) * 100

        return poverty_reduction

    def _calculate_gini_coefficient(self, ubi_payments: pd.Series) -> float:
        """
        Calculate Gini coefficient after UBI redistribution.
        Core insight: UBI reduces income inequality.
        """

        # Calculate new income distribution
        new_income = self.census_data["income"] + (ubi_payments * 12)

        # Calculate Gini coefficient
        gini = self._gini(new_income.values)

        return gini

    def _gini(self, income: np.ndarray) -> float:
        """Calculate Gini coefficient for income distribution"""
        sorted_income = np.sort(income)
        n = len(sorted_income)
        index = np.arange(1, n + 1)
        return (np.sum((2 * index - n - 1) * sorted_income)) / (
            n * np.sum(sorted_income)
        )

    def _calculate_poverty_rate(self, income_series: pd.Series) -> float:
        """Helper: Calculate poverty rate"""
        poverty_line = self.baseline_metrics["median_income"] * 0.6
        poverty_count = (income_series < poverty_line).sum()
        return poverty_count / len(income_series)

    def _calculate_regional_breakdown(
        self, ubi_payments: pd.Series
    ) -> Dict[str, Dict[str, float]]:
        """Calculate regional effects of UBI policy"""

        regional_breakdown = {}

        for region in self.census_data["region"].unique():
            region_data = self.census_data[self.census_data["region"] == region]
            region_payments = ubi_payments[region_data.index]

            # Adjust for regional cost of living
            col_index = self.cost_data[self.cost_data["region"] == region][
                "cost_of_living_index"
            ].iloc[0]
            adjusted_payments = region_payments / (col_index / 100)  # Normalize to 100

            regional_breakdown[region] = {
                "total_cost": region_payments.sum(),
                "avg_payment": region_payments.mean(),
                "households": len(region_data),
                "adjusted_avg_payment": adjusted_payments.mean(),
                "poverty_reduction": self._calculate_poverty_reduction(region_payments),
            }

        return regional_breakdown

    def compare_scenarios(
        self, scenario1: UBIParameters, scenario2: UBIParameters
    ) -> Dict:
        """
        Compare two UBI scenarios side-by-side.
        Useful for policy analysis and decision-making.
        """

        results1 = self.simulate_ubi(scenario1)
        results2 = self.simulate_ubi(scenario2)

        comparison = {
            "cost_difference": results2.total_cost - results1.total_cost,
            "efficiency_ratio": (
                results2.total_cost / results1.total_cost
                if results1.total_cost > 0
                else 0
            ),
            "poverty_reduction_diff": results2.poverty_reduction
            - results1.poverty_reduction,
            "gini_improvement": results1.gini_coefficient
            - results2.gini_coefficient,  # Lower is better
            "employment_impact_diff": results2.employment_change
            - results1.employment_change,
            "gdp_impact_diff": results2.gdp_impact - results1.gdp_impact,
        }

        return {
            "scenario1_results": results1,
            "scenario2_results": results2,
            "comparison": comparison,
        }
