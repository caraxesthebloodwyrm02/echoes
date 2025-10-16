# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
UBI Simulation API: REST endpoints for policy simulation
"""

from typing import Dict

import uvicorn
from data.data_loader import DataLoader
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.ubi_model import UBIParameters, UBISimulator

app = FastAPI(
    title="UBI Simulation Engine API",
    description="Economic modeling API for Universal Basic Income policy simulation",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
data_loader = DataLoader()
census_data = data_loader.load_census_data()
cost_data = data_loader.load_cost_of_living_data()
employment_data = data_loader.load_employment_data()

simulator = UBISimulator(census_data, cost_data, employment_data)

# Predefined scenarios for easy testing
PREDEFINED_SCENARIOS = {
    "basic_ubi": {
        "name": "Basic UBI",
        "description": "Universal $1,000 monthly payment - no phase-out",
        "parameters": {
            "ubi_amount": 1000,
            "eligibility_threshold": 1000000,  # Effectively everyone eligible
            "phase_out_rate": 0,
            "funding_mechanism": "tax",
            "tax_rate": 0.1,
        },
    },
    "targeted_ubi": {
        "name": "Targeted UBI",
        "description": "$1,500 monthly for households below $30k income",
        "parameters": {
            "ubi_amount": 1500,
            "eligibility_threshold": 30000,
            "phase_out_rate": 0.5,
            "funding_mechanism": "tax",
            "tax_rate": 0.15,
        },
    },
    "high_ubi": {
        "name": "High UBI",
        "description": "$2,000 monthly with gradual phase-out",
        "parameters": {
            "ubi_amount": 2000,
            "eligibility_threshold": 50000,
            "phase_out_rate": 0.3,
            "funding_mechanism": "tax",
            "tax_rate": 0.2,
        },
    },
    "pilot_program": {
        "name": "Pilot Program",
        "description": "$600 monthly - similar to Stockton, CA pilot",
        "parameters": {
            "ubi_amount": 600,
            "eligibility_threshold": 35000,
            "phase_out_rate": 0.2,
            "funding_mechanism": "reallocation",
            "tax_rate": 0,
        },
    },
}


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "UBI Simulation Engine API",
        "version": "1.0.0",
        "endpoints": {
            "GET /scenarios": "List predefined scenarios",
            "POST /simulate": "Run custom simulation",
            "POST /compare": "Compare two scenarios",
            "GET /data/summary": "Get dataset summary",
            "GET /health": "Health check",
        },
    }


@app.get("/scenarios")
async def get_scenarios():
    """Get all predefined UBI scenarios"""
    return PREDEFINED_SCENARIOS


@app.get("/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    """Get a specific predefined scenario"""
    if scenario_id not in PREDEFINED_SCENARIOS:
        raise HTTPException(
            status_code=404, detail=f"Scenario '{scenario_id}' not found"
        )

    return PREDEFINED_SCENARIOS[scenario_id]


@app.post("/simulate")
async def run_simulation(parameters: Dict):
    """
    Run UBI simulation with custom parameters

    Expected parameters:
    {
        "ubi_amount": 1000,
        "eligibility_threshold": 30000,
        "phase_out_rate": 0.5,
        "funding_mechanism": "tax",
        "tax_rate": 0.1
    }
    """
    try:
        # Validate parameters
        required_params = [
            "ubi_amount",
            "eligibility_threshold",
            "phase_out_rate",
            "funding_mechanism",
            "tax_rate",
        ]

        for param in required_params:
            if param not in parameters:
                raise HTTPException(
                    status_code=400, detail=f"Missing required parameter: {param}"
                )

        # Create UBIParameters object
        ubi_params = UBIParameters(
            ubi_amount=float(parameters["ubi_amount"]),
            eligibility_threshold=float(parameters["eligibility_threshold"]),
            phase_out_rate=float(parameters["phase_out_rate"]),
            funding_mechanism=str(parameters["funding_mechanism"]),
            tax_rate=float(parameters["tax_rate"]),
        )

        # Validate parameter ranges
        if ubi_params.ubi_amount <= 0:
            raise HTTPException(status_code=400, detail="UBI amount must be positive")
        if ubi_params.eligibility_threshold < 0:
            raise HTTPException(
                status_code=400, detail="Eligibility threshold cannot be negative"
            )
        if not (0 <= ubi_params.phase_out_rate <= 1):
            raise HTTPException(
                status_code=400, detail="Phase-out rate must be between 0 and 1"
            )
        if ubi_params.funding_mechanism not in ["tax", "deficit", "reallocation"]:
            raise HTTPException(status_code=400, detail="Invalid funding mechanism")

        # Run simulation
        results = simulator.simulate_ubi(ubi_params)

        # Convert results to JSON-serializable format
        response = {
            "parameters": {
                "ubi_amount": ubi_params.ubi_amount,
                "eligibility_threshold": ubi_params.eligibility_threshold,
                "phase_out_rate": ubi_params.phase_out_rate,
                "funding_mechanism": ubi_params.funding_mechanism,
                "tax_rate": ubi_params.tax_rate,
            },
            "results": {
                "total_cost": float(results.total_cost),
                "avg_ubi_received": float(results.avg_ubi_received),
                "employment_change": float(results.employment_change),
                "gdp_impact": float(results.gdp_impact),
                "poverty_reduction": float(results.poverty_reduction),
                "gini_coefficient": float(results.gini_coefficient),
                "regional_breakdown": {
                    region: {
                        "total_cost": float(data["total_cost"]),
                        "avg_payment": float(data["avg_payment"]),
                        "households": int(data["households"]),
                    }
                    for region, data in results.regional_breakdown.items()
                },
            },
            "baseline_metrics": data_loader.get_data_summary(),
        }

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid parameter value: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@app.post("/compare")
async def compare_scenarios(scenario1: Dict, scenario2: Dict):
    """
    Compare two UBI scenarios side-by-side

    Input format:
    {
        "scenario1": {"ubi_amount": 1000, ...},
        "scenario2": {"ubi_amount": 1500, ...}
    }
    """
    try:
        # Run both simulations
        result1 = await run_simulation(scenario1)
        result2 = await run_simulation(scenario2)

        # Calculate comparison metrics
        comparison = {
            "cost_difference": result2["results"]["total_cost"]
            - result1["results"]["total_cost"],
            "efficiency_ratio": (
                result2["results"]["total_cost"] / result1["results"]["total_cost"]
                if result1["results"]["total_cost"] > 0
                else 0
            ),
            "poverty_reduction_diff": (
                result2["results"]["poverty_reduction"]
                - result1["results"]["poverty_reduction"]
            ),
            "gini_improvement": (
                result1["results"]["gini_coefficient"]
                - result2["results"]["gini_coefficient"]
            ),  # Lower is better
            "employment_impact_diff": (
                result2["results"]["employment_change"]
                - result1["results"]["employment_change"]
            ),
            "gdp_impact_diff": (
                result2["results"]["gdp_impact"] - result1["results"]["gdp_impact"]
            ),
        }

        return {"scenario1": result1, "scenario2": result2, "comparison": comparison}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")


@app.get("/data/summary")
async def get_data_summary():
    """Get summary statistics of the simulation dataset"""
    try:
        return data_loader.get_data_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data summary error: {str(e)}")


@app.get("/data/validation")
async def validate_data():
    """Validate data quality"""
    try:
        return data_loader.validate_data_quality()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data validation error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "dataset_size": len(census_data),
        "regions_covered": len(cost_data),
        "simulation_ready": True,
    }


@app.post("/simulate/scenario/{scenario_name}")
async def run_predefined_scenario(scenario_name: str):
    """Run a predefined scenario by name"""
    if scenario_name not in PREDEFINED_SCENARIOS:
        raise HTTPException(
            status_code=404, detail=f"Scenario '{scenario_name}' not found"
        )

    scenario = PREDEFINED_SCENARIOS[scenario_name]
    return await run_simulation(scenario["parameters"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
