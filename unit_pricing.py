
import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt
import random
import json

# Page config
st.set_page_config(page_title="Agile Sprint Planner", layout="centered")
st.markdown("## 🧠 Agile Sprint Planning Tool")
st.caption("A unit-based approach for research & strategic collaboration")

# Load OpenAI API key
openai.api_key = st.secrets["openai"]["api_key"]

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🧩 Manual Builder", "🤖 GPT Planner", "📊 Sprint Log", "📈 Simulation"])

# Sidebar Settings
with st.sidebar:
    st.header("🔧 Settings")
    tier1_rate = st.number_input("Tier 1 (Director)", value=300)
    tier2_rate = st.number_input("Tier 2 (Leadership)", value=200)
    tier3_rate = st.number_input("Tier 3 (Coordinator)", value=100)
    overhead_percent = st.number_input("Overhead (%)", 0, 100, 39)
    unit_price = st.number_input("Unit Price ($)", value=5000)

# Domain/Task Structure
domain_tasks = {
    "Discovery & Design": [
        ("Landscape Scan", "Brief lit or market scan with synthesis", 1, 2, 4, ["scan", "research"]),
        ("Discovery Workshop", "Collaborative session to identify goals and needs", 1, 2, 2, ["goals", "framing"]),
        ("Journey Mapping", "Document user experience over time", 1, 3, 4, ["experience", "touchpoint"])
    ],
    "User & Stakeholder Research": [
        ("Focus Group", "Moderated group discussion", 1, 2, 8, ["focus group", "discussion"]),
        ("Stakeholder Interviews", "1:1 interviews to uncover insights", 1, 3, 6, ["interview", "stakeholder"]),
        ("Survey Design + Launch", "Deploy and analyze a survey", 1, 3, 5, ["survey", "form"])
    ],
    "Prototyping & Pilot Testing": [
        ("Rapid Pilot", "Deploy product in real world", 2, 4, 10, ["pilot", "deploy"]),
        ("Concept Testing", "Structured early feedback", 1, 3, 4, ["concept", "prototype"])
    ],
    "Ongoing Strategic Guidance": [
        ("Advisory Session", "1-hour strategy check-in", 1, 1, 1, ["advisory", "check-in"]),
        ("End-of-Phase Briefing", "Summary and implications", 1, 2, 3, ["brief", "findings"])
    ],
    "Implementation Feasibility & Real-World Value": [
        ("ROI Modeling", "Estimate costs and benefits", 2, 4, 4, ["roi", "cost benefit"]),
        ("Community Pilot", "Test in local setting", 2, 4, 8, ["community", "pilot"])
    ],
    "Regulatory & Compliance": [
        ("IRB Protocol Development", "Initial IRB submission", 2, 3, 3, ["irb", "protocol"]),
        ("IRB Amendment", "Modify existing IRB", 1, 1, 1, ["amendment", "update"])
    ]
}

# ----- Tab 4: Simulation -----
with tab4:
    st.subheader("📈 Strategic Simulation")
    col1, col2 = st.columns(2)
    with col1:
        total_units = st.number_input("Total Annual Units", value=100)
    with col2:
        quarters = st.number_input("Number of Quarters", value=4, min_value=1)

    theme = st.text_input("Optional Sprint Goal or Theme")
    simulate_btn = st.button("🔮 Run Simulation")

    def weight_tasks(theme_text):
        weights = []
        for domain, tasks in domain_tasks.items():
            for name, desc, t1, t2, t3, keywords in tasks:
                score = sum(1 for word in keywords if word in theme_text.lower())
                units = ((t1 * tier1_rate + t2 * tier2_rate + t3 * tier3_rate) * (1 + overhead_percent / 100)) / unit_price
                weights.append((domain, name, units, score))
        weights.sort(key=lambda x: (-x[3], x[2]))
        return weights

    if simulate_btn:
        st.markdown("### 🔍 Simulated Plan")
        if theme:
            st.markdown(f"**Theme:** _{theme}_")

        unit_per_q = total_units / quarters
        plan = []
        total_used = 0
        task_pool = weight_tasks(theme) if theme else [
            (d, t[0], ((t[2]*tier1_rate + t[3]*tier2_rate + t[4]*tier3_rate)*(1 + overhead_percent/100))/unit_price, 0)
            for d, tasks in domain_tasks.items() for t in tasks
        ]

        for q in range(quarters):
            used = 0
            for domain, task, units, _ in task_pool:
                if used + units <= unit_per_q:
                    plan.append({"Quarter": f"Q{q+1}", "Domain": domain, "Task": task, "Units": round(units, 2)})
                    used += units
                    total_used += units

        df = pd.DataFrame(plan)
        st.markdown("#### 🧩 Task Breakdown")
        st.dataframe(df, use_container_width=True)

        st.markdown(f"#### 📊 Total Units Used: **{total_used:.2f} / {total_units}**")
        st.markdown(f"#### ⏱ Avg Units per Quarter: **{total_used / quarters:.2f}**")

        st.markdown("#### 🗂 Units by Domain")
        domain_sum = df.groupby("Domain")["Units"].sum().reset_index()
        st.dataframe(domain_sum)

        if total_used <= total_units:
            st.success("✅ Plan fits within unit budget.")
        else:
            st.warning("⚠️ Plan exceeds total available units.") 
