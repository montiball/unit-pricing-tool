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

if "scope_info" not in st.session_state:
    st.session_state.scope_info = {}

# ---------------- Tab 0: Scope Setup ----------------
with tab0:
    st.subheader("📋 Define Project Scope")
    st.markdown("Fill out initial project info to inform planning and exports.")

    scope_info = st.session_state.scope_info

    scope_name = st.text_input("Project Name", value=scope_info.get("Project Name", ""))
    study_type = st.selectbox("Study Type", ["Exploratory", "Cross-sectional", "Longitudinal", "Pilot", "RCT", "Registry"], index=["Exploratory", "Cross-sectional", "Longitudinal", "Pilot", "RCT", "Registry"].index(scope_info.get("Study Type", "Exploratory")))
    estimated_n = st.number_input("Target Sample Size (N)", min_value=1, value=int(scope_info.get("Estimated N", 10)))
    num_timepoints = st.selectbox("Number of Timepoints", ["1", "2–3", "4+", "Ongoing"], index=["1", "2–3", "4+", "Ongoing"].index(scope_info.get("Timepoints", "1")))
    irb_status = st.selectbox("IRB Status", ["Not started", "Exempt", "Full Board", "Approved"], index=["Not started", "Exempt", "Full Board", "Approved"].index(scope_info.get("IRB Status", "Not started")))
    data_methods = st.multiselect("Data Collection Methods", ["Surveys", "Interviews", "Focus Groups", "Devices", "Diaries"], default=scope_info.get("Data Methods", []))
    incentives = st.selectbox("Use of Incentives", ["None", "$25", "$50", "$100+"], index=["None", "$25", "$50", "$100+"].index(scope_info.get("Incentives", "None")))
    tech = st.selectbox("Tech Integration", ["None", "REDCap", "mHealth Device", "App"], index=["None", "REDCap", "mHealth Device", "App"].index(scope_info.get("Tech", "None")))
    timeline = st.selectbox("Timeline Preference", ["Standard", "Expedited"], index=["Standard", "Expedited"].index(scope_info.get("Timeline", "Standard")))

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
            "Timeline": timeline
        }
        st.success("Scope setup saved or updated! Proceed to Manual Builder.")

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
        st.markdown(f"- **Study Type:** {scope.get('Study Type')}\n- **Sample Size (N):** {scope.get('Estimated N')}\n- **Timepoints:** {scope.get('Timepoints')}\n- **IRB:** {scope.get('IRB Status')}\n- **Data Methods:** {', '.join(scope.get('Data Methods', []))}\n- **Incentives:** {scope.get('Incentives')}\n- **Technology:** {scope.get('Tech')}\n- **Timeline:** {scope.get('Timeline')}\n")

    if log:
        st.markdown("---")
        st.markdown("### 🧩 Task Breakdown")
        for task in log:
            st.markdown(f"**{task['Task']}** — Est. {task['Units']} units (${task['Cost']})")
            desc = task_df[task_df["Task Name"] == task["Task"]]["Long Description"]
            if not desc.empty:
                st.markdown(desc.iloc[0])
    else:
        st.info("No tasks added to sprint log yet.")
