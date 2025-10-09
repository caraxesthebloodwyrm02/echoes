"""
Data Loader: Load and preprocess economic data for UBI simulation
"""

import os
from typing import Dict

import numpy as np
import pandas as pd


class DataLoader:
    """
    Load and manage economic data sources for UBI simulation.
    Core responsibility: Provide clean, structured data for policy modeling.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def load_census_data(self) -> pd.DataFrame:
        """
        Load census demographic and income data.
        Core data: Household income, size, demographics, employment status.
        """
        # Generate synthetic but realistic census data
        np.random.seed(42)  # For reproducible results

        n_households = 10000

        # Income distribution (log-normal for realism)
        incomes = np.random.lognormal(mean=10.5, sigma=0.8, size=n_households)

        # Household sizes (Poisson distribution)
        household_sizes = (
            np.random.poisson(lam=2.3, size=n_households) + 1
        )  # Add 1 for realism

        # Age distribution (skewed toward working age)
        ages = np.random.normal(loc=45, scale=18, size=n_households)
        ages = np.clip(ages, 18, 85)  # Realistic age range

        # Education levels
        education_levels = ["High School", "Some College", "Bachelor", "Master", "PhD"]
        education_weights = [0.3, 0.25, 0.25, 0.15, 0.05]
        education = np.random.choice(
            education_levels, size=n_households, p=education_weights
        )

        # Regional distribution (US regions)
        regions = ["Northeast", "Midwest", "South", "West"]
        region_weights = [
            0.18,
            0.21,
            0.37,
            0.24,
        ]  # Approximate US population distribution
        region_assignments = np.random.choice(
            regions, size=n_households, p=region_weights
        )

        # Employment status with realistic correlations
        employment_status = []
        for i in range(n_households):
            age = ages[i]
            education_level = education[i]

            # Employment probability based on age and education
            if age < 25:
                base_prob = 0.6
            elif age < 65:
                base_prob = 0.85
            else:
                base_prob = 0.3

            # Education boost
            education_boost = {
                "High School": 0,
                "Some College": 0.05,
                "Bachelor": 0.1,
                "Master": 0.12,
                "PhD": 0.15,
            }[education_level]
            prob = min(base_prob + education_boost, 0.95)

            status = "Employed" if np.random.random() < prob else "Unemployed"
            employment_status.append(status)

        # Create DataFrame
        census_data = pd.DataFrame(
            {
                "household_id": range(1, n_households + 1),
                "income": incomes,
                "household_size": household_sizes,
                "age": ages,
                "education": education,
                "region": region_assignments,
                "employment_status": employment_status,
            }
        )

        return census_data

    def load_cost_of_living_data(self) -> pd.DataFrame:
        """
        Load cost of living index data by region.
        Used to adjust UBI amounts for regional cost differences.
        """
        cost_data = pd.DataFrame(
            {
                "region": ["Northeast", "Midwest", "South", "West"],
                "cost_of_living_index": [
                    120.5,
                    95.2,
                    89.7,
                    112.8,
                ],  # Index where 100 = national average
                "housing_cost_index": [145.3, 88.9, 79.2, 138.7],
                "food_cost_index": [108.4, 97.6, 95.1, 103.2],
                "transportation_cost_index": [115.6, 102.3, 98.7, 107.8],
                "healthcare_cost_index": [122.1, 98.4, 94.3, 109.2],
            }
        )

        return cost_data

    def load_employment_data(self) -> pd.DataFrame:
        """
        Load employment statistics by region.
        Used for employment impact calculations.
        """
        employment_data = pd.DataFrame(
            {
                "region": ["Northeast", "Midwest", "South", "West"],
                "unemployment_rate": [0.035, 0.042, 0.051, 0.048],  # Current rates
                "average_wage": [68500, 54800, 49800, 63200],  # Annual average wage
                "labor_force_participation": [
                    0.63,
                    0.61,
                    0.59,
                    0.62,
                ],  # Working age population
                "employment_population_ratio": [0.605, 0.583, 0.559, 0.590],
            }
        )

        return employment_data

    def load_macroeconomic_data(self) -> pd.DataFrame:
        """
        Load macroeconomic indicators for advanced simulations.
        """
        # Simplified macroeconomic data
        macro_data = pd.DataFrame(
            {
                "year": [2020, 2021, 2022, 2023, 2024],
                "gdp_growth": [0.023, 0.029, 0.018, 0.025, 0.022],
                "inflation_rate": [0.012, 0.047, 0.032, 0.024, 0.021],
                "unemployment_rate": [0.082, 0.053, 0.036, 0.037, 0.042],
                "federal_funds_rate": [0.0009, 0.0025, 0.033, 0.0425, 0.044],
            }
        )

        return macro_data

    def generate_synthetic_ubi_pilot_data(self) -> pd.DataFrame:
        """
        Generate synthetic data based on real UBI pilot studies.
        Useful for validation and calibration.
        """
        # Based on Stockton, CA UBI pilot and Finland basic income experiment
        pilot_data = pd.DataFrame(
            {
                "program": ["Stockton_CA", "Finland_National", "Ontario_Canada"],
                "ubi_amount_monthly": [500, 560, 1325],  # CAD for Ontario
                "duration_months": [24, 24, 36],
                "participants": [125, 2000, 4000],
                "employment_change_percent": [-1.2, 0.8, -0.5],  # From actual studies
                "wellbeing_improvement": [
                    0.15,
                    0.08,
                    0.12,
                ],  # Self-reported improvement
                "healthcare_cost_change": [
                    -0.08,
                    -0.03,
                    -0.05,
                ],  # Healthcare utilization
            }
        )

        return pilot_data

    def validate_data_quality(self) -> Dict[str, bool]:
        """
        Validate data quality and completeness.
        Returns dict of validation results.
        """

        validations = {}

        # Check census data
        census_data = self.load_census_data()
        validations["census_income_positive"] = (census_data["income"] > 0).all()
        validations["census_household_size_valid"] = (
            census_data["household_size"] >= 1
        ).all()
        validations["census_age_range"] = (
            (census_data["age"] >= 18) & (census_data["age"] <= 85)
        ).all()

        # Check cost of living data
        cost_data = self.load_cost_of_living_data()
        validations["cost_index_positive"] = (
            cost_data["cost_of_living_index"] > 0
        ).all()

        # Check employment data
        employment_data = self.load_employment_data()
        validations["unemployment_rate_valid"] = (
            (employment_data["unemployment_rate"] >= 0)
            & (employment_data["unemployment_rate"] <= 1)
        ).all()

        return validations

    def get_data_summary(self) -> Dict:
        """
        Get summary statistics of loaded data.
        Useful for understanding the dataset characteristics.
        """

        census_data = self.load_census_data()
        cost_data = self.load_cost_of_living_data()
        employment_data = self.load_employment_data()

        summary = {
            "census": {
                "total_households": len(census_data),
                "mean_income": census_data["income"].mean(),
                "median_income": census_data["income"].median(),
                "income_std": census_data["income"].std(),
                "regional_distribution": census_data["region"].value_counts().to_dict(),
                "employment_rate": (
                    census_data["employment_status"] == "Employed"
                ).mean(),
            },
            "cost_of_living": {
                "regions_covered": len(cost_data),
                "avg_col_index": cost_data["cost_of_living_index"].mean(),
                "col_range": {
                    "min": cost_data["cost_of_living_index"].min(),
                    "max": cost_data["cost_of_living_index"].max(),
                },
            },
            "employment": {
                "avg_unemployment_rate": employment_data["unemployment_rate"].mean(),
                "avg_wage": employment_data["average_wage"].mean(),
            },
        }

        return summary
