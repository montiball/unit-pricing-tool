import streamlit as st

st.title("Dynamic Unit Pricing Calculator")

st.sidebar.header("Staff Hourly Rates")
tier1_rate = st.sidebar.number_input("Tier 1 (Director) Hourly Rate", value=300)
tier2_rate = st.sidebar.number_input("Tier 2 (Leadership) Hourly Rate", value=200)
tier3_rate = st.sidebar.number_input("Tier 3 (Coordinator/Support) Hourly Rate", value=100)

st.sidebar.header("Overhead")
overhead_multiplier = st.sidebar.slider("Overhead Multiplier", 1.0, 3.0, 2.0, 0.1)

st.header("Select Task")
task = st.selectbox("Task", ["Focus Group", "Pilot Study", "Advisory Session", "IRB Protocol"])

if task == "Focus Group":
    num_groups = st.number_input("Number of Focus Groups", min_value=1, value=4)
    new_irb = st.checkbox("New IRB Required?", value=True)

    tier1_hours = st.number_input("Tier 1 Hours", value=1.0)
    tier2_hours = st.number_input("Tier 2 Hours", value=3.0)
    tier3_hours = st.number_input("Tier 3 Hours per Group", value=8.0) * num_groups
    additional_costs = st.number_input("Additional Costs (Incentives, etc.) per Group", value=400.0) * num_groups

    if new_irb:
        irb_cost = st.number_input("IRB Setup Cost", value=1000.0)
    else:
        irb_cost = 0.0

    staff_cost = (tier1_hours * tier1_rate) + (tier2_hours * tier2_rate) + (tier3_hours * tier3_rate)
    total_cost = (staff_cost + additional_costs + irb_cost) * overhead_multiplier
    unit_price = st.number_input("Unit Price (per unit)", value=5000)
    units = total_cost / unit_price

    st.markdown(f"## Total Cost: ${total_cost:,.2f}")
    st.markdown(f"## Total Units: {units:.2f}")

    cost_breakdown = {"Staff Costs": staff_cost, "Additional Costs": additional_costs, "IRB Costs": irb_cost, "Total Cost": total_cost}
    st.bar_chart(cost_breakdown, use_container_width=True)
