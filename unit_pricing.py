
import streamlit as st
import pandas as pd
import uuid

st.set_page_config(page_title="Agile Unit Pricing Tool", layout="wide")
st.title("Agile Unit Pricing Tool")

st.markdown("""
**Welcome to the Agile Unit Pricing Tool**

Use this tool to scope, simulate, and track research and strategy work with unit-based pricing.  
Toggle between internal costing and partner-facing pricing to test feasibility, pricing models, and sprint scope.

- 🧩 **Sprint Builder**: Select tasks manually or use GPT to generate a scope.
- 📊 **Sprint Log**: Track what you've added and see unit totals by domain.
- 📈 **Simulation**: Forecast what can be done per sprint or quarter.
- 💰 **Pricing Strategy**: View unit margins and explore cost assumptions.
""")
mode = st.radio("Select Pricing Mode", ["Partner (Rounded + Floors)", "Internal (Exact Costs)"], horizontal=True)
partner_mode = (mode == "Partner (Rounded + Floors)")
unit_price = 5000
overhead_pct = 32.9
rates = {"Tier 1": 300, "Tier 2": 200, "Tier 3": 100}
complexity_floors = {"Low": 0.5, "Medium": 1.0, "High": 1.5}

if "sprint_log" not in st.session_state:
    st.session_state["sprint_log"] = []

tabs = st.tabs(["🧩 Sprint Builder", "📊 Sprint Log", "📈 Simulation", "💰 Pricing Strategy"])

# Sprint Builder Tab
with tabs[0]:
    st.subheader("🧩 Sprint Builder")
    domain = st.selectbox("Domain", ["Discovery & Design", "User & Stakeholder Research", "Prototyping & Pilot Testing",
                                     "Ongoing Strategic Guidance", "Implementation Feasibility", "Regulatory & Compliance"])
    task = st.selectbox("Task", {
        "Discovery & Design": ["Discovery Workshop", "Journey Mapping"],
        "User & Stakeholder Research": ["Focus Group (2x)", "Survey + Report"],
        "Prototyping & Pilot Testing": ["Concept Testing"],
        "Ongoing Strategic Guidance": ["Advisory Session"],
        "Implementation Feasibility": ["ROI Modeling"],
        "Regulatory & Compliance": ["IRB Protocol Development"]
    }[domain])

    complexity = st.selectbox("Complexity", ["Low", "Medium", "High"])
    hours = {
        "Tier 1": st.number_input("Tier 1 Hours", value=1.0),
        "Tier 2": st.number_input("Tier 2 Hours", value=2.0),
        "Tier 3": st.number_input("Tier 3 Hours", value=4.0),
    }
    other_costs = st.number_input("Other Costs (Travel, Incentives, etc)", value=500.0)

    staff_cost = sum(hours[t] * rates[t] for t in hours)
    raw_total = staff_cost + other_costs
    total_cost = raw_total * (1 + overhead_pct / 100)

    exact_units = total_cost / unit_price
    if partner_mode:
        displayed_units = max(round(exact_units * 2) / 2, complexity_floors[complexity])
    else:
        displayed_units = round(exact_units, 2)

    st.markdown(f"**Total Cost:** ${total_cost:,.0f}  |  **Estimated Units:** {displayed_units}")

    if st.button("➕ Add to Sprint Log"):
        st.session_state["sprint_log"].append({
            "Domain": domain,
            "Task": task,
            "Complexity": complexity,
            "Units": displayed_units
        })
        st.success("Added to log.")

# Sprint Log Tab
with tabs[1]:
    st.subheader("📊 Sprint Log")
    if len(st.session_state["sprint_log"]) == 0:
        st.info("No tasks added yet.")
    else:
        df = pd.DataFrame(st.session_state["sprint_log"])
        st.dataframe(df, use_container_width=True)

        unit_total = sum(float(row["Units"]) for row in st.session_state["sprint_log"])
        st.markdown(f"### Total Units: **{unit_total}**")

        domain_summary = df.groupby("Domain")["Units"].count().reset_index(name="Count")
        st.bar_chart(domain_summary.set_index("Domain"))

# Simulation Tab
with tabs[2]:
    st.subheader("📈 Sprint Simulation")
    st.markdown("Try simulating what a sprint or quarter might look like given a unit budget.")
    sprint_units = st.slider("Available Units for Sprint", 5, 100, 25)
    theme = st.text_input("Sprint Theme (optional)", value="Example: Stakeholder Discovery + Concept Validation")
    st.markdown(f"*(This feature could suggest real task bundles soon. Currently manual.)*")

# Pricing Strategy Tab
with tabs[3]:
    st.subheader("💰 Pricing Strategy")
    st.markdown("Below is a comparison of estimated cost vs partner pricing for select tasks.")

    sample = [
        {"Task": "Discovery Workshop", "Cost": 12000, "Units": 3.0},
        {"Task": "Focus Group (2x)", "Cost": 21000, "Units": 5.0},
        {"Task": "Concept Testing", "Cost": 9800, "Units": 2.0},
        {"Task": "Advisory Session", "Cost": 4100, "Units": 1.0},
    ]
    for task in sample:
        partner_val = task["Units"] * unit_price
        task["Partner Value"] = partner_val
        task["Margin"] = round(partner_val - task["Cost"])
        task["Margin %"] = round((partner_val - task["Cost"]) / task["Cost"] * 100, 1)

    df = pd.DataFrame(sample)
    st.dataframe(df, use_container_width=True)
