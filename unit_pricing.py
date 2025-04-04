import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt
import random
import json
import uuid

st.set_page_config(page_title="Agile Project Scoping Tool", layout="wide")
st.title("🧠 Agile Project Scoping Tool")
st.caption("Dynamically scope out research projects, program evaluations, consulting engagements, and more.")

openai.api_key = st.secrets["openai"]["api_key"]

# ----------------- Load or Simulate Task Library -----------------
try:
    csv_path = "ResearchCenter_ServiceMenu_Template(Task Library).csv"
    task_df = pd.read_csv(csv_path, encoding='latin1')
except Exception as e:
    # Simulated tasks data if CSV not found
    data = {
        "Task Name": ["Focus Group", "Device Testing", "Survey Administration"],
        "Category": ["Research", "Research", "Program Eval"],
        "Brief Description (Visuals)": [
            "Conduct focus groups with older adults.",
            "Test new mHealth device with users.",
            "Administer surveys to evaluate program impact."
        ],
        "Longer Description (SOW)": [
            "Conduct detailed focus group sessions, stratify by demographic factors, and analyze themes.",
            "Perform device testing with a sample of users, capturing usability and performance metrics.",
            "Distribute and analyze surveys to capture program impact and participant satisfaction."
        ],
        "Estimated Hours": [10, 8, 5],
        "Tier 2 Hours": [2, 1, 1],
        "Tier 3 Hours": [1, 0, 0],
        "Task Duration": [3, 2, 1],  # in days
        "Prerequisites": ["None", "Focus Group", "Focus Group"],
        "Custom Notes": [
            "May require additional analysis if themes exceed 3.",
            "Device testing contingent on prototype availability.",
            "Survey design can be adjusted based on focus group insights."
        ]
    }
    task_df = pd.DataFrame(data)

# ----------------- Initialize Session State -----------------
if "sprint_log" not in st.session_state:
    st.session_state.sprint_log = []
if "task_modifiers" not in st.session_state:
    st.session_state.task_modifiers = {}

# ----------------- Sidebar Global Settings -----------------
with st.sidebar:
    st.header("🔧 Global Settings")
    tier1_rate = st.number_input("Tier 1 (Director) Rate ($/hr)", value=300)
    tier2_rate = st.number_input("Tier 2 (Leadership) Rate ($/hr)", value=200)
    tier3_rate = st.number_input("Tier 3 (Coordinator) Rate ($/hr)", value=100)
    overhead_percent = st.number_input("Overhead / Indirect (%)", min_value=0, max_value=100, value=39, step=1)
    unit_price = st.number_input("Unit Price ($ per unit)", min_value=100, step=100, value=5000)

# ----------------- Define Tabs -----------------
tab0, tab1, tab2, tab3 = st.tabs(["📋 Scope Setup", "🧩 Manual Builder", "📊 Dashboard", "📤 Exports"])

# ----------------- Tab 0: Scope Setup -----------------
with tab0:
    st.subheader("Define Project Scope")
    st.markdown("Fill out the project details to inform planning and proposals.")
    
    scope_info = st.session_state.scope_info if "scope_info" in st.session_state else {}
    
    scope_name = st.text_input("Project Name", value=scope_info.get("Project Name", ""))
    project_type = st.selectbox("Project Type", ["Research", "Program Evaluation", "Consulting", "Other"], index=0)
    study_type = st.selectbox("Study Type", ["Exploratory", "Cross-sectional", "Longitudinal", "Pilot", "RCT", "Registry"], index=0)
    estimated_n = st.number_input("Target Sample Size (N)", min_value=1, value=int(scope_info.get("Estimated N", 10)))
    timeline = st.selectbox("Timeline Preference", ["Standard", "Expedited"], index=0)
    study_length = st.number_input("Estimated Study Length (Months)", min_value=1, value=int(scope_info.get("Study Length (Months)", 6)))
    budget_estimate = st.number_input("Rough Budget Estimate ($)", min_value=0, value=int(scope_info.get("Budget Estimate", 100000)))
    
    st.markdown("---")
    st.markdown("### Define Key Milestones / Phases")
    phase1_name = st.text_input("Phase 1 Title", value=scope_info.get("Phase 1 Title", "Phase 1: Discovery"))
    phase1_desc = st.text_area("Phase 1 Description", value=scope_info.get("Phase 1 Description", "Initial research, stakeholder interviews, and planning."))
    phase2_name = st.text_input("Phase 2 Title", value=scope_info.get("Phase 2 Title", "Phase 2: Implementation"))
    phase2_desc = st.text_area("Phase 2 Description", value=scope_info.get("Phase 2 Description", "Execution of research activities, data collection, and analysis."))
    phase3_name = st.text_input("Phase 3 Title", value=scope_info.get("Phase 3 Title", "Phase 3: Reporting"))
    phase3_desc = st.text_area("Phase 3 Description", value=scope_info.get("Phase 3 Description", "Final report, insights, and recommendations."))
    
    if st.button("Save / Update Scope Setup"):
        st.session_state.scope_info = {
            "Project Name": scope_name,
            "Project Type": project_type,
            "Study Type": study_type,
            "Estimated N": estimated_n,
            "Timeline": timeline,
            "Study Length (Months)": study_length,
            "Budget Estimate": budget_estimate,
            "Phase 1 Title": phase1_name,
            "Phase 1 Description": phase1_desc,
            "Phase 2 Title": phase2_name,
            "Phase 2 Description": phase2_desc,
            "Phase 3 Title": phase3_name,
            "Phase 3 Description": phase3_desc
        }
        st.success("Scope setup saved or updated!")
        
# ----------------- Tab 1: Manual Builder -----------------
with tab1:
    st.subheader("Manual Builder & Task Customization")
    
    if task_df.empty:
        st.warning("No tasks available in the library.")
    else:
        # Select task from library
        domain = st.selectbox("Select Domain", sorted(task_df["Category"].dropna().unique()))
        task_subset = task_df[task_df["Category"] == domain]
        task_name = st.selectbox("Select Task", task_subset["Task Name"].unique())
        task = task_subset[task_df["Task Name"] == task_name].iloc[0]
        
        st.markdown(f"**Description:** {task['Brief Description (Visuals)']}")
        st.markdown(f"*Category:* {task['Category']}")
        
        # Option to show full description
        if st.checkbox("Show Full Proposal Description"):
            st.markdown(task["Longer Description (SOW)"])
        
        # Show additional task details (with editable modifiers)
        current_mods = st.session_state.task_modifiers.get(task_name, {})
        task_duration = current_mods.get("Task Duration", task.get("Task Duration", 0))
        prerequisites = current_mods.get("Prerequisites", task.get("Prerequisites", ""))
        custom_notes = current_mods.get("Custom Notes", task.get("Custom Notes", ""))
        
        st.markdown(f"**Task Duration:** {task_duration} days")
        st.markdown(f"**Prerequisites:** {prerequisites}")
        st.markdown(f"**Custom Notes:** {custom_notes}")
        
        # Option to edit task details
        if st.checkbox("Edit Task Details"):
            new_duration = st.number_input("Task Duration (days)", value=int(task_duration))
            new_prereq = st.text_input("Prerequisites", value=prerequisites)
            new_notes = st.text_area("Custom Notes", value=custom_notes)
            if st.button("Save Task Details"):
                st.session_state.task_modifiers[task_name] = {
                    "Task Duration": new_duration,
                    "Prerequisites": new_prereq,
                    "Custom Notes": new_notes
                }
                st.success("Task details updated!")
        
        st.markdown("---")
        st.markdown("### Cost Simulation")
        
        # Choose simulation mode: Standard vs Inverse Budgeting
        sim_mode = st.radio("Simulation Mode", ["Standard", "Inverse Budgeting"], index=0)
        
        if sim_mode == "Standard":
            num_participants = st.number_input("Estimated Participants", value=estimated_n)
            use_translation = st.radio("Translation Needed?", ["No", "Yes"], index=0)
            try:
                default_t1 = int(float(task.get("Estimated Hours", 1)))
            except Exception:
                default_t1 = 1
            tier1_hours = st.number_input("Tier 1 Hours", value=default_t1)
            try:
                default_t2 = int(float(task.get("Tier 2 Hours", 0)))
            except Exception:
                default_t2 = 0
            tier2_hours = st.number_input("Tier 2 Hours", value=default_t2)
            try:
                default_t3 = int(float(task.get("Tier 3 Hours", 0)))
            except Exception:
                default_t3 = 0
            tier3_hours = st.number_input("Tier 3 Hours", value=default_t3)
            
            # Calculate incentives if defined in scope (if not, it defaults to 0)
            incentive_val = int(str(st.session_state.scope_info.get("Incentives", "$0")).replace("$", "").replace("+", "") or 0)
            incentive_total = num_participants * incentive_val
            other_costs = st.number_input("Other Costs (e.g., transcription, travel)", value=500.0)
            
            base_cost = tier1_hours * tier1_rate + tier2_hours * tier2_rate + tier3_hours * tier3_rate
            total_raw = base_cost + incentive_total + other_costs
            total_cost = total_raw * (1 + overhead_percent / 100)
            total_units = total_cost / unit_price
            
            st.markdown(f"**Estimated Cost:** ${total_cost:,.2f}")
            st.markdown(f"**Estimated Units:** {total_units:.2f}")
            
            if st.button("➕ Add Task to Project", key="std_add"):
                st.session_state.sprint_log.append({
                    "Domain": domain,
                    "Task": task_name,
                    "Participants": num_participants,
                    "Translation": use_translation,
                    "Units": round(total_units, 2),
                    "Cost": round(total_cost, 2)
                })
                st.success("Task added to project!")
        
        else:
            target_budget = st.number_input("Target Budget ($)", value=100000)
            try:
                default_t1 = int(float(task.get("Estimated Hours", 1)))
            except Exception:
                default_t1 = 1
            tier1_hours = st.number_input("Tier 1 Hours", value=default_t1, key="inv_t1")
            try:
                default_t2 = int(float(task.get("Tier 2 Hours", 0)))
            except Exception:
                default_t2 = 0
            tier2_hours = st.number_input("Tier 2 Hours", value=default_t2, key="inv_t2")
            try:
                default_t3 = int(float(task.get("Tier 3 Hours", 0)))
            except Exception:
                default_t3 = 0
            tier3_hours = st.number_input("Tier 3 Hours", value=default_t3, key="inv_t3")
            other_costs = st.number_input("Other Costs (e.g., transcription, travel)", value=500.0, key="inv_other")
            
            incentive_val = int(str(st.session_state.scope_info.get("Incentives", "$0")).replace("$", "").replace("+", "") or 0)
            base_cost = tier1_hours * tier1_rate + tier2_hours * tier2_rate + tier3_hours * tier3_rate
            if incentive_val > 0:
                max_participants = (target_budget / (1 + overhead_percent / 100) - base_cost - other_costs) / incentive_val
                max_participants = int(max_participants) if max_participants > 0 else 0
                st.markdown(f"**Estimated Maximum Participants:** {max_participants}")
            else:
                st.info("Inverse Budgeting not applicable when no incentive cost is defined.")

# ----------------- Tab 2: Dashboard -----------------
with tab2:
    st.subheader("Project Dashboard & Visualization")
    
    if st.session_state.sprint_log:
        df_log = pd.DataFrame(st.session_state.sprint_log)
        st.dataframe(df_log, use_container_width=True)
        
        total_units = df_log['Units'].sum()
        total_cost = df_log['Cost'].sum()
        st.markdown(f"**Total Units Used:** {total_units:.2f}")
        st.markdown(f"**Total Cost:** ${total_cost:,.2f}")
        
        # Visualization: Cost Breakdown by Domain
        cost_by_domain = df_log.groupby("Domain")["Cost"].sum().reset_index()
        fig, ax = plt.subplots()
        ax.bar(cost_by_domain["Domain"], cost_by_domain["Cost"])
        ax.set_xlabel("Domain")
        ax.set_ylabel("Cost ($)")
        ax.set_title("Cost Breakdown by Domain")
        st.pyplot(fig)
    else:
        st.info("No tasks added to the project yet.")
        
# ----------------- Tab 3: Exports & Proposal -----------------
with tab3:
    st.subheader("Export & Proposal Generation")
    scope = st.session_state.scope_info if "scope_info" in st.session_state else {}
    log = st.session_state.sprint_log
    
    if scope:
        st.markdown(f"### Project: {scope.get('Project Name', 'Untitled')}")
        st.markdown(f"""
- **Project Type:** {scope.get('Project Type', '')}
- **Study Type:** {scope.get('Study Type', '')}
- **Target Sample Size (N):** {scope.get('Estimated N', '')}
- **Timeline:** {scope.get('Timeline', '')}
- **Study Length (Months):** {scope.get('Study Length (Months)', '')}
- **Estimated Budget:** ${scope.get('Budget Estimate', 0):,}
- **Phases:**
  - **{scope.get('Phase 1 Title', '')}:** {scope.get('Phase 1 Description', '')}
  - **{scope.get('Phase 2 Title', '')}:** {scope.get('Phase 2 Description', '')}
  - **{scope.get('Phase 3 Title', '')}:** {scope.get('Phase 3 Description', '')}
        """)
    else:
        st.info("No project scope defined yet.")
        
    st.markdown("---")
    st.markdown("### Task Breakdown")
    if log:
        for task in log:
            st.markdown(f"**{task['Task']}** — Est. {task['Units']} units (${task['Cost']})")
            desc = task_df[task_df["Task Name"] == task["Task"]]["Longer Description (SOW)"]
            if not desc.empty:
                st.markdown(desc.iloc[0])
    else:
        st.info("No tasks added to the project.")
        
    # Proposal Generation Function
    def generate_proposal(scope, sprint_log):
        proposal = ""
        proposal += "# Proposal for " + scope.get("Project Name", "Untitled Project") + "\n\n"
        proposal += "## Introduction\n"
        proposal += ("This proposal outlines our approach for the project, including methodology, timeline, and cost breakdown. "
                     "Our team is committed to delivering high-quality insights tailored to your needs.\n\n")
        proposal += "## Project Overview\n"
        proposal += f"- **Project Type:** {scope.get('Project Type', '')}\n"
        proposal += f"- **Study Type:** {scope.get('Study Type', '')}\n"
        proposal += f"- **Target Sample Size (N):** {scope.get('Estimated N', '')}\n"
        proposal += f"- **Timeline:** {scope.get('Timeline', '')}\n"
        proposal += f"- **Study Length (Months):** {scope.get('Study Length (Months)', '')}\n"
        proposal += f"- **Estimated Budget:** ${scope.get('Budget Estimate', 0):,}\n\n"
        
        proposal += "## Phases\n"
        proposal += f"### {scope.get('Phase 1 Title', '')}\n{scope.get('Phase 1 Description', '')}\n\n"
        proposal += f"### {scope.get('Phase 2 Title', '')}\n{scope.get('Phase 2 Description', '')}\n\n"
        proposal += f"### {scope.get('Phase 3 Title', '')}\n{scope.get('Phase 3 Description', '')}\n\n"
        
        proposal += "## Detailed Task Breakdown\n"
        for task in sprint_log:
            proposal += f"### {task['Task']}\n"
            proposal += f"- **Domain:** {task['Domain']}\n"
            proposal += f"- **Participants:** {task['Participants']}\n"
            proposal += f"- **Translation Needed:** {task['Translation']}\n"
            proposal += f"- **Units:** {task['Units']}\n"
            proposal += f"- **Cost:** ${task['Cost']}\n"
            mods = st.session_state.task_modifiers.get(task['Task'], {})
            if mods:
                proposal += f"- **Task Duration:** {mods.get('Task Duration', '')} days\n"
                proposal += f"- **Prerequisites:** {mods.get('Prerequisites', '')}\n"
                proposal += f"- **Notes:** {mods.get('Custom Notes', '')}\n"
            proposal += "\n"
            desc = task_df[task_df["Task Name"] == task["Task"]]["Longer Description (SOW)"]
            if not desc.empty:
                proposal += f"{desc.iloc[0]}\n\n"
                
        total_cost = sum(task["Cost"] for task in sprint_log)
        proposal += "## Cost Breakdown\n"
        proposal += f"**Total Project Cost:** ${total_cost:,.2f}\n\n"
        proposal += "## Timeline & Deliverables\n"
        proposal += "A detailed timeline and deliverables will be provided upon project initiation.\n\n"
        proposal += "## Conclusion\n"
        proposal += "We look forward to partnering with you on this project.\n\n"
        proposal += "*(End of Proposal)*\n"
        return proposal
    
    if st.button("Generate Proposal Document"):
        proposal_text = generate_proposal(scope, log)
        st.download_button("Download Proposal Markdown", proposal_text, file_name="proposal.md")
