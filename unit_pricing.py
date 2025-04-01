
import streamlit as st

st.set_page_config(page_title="Agile Unit Pricing Tool", layout="centered")

st.title("Agile Unit Pricing Tool")

# Domain and task mapping
domain_tasks = {
    "Discovery & Design": {
        "Landscape Scan": "Brief lit or market scan with synthesis",
        "Discovery Workshop": "Collaborative session to identify goals, needs, and framing",
        "Journey Mapping": "Document user experience over time to find friction points",
    },
    "User & Stakeholder Research": {
        "Focus Group (1x)": "Recruit, moderate, and analyze 1 focus group",
        "Survey Design + Launch": "Build, launch, and summarize a short survey",
        "Stakeholder Interviews": "Conduct up to 5 interviews and synthesize insights",
    },
    "Prototyping & Pilot Testing": {
        "Rapid Pilot (1-month)": "Deploy and monitor a product/test in the real world",
        "Concept Testing": "Structured feedback on early ideas via survey or interviews",
    },
    "Ongoing Strategic Guidance": {
        "Advisory Session": "1-hour strategic check-in + notes",
        "End-of-Phase Briefing": "Visual presentation of findings and implications",
    },
    "Implementation Feasibility & Real-World Value": {
        "ROI Modeling": "Estimate costs and benefits based on assumptions",
        "Community Pilot (N=10–20)": "Small test in real setting with community sample",
    },
    "Regulatory & Compliance": {
        "IRB Protocol Development": "Full IRB submission and supporting documents",
        "IRB Amendment": "Modify an existing protocol for new scope or methods",
    }
}

st.sidebar.header("Staff Hourly Rates")
tier1_rate = st.sidebar.number_input("Tier 1 (Director)", value=300)
tier2_rate = st.sidebar.number_input("Tier 2 (Leadership)", value=200)
tier3_rate = st.sidebar.number_input("Tier 3 (Coordinator)", value=100)
overhead = st.sidebar.slider("Overhead Multiplier", 1.0, 3.0, 2.0, 0.1)
unit_price = st.sidebar.number_input("Unit Price ($)", value=5000)

st.subheader("Step 1: Choose a Domain")
domain = st.selectbox("Domain", list(domain_tasks.keys()))

st.subheader("Step 2: Choose a Task")
task = st.selectbox("Task", list(domain_tasks[domain].keys()))
st.markdown(f"**Description:** {domain_tasks[domain][task]}")

# Placeholder input defaults
tier1_hours = st.number_input("Tier 1 Hours", value=1.0)
tier2_hours = st.number_input("Tier 2 Hours", value=2.0)
tier3_hours = st.number_input("Tier 3 Hours", value=4.0)
additional_costs = st.number_input("Additional Costs (Incentives, Travel, Supplies)", value=500.0)

# Calculate costs
staff_cost = (tier1_hours * tier1_rate) + (tier2_hours * tier2_rate) + (tier3_hours * tier3_rate)
total_raw_cost = staff_cost + additional_costs
total_cost = total_raw_cost * overhead
units = total_cost / unit_price

st.markdown(f"### Total Cost: ${total_cost:,.2f}")
st.markdown(f"### Total Units: {units:.2f}")

# Pie chart breakdown
import matplotlib.pyplot as plt

labels = ["Staff Cost", "Additional Costs", "Overhead"]
values = [staff_cost, additional_costs, total_cost - staff_cost - additional_costs]

fig, ax = plt.subplots()
ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
ax.axis("equal")
st.pyplot(fig)
