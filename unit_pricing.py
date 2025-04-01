
import streamlit as st

st.set_page_config(page_title="Agile Unit Pricing Tool", layout="centered")

st.title("Agile Unit Pricing Tool")

# Define tasks with descriptions and default hours
domain_tasks = {
    "Discovery & Design": {
        "Landscape Scan": ("Brief lit or market scan with synthesis", 1, 2, 4),
        "Discovery Workshop": ("Collaborative session to identify goals, needs, and framing", 1, 2, 2),
        "Journey Mapping": ("Document user experience over time to find friction points", 1, 3, 4),
        "Persona Development": ("Create evidence-informed user personas", 1, 2, 3),
        "Sprint Design": ("Scope and frame a targeted research sprint or pilot", 1, 1, 2),
    },
    "User & Stakeholder Research": {
        "Focus Group (1x)": ("Recruit, moderate, and analyze 1 focus group", 1, 2, 8),
        "Stakeholder Interviews": ("Conduct up to 5 interviews and synthesize insights", 1, 3, 6),
        "Survey Design + Launch": ("Build, launch, and summarize a short survey", 1, 3, 5),
        "Co-Design Session": ("Work session with users/stakeholders to test ideas", 1, 2, 4),
        "Usability Walkthrough": ("Moderated session with real users exploring product flow", 1, 2, 4),
    },
    "Prototyping & Pilot Testing": {
        "Rapid Pilot (1-month)": ("Deploy and monitor a product/test in the real world", 2, 4, 10),
        "Concept Testing": ("Structured feedback on early ideas via survey or interviews", 1, 3, 4),
        "Field Test Setup": ("Define measures, prep team/tools, secure approvals", 2, 4, 6),
        "Pilot Debrief & Learnings": ("Rapid synthesis after pilot wrap-up", 1, 2, 2),
        "Iteration Workshop": ("Translate findings into next build or change", 1, 2, 2),
    },
    "Ongoing Strategic Guidance": {
        "Advisory Session": ("1-hour strategic check-in + notes", 1, 1, 1),
        "Deep Dive Workshop": ("Half-day session to align or synthesize", 1, 2, 2),
        "Internal Synthesis Memo": ("Written summary of findings", 1, 1, 2),
        "End-of-Phase Briefing": ("Visual presentation of findings and implications", 1, 2, 3),
        "Quarterly Strategy Review": ("Planning session for next 90 days", 1, 2, 2),
    },
    "Implementation Feasibility & Real-World Value": {
        "ROI Modeling": ("Estimate costs and benefits", 2, 4, 4),
        "Adoption Barriers Mapping": ("Understand logistical/behavioral blockers", 1, 3, 4),
        "Community Pilot (N=10–20)": ("Small test in real setting", 2, 4, 8),
        "Trusted Messenger Testing": ("See which voices drive change", 1, 2, 3),
        "Local Ecosystem Scan": ("Document local needs, gaps, or assets", 1, 2, 3),
    },
    "Regulatory & Compliance": {
        "IRB Protocol Development": ("Full IRB submission and support docs", 2, 3, 3),
        "IRB Amendment": ("Change to existing protocol", 1, 1, 1),
        "Data Governance Setup": ("Review workflows for consent/privacy", 1, 2, 2),
        "Institutional Agreements": ("Assist with DUAs, BAAs, or site onboarding", 1, 2, 2),
        "Regulatory Strategy Advising": ("Strategic input on risk and IRB feasibility", 1, 1, 1),
    }
}

# Sidebar for rates and overhead
st.sidebar.header("Staff Hourly Rates")
tier1_rate = st.sidebar.number_input("Tier 1 (Director)", value=300)
tier2_rate = st.sidebar.number_input("Tier 2 (Leadership)", value=200)
tier3_rate = st.sidebar.number_input("Tier 3 (Coordinator)", value=100)
overhead = st.sidebar.slider("Overhead Multiplier", 1.0, 3.0, 2.0, 0.1)
unit_price = st.sidebar.number_input("Unit Price ($)", value=5000)

# Main UI
st.subheader("Step 1: Choose a Domain")
domain = st.selectbox("Domain", list(domain_tasks.keys()))

st.subheader("Step 2: Choose a Task")
task = st.selectbox("Task", list(domain_tasks[domain].keys()))
desc, default_t1, default_t2, default_t3 = domain_tasks[domain][task]
st.markdown(f"**Description:** {desc}")

# Input Fields
tier1_hours = st.number_input("Tier 1 Hours", value=default_t1)
tier2_hours = st.number_input("Tier 2 Hours", value=default_t2)
tier3_hours = st.number_input("Tier 3 Hours", value=default_t3)
additional_costs = st.number_input("Additional Costs (e.g. incentives, travel, supplies)", value=500.0)

# Cost Calculations
staff_cost = (tier1_hours * tier1_rate) + (tier2_hours * tier2_rate) + (tier3_hours * tier3_rate)
total_raw_cost = staff_cost + additional_costs
total_cost = total_raw_cost * overhead
units = total_cost / unit_price

st.markdown(f"### Total Cost: ${total_cost:,.2f}")
st.markdown(f"### Total Units: {units:.2f}")

# Pie Chart
import matplotlib.pyplot as plt
labels = ["Staff Cost", "Additional Costs", "Overhead"]
values = [staff_cost, additional_costs, total_cost - staff_cost - additional_costs]
fig, ax = plt.subplots()
ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
ax.axis("equal")
st.pyplot(fig)

# Sprint Summary Generator
st.subheader("📋 Sprint Summary Generator")
sprint_name = st.text_input("Sprint Name", value=f"{task} Sprint")
if st.button("Generate Sprint Summary"):
    st.markdown("#### 🔹 Sprint Summary")
    st.markdown(f"**Sprint Name:** {sprint_name}")
    st.markdown(f"**Domain:** {domain}")
    st.markdown(f"**Task:** {task}")
    st.markdown(f"**Description:** {desc}")
    st.markdown(f"**Tier 1 Hours:** {tier1_hours}")
    st.markdown(f"**Tier 2 Hours:** {tier2_hours}")
    st.markdown(f"**Tier 3 Hours:** {tier3_hours}")
    st.markdown(f"**Additional Costs:** ${additional_costs:,.2f}")
    st.markdown(f"**Overhead Multiplier:** x{overhead}")
    st.markdown(f"**Total Cost:** ${total_cost:,.2f}")
    st.markdown(f"**Total Units:** {units:.2f}")
