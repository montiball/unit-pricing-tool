import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt
import random
import json
import uuid

st.set_page_config(page_title="Agile Sprint Planner", layout="centered")
st.title("🧠 Agile Sprint Planning Tool")
st.caption("Use units to design, price, and simulate strategic research sprints")

openai.api_key = st.secrets["openai"]["api_key"]

# Load sample tasks from CSV instead
csv_path = "ResearchCenter_ServiceMenu_Template(Task Library).csv"
task_df = pd.read_csv(csv_path, encoding='latin1')
task_df = task_df[task_df["Task Name"].notna() & task_df["Brief Description (Visuals)"].notna()]

# UI Tabs
tab0, tab1, tab2, tab3 = st.tabs([
    "📋 Scope Setup", "🧩 Manual Builder", "📊 Sprint Log", "📤 Exports"
])

# Global settings
with st.sidebar:
    st.header("🔧 Settings")
    tier1_rate = st.number_input("Tier 1 (Director)", value=300)
    tier2_rate = st.number_input("Tier 2 (Leadership)", value=200)
    tier3_rate = st.number_input("Tier 3 (Coordinator)", value=100)
    overhead_percent = st.number_input("Overhead / Indirect (%)", min_value=0, max_value=100, value=39, step=1)
    unit_price = st.number_input("Unit Price ($)", min_value=100, step=100, value=5000)

if "sprint_log" not in st.session_state:
    st.session_state.sprint_log = []



# ---------------- Tab 0: Scope Setup (Updated with duration + budget) ----------------
with tab0:
    st.subheader("📋 Define Project Scope")
    st.markdown("Fill out initial project info to inform planning and exports.")

                        scope_info = st.session_state.scope_info if 'scope_info' in st.session_state else {}

    scope_name = st.text_input("Project Name", value=scope_info.get("Project Name", ""))
    study_type = st.selectbox("Study Type", ["Exploratory", "Cross-sectional", "Longitudinal", "Pilot", "RCT", "Registry"], index=["Exploratory", "Cross-sectional", "Longitudinal", "Pilot", "RCT", "Registry"].index(scope_info.get("Study Type", "Exploratory")))
    estimated_n = st.number_input("Target Sample Size (N)", min_value=1, value=int(scope_info.get("Estimated N", 10)))
    num_timepoints = st.selectbox("Number of Timepoints", ["1", "2–3", "4+", "Ongoing"], index=["1", "2–3", "4+", "Ongoing"].index(scope_info.get("Timepoints", "1")))
    irb_status = st.selectbox("IRB Status", ["Not started", "Exempt", "Full Board", "Approved"], index=["Not started", "Exempt", "Full Board", "Approved"].index(scope_info.get("IRB Status", "Not started")))
    data_methods = st.multiselect("Data Collection Methods", ["Surveys", "Interviews", "Focus Groups", "Devices", "Diaries"], default=scope_info.get("Data Methods", []))
    incentives = st.selectbox("Use of Incentives", ["None", "$25", "$50", "$100+"], index=["None", "$25", "$50", "$100+"].index(scope_info.get("Incentives", "None")))
                            tech = st.selectbox("Tech Integration", ["None", "REDCap", "mHealth Device", "App"], index=["None", "REDCap", "mHealth Device", "App"].index(scope_info.get("Tech", "None")))
                        timeline = st.selectbox("Timeline Preference", ["Standard", "Expedited"], index=["Standard", "Expedited"].index(scope_info.get("Timeline", "Standard")))
                                    study_length = st.number_input("Estimated Study Length (Months)", min_value=1, value=int(scope_info.get("Study Length (Months)", 6)))
                                    budget_estimate = st.number_input("Rough Budget Estimate ($)", min_value=0, value=int(scope_info.get("Budget Estimate", 100000)))

                            st.markdown("---")
    st.markdown("### 🧱 Optional: Define Key Milestones / Sprints")
    st.caption("These will structure your scope of work. You can leave them blank or customize.")

    sprint1_name = st.text_input("Sprint 1 Title", value=scope_info.get("Sprint 1 Title", "Phase 1: Qualitative Work"))
    sprint1_goal = st.text_area("Sprint 1 Goal / Summary", value=scope_info.get("Sprint 1 Goal", "Conduct focus groups and stakeholder interviews."))

    sprint2_name = st.text_input("Sprint 2 Title", value=scope_info.get("Sprint 2 Title", "Phase 2: In-Home Data Collection"))
    sprint2_goal = st.text_area("Sprint 2 Goal / Summary", value=scope_info.get("Sprint 2 Goal", "Collect at-home data using crossover device design."))

    sprint3_name = st.text_input("Sprint 3 Title", value=scope_info.get("Sprint 3 Title", "Phase 3: Analysis & Reporting"))
    sprint3_goal = st.text_area("Sprint 3 Goal / Summary", value=scope_info.get("Sprint 3 Goal", "Analyze results and deliver final report to partner."))
                                        if st.button("Save / Update Scope Setup"):
        st.session_state.scope_info = {
            "Project Name": scope_name,
            "Study Type": study_type,
            "Estimated N": estimated_n,
            "Timepoints": num_timepoints,
            "IRB Status": irb_status,
            "Data Methods": data_methods,
            "Incentives": incentives,
            "Tech": tech,
            "Timeline": timeline,
            "Study Length (Months)": study_length,
            "Budget Estimate": budget_estimate,
            "Sprint 1 Title": sprint1_name,
            "Sprint 1 Goal": sprint1_goal,
            "Sprint 2 Title": sprint2_name,
            "Sprint 2 Goal": sprint2_goal,
            "Sprint 3 Title": sprint3_name,
            "Sprint 3 Goal": sprint3_goal
        }
        st.success("Scope setup saved or updated! Proceed to Manual Builder.")

# ---------------- Tab 1: Manual Builder ----------------
with tab1:
    st.subheader("🧩 Manual Builder")
    scope = st.session_state.scope_info

    if task_df.empty:
        st.warning("No tasks available. Please check the uploaded task file.")
    else:
        domain = st.selectbox("Domain", sorted(task_df["Category"].dropna().unique()))
        task_subset = task_df[task_df["Category"] == domain]
        task_name = st.selectbox("Select Task", task_subset["Task Name"].unique())
        task = task_subset[task_subset["Task Name"] == task_name].iloc[0]

        st.markdown(f"**Description:** {task['Brief Description (Visuals)']}")
        st.markdown(f"*Domain:* {task['Category']}")

        if st.checkbox("Show long proposal description"):
            st.markdown(task["Longer Description (SOW)"])

        estimated_n = scope.get("Estimated N", 10)
        incentive_val = int(scope.get("Incentives", "$0").replace("$", "").replace("+", "") or 0)

        num_participants = st.number_input("Estimated Participants", value=estimated_n)
        use_translation = st.radio("Translation Needed?", ["No", "Yes"], index=0)

        try:
            default_t1 = int(float(task.get("Estimated Hours", 1)))
        except:
            default_t1 = 1
        tier1_hours = st.number_input("Tier 1 Hours", value=default_t1)
        try:
            default_t2 = int(float(task.get("Tier 2 Hours", 0)))
        except:
            default_t2 = 0
        tier2_hours = st.number_input("Tier 2 Hours", value=default_t2)
        try:
            default_t3 = int(float(task.get("Tier 3 Hours", 0)))
        except:
            default_t3 = 0
        tier3_hours = st.number_input("Tier 3 Hours", value=default_t3)

        incentive_total = num_participants * incentive_val
        other_costs = st.number_input("Other Costs (e.g., transcription, travel)", value=500.0)

        base_cost = tier1_hours * tier1_rate + tier2_hours * tier2_rate + tier3_hours * tier3_rate
        total_raw = base_cost + incentive_total + other_costs
        total_cost = total_raw * (1 + overhead_percent / 100)
        total_units = total_cost / unit_price

        st.markdown(f"**Estimated Cost:** ${total_cost:,.2f}")
        st.markdown(f"**Estimated Units:** {total_units:.2f}")

        if st.button("➕ Add to Sprint Log"):
            st.session_state.sprint_log.append({
                "Domain": domain,
                "Task": task_name,
                "Participants": num_participants,
                "Translation": use_translation,
                "Units": round(total_units, 2),
                "Cost": round(total_cost, 2)
            })
            st.success("Task added to sprint ✅")

# ---------------- Tab 2: Sprint Log ----------------
with tab2:
    st.subheader("📊 Sprint Log")
    if st.session_state.sprint_log:
        df = pd.DataFrame(st.session_state.sprint_log)
        st.dataframe(df, use_container_width=True)
        st.markdown(f"**Total Units Used:** {df['Units'].sum():.2f}")
        st.markdown(f"**Total Cost:** ${df['Cost'].sum():,.2f}")
        st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="sprint_log.csv")
    else:
        st.info("No tasks in sprint log yet.")

# ---------------- Tab 3: Export ----------------
with tab3:
    st.subheader("📤 Export Scope of Work / Proposal")
    scope = st.session_state.scope_info
    log = st.session_state.sprint_log

    if scope:
        st.markdown(f"### 📁 Project: {scope.get('Project Name', 'Untitled')}")
        st.markdown(f"- **Study Type:** {scope.get('Study Type')}
- **Sample Size (N):** {scope.get('Estimated N')}
- **Timepoints:** {scope.get('Timepoints')}
- **IRB:** {scope.get('IRB Status')}
- **Study Length (Months):** {scope.get('Study Length (Months)')}
- **Estimated Budget:** ${scope.get('Budget Estimate'):,}
- **Data Methods:** {', '.join(scope.get('Data Methods', []))}
- **Incentives:** {scope.get('Incentives')}
- **Technology:** {scope.get('Tech')}
- **Timeline:** {scope.get('Timeline')}
- **Milestones / Sprints Defined:**
  - {scope.get('Sprint 1 Title')}: {scope.get('Sprint 1 Goal')}
  - {scope.get('Sprint 2 Title')}: {scope.get('Sprint 2 Goal')}
  - {scope.get('Sprint 3 Title')}: {scope.get('Sprint 3 Goal')}
")

    st.markdown("---")
                                                            st.markdown("### 🧩 Task Breakdown")
        for task in log:
            st.markdown(f"**{task['Task']}** — Est. {task['Units']} units (${task['Cost']})")
            desc = task_df[task_df["Task Name"] == task["Task"]]["Longer Description (SOW)"]
            if not desc.empty:
                st.markdown(desc.iloc[0])
    else:
        st.info("No tasks added to sprint log yet.")
