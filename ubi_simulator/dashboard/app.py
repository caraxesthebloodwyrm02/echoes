"""
UBI Simulation Dashboard: Interactive policy exploration tool
"""

import time
from typing import Dict, Optional

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Streamlit app configuration
st.set_page_config(
    page_title="UBI Simulation Engine",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API configuration
API_BASE_URL = "http://localhost:8001"

# Custom CSS for better styling
st.markdown(
    """
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff6b6b;
    }
    .positive-metric {
        border-left-color: #51cf66;
    }
    .negative-metric {
        border-left-color: #ff6b6b;
    }
    .neutral-metric {
        border-left-color: #74c0fc;
    }
</style>
""",
    unsafe_allow_html=True,
)


def run_simulation(parameters: Dict) -> Optional[Dict]:
    """Call API to run UBI simulation"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/simulate", json=parameters, timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error running simulation: {str(e)}")
        return None


def get_scenarios() -> Dict:
    """Get predefined scenarios from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/scenarios", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching scenarios: {str(e)}")
        return {}


def compare_scenarios(scenario1_params: Dict, scenario2_params: Dict) -> Optional[Dict]:
    """Compare two scenarios"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/compare",
            json={"scenario1": scenario1_params, "scenario2": scenario2_params},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error comparing scenarios: {str(e)}")
        return None


# Main app
st.title("💰 UBI Simulation Engine")
st.markdown("*Explore the economic impacts of Universal Basic Income policies*")

# Sidebar for parameters
with st.sidebar:
    st.header("🎛️ Policy Parameters")

    # Scenario selection
    scenarios = get_scenarios()
    scenario_names = list(scenarios.keys()) + ["Custom"]
    selected_scenario = st.selectbox(
        "Select Scenario",
        scenario_names,
        help="Choose a predefined scenario or create a custom one",
    )

    # Initialize parameters
    if selected_scenario in scenarios:
        scenario_params = scenarios[selected_scenario]["parameters"]
        if selected_scenario != "Custom":
            st.info(
                f"📋 **{scenarios[selected_scenario]['name']}**\n\n"
                f"{scenarios[selected_scenario]['description']}"
            )
    else:
        scenario_params = {
            "ubi_amount": 1000,
            "eligibility_threshold": 50000,
            "phase_out_rate": 0.3,
            "funding_mechanism": "tax",
            "tax_rate": 0.1,
        }

    # Parameter inputs with helpful descriptions
    st.subheader("💵 UBI Amount")
    ubi_amount = st.number_input(
        "Monthly UBI Amount ($)",
        min_value=0,
        max_value=5000,
        value=int(scenario_params["ubi_amount"]),
        step=100,
        help="Monthly payment amount per eligible household",
    )

    st.subheader("📊 Eligibility")
    eligibility_threshold = st.number_input(
        "Eligibility Threshold ($)",
        min_value=0,
        max_value=200000,
        value=int(scenario_params["eligibility_threshold"]),
        step=5000,
        help="Income threshold for full UBI eligibility",
    )

    phase_out_rate = st.slider(
        "Phase-out Rate",
        0.0,
        1.0,
        scenario_params["phase_out_rate"],
        0.05,
        help="How quickly UBI decreases with income above threshold",
    )

    st.subheader("💰 Funding")
    funding_mechanism = st.selectbox(
        "Funding Mechanism",
        ["tax", "deficit", "reallocation"],
        index=["tax", "deficit", "reallocation"].index(
            scenario_params["funding_mechanism"]
        ),
        help="How the program is funded",
    )

    if funding_mechanism == "tax":
        tax_rate = st.slider(
            "Tax Rate",
            0.0,
            0.5,
            scenario_params["tax_rate"],
            0.01,
            help="Additional tax rate to fund the program",
        )
    else:
        tax_rate = 0.0

    # Run simulation button
    run_button = st.button(
        "🚀 Run Simulation", type="primary", use_container_width=True
    )

# Main content area
if run_button:
    parameters = {
        "ubi_amount": ubi_amount,
        "eligibility_threshold": eligibility_threshold,
        "phase_out_rate": phase_out_rate,
        "funding_mechanism": funding_mechanism,
        "tax_rate": tax_rate,
    }

    with st.spinner("🧮 Running economic simulation..."):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        progress_bar.empty()

        results = run_simulation(parameters)

    if results:
        st.success("✅ Simulation completed!")

        # Display results
        st.header("📊 Simulation Results")

        results_data = results["results"]

        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            cost_color = (
                "positive-metric"
                if results_data["total_cost"] < 500000000
                else "negative-metric"
            )
            st.markdown(
                f"""
            <div class="metric-card {cost_color}">
                <h3>Total Cost</h3>
                <h2>${results_data["total_cost"]/1e9:.1f}B</h2>
                <p>Annual program cost</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
            <div class="metric-card neutral-metric">
                <h3>Avg Payment</h3>
                <h2>${results_data["avg_ubi_received"]:.0f}</h2>
                <p>Monthly per household</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            employment_color = (
                "positive-metric"
                if results_data["employment_change"] >= 0
                else "negative-metric"
            )
            st.markdown(
                f"""
            <div class="metric-card {employment_color}">
                <h3>Employment Change</h3>
                <h2>{results_data["employment_change"]/1000:+.0f}K</h2>
                <p>Jobs affected</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col4:
            gdp_color = (
                "positive-metric"
                if results_data["gdp_impact"] >= 0
                else "negative-metric"
            )
            st.markdown(
                f"""
            <div class="metric-card {gdp_color}">
                <h3>GDP Impact</h3>
                <h2>${results_data["gdp_impact"]/1e9:+.1f}B</h2>
                <p>Annual economic effect</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Distributional effects
        st.header("📈 Distributional Effects")

        dist_col1, dist_col2 = st.columns(2)

        with dist_col1:
            poverty_color = (
                "positive-metric"
                if results_data["poverty_reduction"] > 0
                else "neutral-metric"
            )
            st.markdown(
                f"""
            <div class="metric-card {poverty_color}">
                <h3>Poverty Reduction</h3>
                <h2>{results_data["poverty_reduction"]:+.1f}%</h2>
                <p>Reduction in poverty rate</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with dist_col2:
            st.markdown(
                f"""
            <div class="metric-card neutral-metric">
                <h3>Income Inequality</h3>
                <h2>{results_data["gini_coefficient"]:.3f}</h2>
                <p>Gini coefficient (lower = more equal)</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Regional breakdown
        st.header("🗺️ Regional Impact")

        regional_data = []
        for region, data in results_data["regional_breakdown"].items():
            regional_data.append(
                {
                    "Region": region,
                    "Total Cost ($B)": data["total_cost"] / 1e9,
                    "Avg Payment ($)": data["avg_payment"],
                    "Households": data["households"],
                }
            )

        regional_df = pd.DataFrame(regional_data)

        # Regional cost chart
        fig_cost = px.bar(
            regional_df,
            x="Region",
            y="Total Cost ($B)",
            title="UBI Cost by Region",
            color="Total Cost ($B)",
            color_continuous_scale="Blues",
        )
        fig_cost.update_layout(yaxis_tickformat="$,.2f")
        st.plotly_chart(fig_cost, use_container_width=True)

        # Regional payment chart
        fig_payment = px.bar(
            regional_df,
            x="Region",
            y="Avg Payment ($)",
            title="Average UBI Payment by Region",
            color="Avg Payment ($)",
            color_continuous_scale="Greens",
        )
        fig_payment.update_layout(yaxis_tickformat="$,.0f")
        st.plotly_chart(fig_payment, use_container_width=True)

        # Regional data table
        st.subheader("Regional Breakdown Table")
        st.dataframe(
            regional_df.style.format(
                {
                    "Total Cost ($B)": "${:.2f}",
                    "Avg Payment ($)": "${:.0f}",
                    "Households": "{:,}",
                }
            ),
            use_container_width=True,
        )

        # Parameter summary
        st.header("⚙️ Policy Summary")
        param_summary = pd.DataFrame(
            {
                "Parameter": [
                    "UBI Amount",
                    "Eligibility Threshold",
                    "Phase-out Rate",
                    "Funding Mechanism",
                    "Tax Rate",
                ],
                "Value": [
                    f"${ubi_amount}",
                    f"${eligibility_threshold:,}",
                    f"{phase_out_rate:.1%}",
                    funding_mechanism,
                    f"{tax_rate:.1%}",
                ],
            }
        )
        st.table(param_summary)

    else:
        st.error("❌ Simulation failed. Please check your parameters and try again.")

# Scenario comparison section
st.header("🔄 Scenario Comparison")
st.markdown("Compare two different UBI policies side-by-side")

comp_col1, comp_col2 = st.columns(2)

with comp_col1:
    st.subheader("Scenario A")
    scenario_a = st.selectbox(
        "Select Scenario A", list(scenarios.keys()) + ["Current"], key="scenario_a"
    )

    if scenario_a in scenarios:
        scenario_a_params = scenarios[scenario_a]["parameters"]
    else:
        scenario_a_params = {
            "ubi_amount": 1000,
            "eligibility_threshold": 50000,
            "phase_out_rate": 0.3,
            "funding_mechanism": "tax",
            "tax_rate": 0.1,
        }

with comp_col2:
    st.subheader("Scenario B")
    scenario_b = st.selectbox(
        "Select Scenario B", list(scenarios.keys()) + ["Current"], key="scenario_b"
    )

    if scenario_b in scenarios:
        scenario_b_params = scenarios[scenario_b]["parameters"]
    else:
        scenario_b_params = {
            "ubi_amount": 1500,
            "eligibility_threshold": 30000,
            "phase_out_rate": 0.5,
            "funding_mechanism": "tax",
            "tax_rate": 0.15,
        }

if st.button("⚖️ Compare Scenarios", use_container_width=True):
    with st.spinner("🔍 Comparing scenarios..."):
        comparison = compare_scenarios(scenario_a_params, scenario_b_params)

    if comparison:
        comp_results = comparison["comparison"]

        st.subheader("📊 Comparison Results")

        # Comparison metrics
        comp_metrics = pd.DataFrame(
            {
                "Metric": [
                    "Cost Difference",
                    "Efficiency Ratio",
                    "Poverty Reduction Diff",
                    "Gini Improvement",
                    "Employment Impact Diff",
                    "GDP Impact Diff",
                ],
                "Value": [
                    f'${comp_results["cost_difference"]/1e9:+.1f}B',
                    f'{comp_results["efficiency_ratio"]:.2f}x',
                    f'{comp_results["poverty_reduction_diff"]:+.1f}pp',
                    f'{comp_results["gini_improvement"]:+.3f}',
                    f'{comp_results["employment_impact_diff"]/1000:+.0f}K',
                    f'${comp_results["gdp_impact_diff"]/1e9:+.1f}B',
                ],
            }
        )

        st.table(comp_metrics)

        # Visual comparison
        scenarios_data = pd.DataFrame(
            {
                "Scenario": ["A", "B"],
                "Total Cost ($B)": [
                    comparison["scenario1"]["results"]["total_cost"] / 1e9,
                    comparison["scenario2"]["results"]["total_cost"] / 1e9,
                ],
                "Poverty Reduction (%)": [
                    comparison["scenario1"]["results"]["poverty_reduction"],
                    comparison["scenario2"]["results"]["poverty_reduction"],
                ],
                "GDP Impact ($B)": [
                    comparison["scenario1"]["results"]["gdp_impact"] / 1e9,
                    comparison["scenario2"]["results"]["gdp_impact"] / 1e9,
                ],
            }
        )

        # Cost comparison chart
        fig_comp = px.bar(
            scenarios_data,
            x="Scenario",
            y="Total Cost ($B)",
            title="Cost Comparison",
            color="Scenario",
        )
        st.plotly_chart(fig_comp, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("💰 **UBI Simulation Engine** - Economic Policy Analysis Tool")
st.markdown("*Built for evidence-based policy making*")

# Data info in sidebar
with st.sidebar:
    st.markdown("---")
    st.header("📊 Dataset Info")

    try:
        data_summary = requests.get(f"{API_BASE_URL}/data/summary", timeout=10).json()

        st.metric("Households", f"{data_summary['census']['total_households']:,}")
        st.metric("Mean Income", f"${data_summary['census']['mean_income']:,.0f}")
        st.metric("Employment Rate", f"{data_summary['census']['employment_rate']:.1%}")

        st.markdown("**Regional Coverage:**")
        for region, count in data_summary["census"]["regional_distribution"].items():
            st.write(f"- {region}: {count:,}")

    except Exception:
        st.warning("Unable to load dataset info")

    st.markdown("---")
    st.info(
        "🛡️ **Disclaimer:** This simulator uses synthetic data and "
        "simplified models. Results are illustrative and should not be "
        "used for actual policy decisions without further validation and "
        "expert review."
    )
