import streamlit as st
import pandas as pd
import altair as alt

st.title("echoes AI: Live Intelligence Demonstration")
st.subheader("Core Value Proposition")
st.write("""
- Synthesize intelligence across domains
- Orchestrate multi-agent workflows
- Inform actionable insights
- Create measurable value
""")
st.progress(1.0)

values = [50000, 105000, 75000]

phases = ["Phase 1: Cost Reduction", "Phase 2: Growth", "Phase 3: Strategy"]
tab1, tab2, tab3 = st.tabs(phases)

with tab1:
    st.write("🔹 Inventory Health Check → Risk Reduction")
    st.metric("Monthly Savings Identified", f"${values[0]:,}")
    st.caption("Mechanism: AI-incentive stockout risk mitigation")

with tab2:
    st.write("🔹 Dynamic AOV Optimization")
    st.metric("Monthly Revenue Opportunity", f"${values[1]:,}")
    st.caption("Mechanism: Smart bundling + threshold shipping")

with tab3:
    st.write("🔹 Strategic Orchestration")
    st.metric("Strategic Value Realized", f"${values[2]:,}")
    st.caption("Mechanism: AI-curated strategy recommendations generating sustained high-margin decisions")

st.header("Total Monthly Impact")
st.metric("Combined Value Creation", f"${sum(values):,}")
st.caption("Phase 1 + Phase 2 + Phase 3 = Full Business Transformation")

st.header("Demo Execution Methods")
methods = ["Share Streamlit Directly", "Serve as HTML File", "Use Recorded Backup"]
demo_mode = st.radio("Select Demo Method:", methods)
st.success(f"Mode Selected: {demo_mode}")

data = pd.DataFrame({
    'Phase': ['Phase 1: Cost Reduction', 'Phase 2: Growth', 'Phase 3: Strategy'],
    'ROI ($/mo)': [50000, 105000, 75000]
})

chart = alt.Chart(data).mark_bar().encode(
    x='Phase:N',
    y='ROI ($/mo):Q',
    color='Phase:N',
    tooltip=['Phase', 'ROI ($/mo)']
)

st.altair_chart(chart, use_container_width=True)
st.balloons()
