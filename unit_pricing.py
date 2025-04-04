import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import openai

# Set your OpenAI API key securely from Streamlit secrets.
openai.api_key = st.secrets["openai"]["api_key"]

# ----------------- Page Configuration -----------------
st.set_page_config(page_title="Dynamic Research Project Scoping Tool", layout="wide")
st.title("Dynamic Research Project Scoping Tool")
st.caption("From broad scoping to detailed proposals across 13 core service categories.")

# ----------------- Global Settings in Sidebar -----------------
with st.sidebar:
    st.header("🔧 Global Settings")
    tier1_rate = st.number_input("Tier 1 (Director) Rate ($/hr)", value=300)
    tier2_rate = st.number_input("Tier 2 (Leadership) Rate ($/hr)", value=200)
    tier3_rate = st.number_input("Tier 3 (Coordinator) Rate ($/hr)", value=100)
    overhead_percent = st.number_input("Overhead / Indirect (%)", min_value=0, max_value=100, value=39, step=1)
    unit_price = st.number_input("Unit Price ($ per unit)", min_value=100, step=100, value=5000)

# ----------------- Running Cost Summary Container in Sidebar -----------------
cost_container = st.sidebar.container()
with cost_container:
    st.markdown("### Running Project Cost Summary")
    if st.session_state.sprint_log:
        df_log = pd.DataFrame(st.session_state.sprint_log)
        if "Direct Cost" not in df_log.columns:
            df_log["Direct Cost"] = 0
        total_direct_cost = df_log["Direct Cost"].sum()
        overhead_amount = total_direct_cost * (overhead_percent / 100)
        total_project_cost = total_direct_cost + overhead_amount
        st.write(f"**Total Direct Cost:** ${total_direct_cost:,.2f}")
        st.write(f"**Overhead ({overhead_percent}%):** ${overhead_amount:,.2f}")
        st.write(f"**Total Project Cost:** ${total_project_cost:,.2f}")
    else:
        st.write("No tasks added yet.")


# ----------------- Initialize Session State -----------------
if "sprint_log" not in st.session_state:
    st.session_state.sprint_log = []
if "scope_info" not in st.session_state:
    st.session_state.scope_info = {}
if "task_modifiers" not in st.session_state:
    st.session_state.task_modifiers = {}
# We'll store phases as a list of dictionaries.
if "phases" not in st.session_state:
    st.session_state.phases = []

# ----------------- Default Template Cost Function -----------------
def compute_task_cost(task_category, subcategory, num_units, custom_overrides=None):
    """
    Computes labor cost based on default templates.
    For Data Collection & Management tasks:
      - "Self-Reported Survey": fixed overhead for Tier 1 and Tier 2 plus variable hours for Tier 3 per unit.
      - "Clinical Measure": fixed hours for all tiers.
    For other categories, fixed defaults are used.
    
    Returns: labor_cost, tier1_hours, tier2_hours, tier3_hours
    """
    if task_category == "Data Collection & Management":
        if subcategory == "Self-Reported Survey":
            defaults = {"tier1_fixed": 2, "tier2_fixed": 1, "tier3_per_unit": 0.2}
        elif subcategory == "Clinical Measure":
            defaults = {"tier1_fixed": 1, "tier2_fixed": 1, "tier3_fixed": 1}
        else:
            defaults = {"tier1_fixed": 1, "tier2_fixed": 1, "tier3_fixed": 1}
    elif task_category == "Discovery & Design":
        defaults = {"tier1_fixed": 4, "tier2_fixed": 2, "tier3_fixed": 1}
    else:
        defaults = {"tier1_fixed": 1, "tier2_fixed": 1, "tier3_fixed": 1}
    
    if custom_overrides:
        defaults.update(custom_overrides)
    
    if task_category == "Data Collection & Management":
        if subcategory == "Self-Reported Survey":
            tier1_hours = defaults.get("tier1_fixed", 2)
            tier2_hours = defaults.get("tier2_fixed", 1)
            tier3_hours = num_units * defaults.get("tier3_per_unit", 0.2)
        elif subcategory == "Clinical Measure":
            tier1_hours = defaults.get("tier1_fixed", 1)
            tier2_hours = defaults.get("tier2_fixed", 1)
            tier3_hours = defaults.get("tier3_fixed", 1)
        else:
            tier1_hours = defaults.get("tier1_fixed", 1)
            tier2_hours = defaults.get("tier2_fixed", 1)
            tier3_hours = defaults.get("tier3_fixed", 1)
    else:
        tier1_hours = defaults.get("tier1_fixed", 1)
        tier2_hours = defaults.get("tier2_fixed", 1)
        tier3_hours = defaults.get("tier3_fixed", 1)
    
    labor_cost = (tier1_hours * tier1_rate) + (tier2_hours * tier2_rate) + (tier3_hours * tier3_rate)
    return labor_cost, tier1_hours, tier2_hours, tier3_hours

# ----------------- Comprehensive Service Database -----------------
data = [
    {
        "Category": "Discovery & Design",
        "Subcategory": "",
        "Task Name": "Initial Needs Assessment",
        "Purpose": "Determine client requirements and market opportunities.",
        "Complexity": "Medium",
        "Estimated Hours": 20,
        "Base Cost": 2000,
        "Staff Role(s)": "Strategy Consultant, Analyst",
        "Participant Involvement": "No",
        "Deliverables": "Needs Assessment Report, Strategic Recommendations",
        "Notes": "Ideal for early-stage projects."
    },
    {
        "Category": "Stakeholder & Community Engagement",
        "Subcategory": "",
        "Task Name": "Community Focus Group",
        "Purpose": "Gather insights from community members.",
        "Complexity": "Medium",
        "Estimated Hours": 25,
        "Base Cost": 2500,
        "Staff Role(s)": "Facilitator, Analyst",
        "Participant Involvement": "Yes ($50 per participant)",
        "Deliverables": "Focus Group Report, Transcripts",
        "Notes": "Adjust group size based on client needs."
    },
    {
        "Category": "Study Planning & IRB",
        "Subcategory": "",
        "Task Name": "Protocol Development",
        "Purpose": "Develop research protocols and study designs.",
        "Complexity": "High",
        "Estimated Hours": 40,
        "Base Cost": 4000,
        "Staff Role(s)": "Research Scientist, IRB Specialist",
        "Participant Involvement": "No",
        "Deliverables": "Study Protocol Document, IRB Submission Package",
        "Notes": "Essential for clinical research."
    },
    {
        "Category": "Data Collection & Management",
        "Subcategory": "Self-Reported Survey",
        "Task Name": "Self-Reported Survey Administration",
        "Purpose": "Administer surveys to collect self-reported data.",
        "Complexity": "Low",
        "Estimated Hours": 10,
        "Base Cost": 1000,
        "Staff Role(s)": "Survey Administrator, Analyst",
        "Participant Involvement": "Yes ($25 per participant)",
        "Deliverables": "Survey Data, Summary Report",
        "Notes": "Low cost and scalable."
    },
    {
        "Category": "Data Collection & Management",
        "Subcategory": "Clinical Measure",
        "Task Name": "Point-of-Care Blood Test",
        "Purpose": "Conduct a point-of-care blood test.",
        "Complexity": "Medium",
        "Estimated Hours": 3,
        "Base Cost": 1500,
        "Staff Role(s)": "Lab Technician, Nurse",
        "Participant Involvement": "Yes (incentivized)",
        "Deliverables": "Test Results, Report",
        "Notes": "Advanced options available."
    },
    {
        "Category": "Strategic Advisory & Program Management",
        "Subcategory": "",
        "Task Name": "Project Coordination & Roadmap Development",
        "Purpose": "Manage project timelines and develop strategic roadmaps.",
        "Complexity": "Medium",
        "Estimated Hours": 30,
        "Base Cost": 2500,
        "Staff Role(s)": "Project Manager, Advisor",
        "Participant Involvement": "No",
        "Deliverables": "Project Roadmap, Coordination Report",
        "Notes": "Ideal for complex projects."
    }
]

df_services = pd.DataFrame(data)

# ----------------- Define Tabs -----------------
# Renaming Tab 2 to "Project Cart and Dashboard"
tab0, tab1, tab2, tab3 = st.tabs(["📋 Scope Setup", "🧩 Manual Builder", "🛒 Project Cart and Dashboard", "📤 Exports"])

# ----------------- Tab 0: Scope Setup -----------------
with tab0:
    st.subheader("Define Project Scope")
    st.markdown("Enter high-level project details that will inform your proposal and planning. These details will automatically influence other sections of the app.")
    
    project_name = st.text_input("Project Name", value=st.session_state.scope_info.get("Project Name", ""))
    project_description = st.text_area("Project Description", value=st.session_state.scope_info.get("Project Description", ""))
    partner_name = st.text_input("Partner Name", value=st.session_state.scope_info.get("Partner Name", ""))
    
    project_type = st.selectbox("Project Type", 
                                ["Pilot Study", "Cross-sectional", "Longitudinal", "Mixed Methods", "Experimental", 
                                 "Evaluation", "Education", "Training", "Strategic Guidance", "Other"],
                                index=0)
    
    target_sample_size = st.number_input("Target Sample Size (N)", min_value=1, value=int(st.session_state.scope_info.get("Estimated N", 50)))
    rough_budget = st.number_input("Rough Budget Estimate ($)", min_value=0, value=int(st.session_state.scope_info.get("Budget Estimate", 100000)))
    
    study_length = st.number_input("Study Length (Months)", min_value=1, value=int(st.session_state.scope_info.get("Study Length (Months)", 12)))
    timeline_preference = st.selectbox("Timeline Preference", ["Standard", "Expedited"], index=0)
    
    project_start_date = st.date_input("Project Start Date", value=st.session_state.scope_info.get("Project Start Date", date.today()))
    project_end_date = project_start_date + relativedelta(months=study_length)
    st.markdown(f"**Computed Project End Date:** {project_end_date}")
    
    st.markdown("---")
    st.markdown("### Define Project Phases / Milestones")
    st.markdown("Instead of manually choosing dates, please specify the number of phases and the duration (in weeks) for each phase. The start and end dates will be computed automatically.")
    num_phases = st.number_input("Number of Phases", min_value=1, value=len(st.session_state.phases) if st.session_state.phases else 3)
    
    # Initialize phases list if necessary
    if len(st.session_state.phases) != num_phases:
        st.session_state.phases = [{"Title": "", "Description": "", "DurationWeeks": 4} for _ in range(num_phases)]
    
    current_start = project_start_date
    for idx, phase in enumerate(st.session_state.phases):
        with st.expander(f"Phase {idx+1} Details"):
            phase_title = st.text_input("Phase Title", value=phase.get("Title", ""), key=f"phase_title_{idx}")
            phase_desc = st.text_area("Phase Description", value=phase.get("Description", ""), key=f"phase_desc_{idx}")
            duration_weeks = st.number_input("Duration (weeks)", min_value=1, value=phase.get("DurationWeeks", 4), key=f"duration_{idx}")
            phase_end = current_start + timedelta(days=duration_weeks*7 - 1)
            st.write(f"**Computed Phase Dates:** {current_start} to {phase_end}")
            st.session_state.phases[idx] = {
                "Title": phase_title,
                "Description": phase_desc,
                "Start": current_start,
                "End": phase_end,
                "DurationWeeks": duration_weeks
            }
            current_start = phase_end + timedelta(days=1)
    
    st.markdown("---")
    st.markdown("### Broad Project Goals")
    project_goals = st.text_area("Enter broad project goals (e.g., maximize ROI, establish a scalable model, strategic outcomes)", 
                                 value=st.session_state.scope_info.get("Project Goals", ""))
    
    if st.button("Save / Update Scope Setup"):
        st.session_state.scope_info = {
            "Project Name": project_name,
            "Project Description": project_description,
            "Partner Name": partner_name,
            "Project Type": project_type,
            "Estimated N": target_sample_size,
            "Budget Estimate": rough_budget,
            "Study Length (Months)": study_length,
            "Timeline": timeline_preference,
            "Project Start Date": project_start_date,
            "Project End Date": project_end_date,
            "Project Goals": project_goals
        }
        st.success("Scope Setup saved or updated!")

# ----------------- Tab 1: Manual Builder -----------------
with tab1:
    st.subheader("Manual Builder & Service Selection")
    
    st.markdown("#### 1. Choose a Core Service Category")
    core_categories = df_services["Category"].unique()
    selected_category = st.selectbox("Core Category", core_categories)
    
    filtered_services = df_services[df_services["Category"] == selected_category]
    if filtered_services["Subcategory"].nunique() > 1 or (filtered_services["Subcategory"].nunique() == 1 and filtered_services.iloc[0]["Subcategory"] != ""):
        subcategories = filtered_services["Subcategory"].unique()
        selected_subcategory = st.selectbox("Subcategory", subcategories)
        filtered_services = filtered_services[filtered_services["Subcategory"] == selected_subcategory]
    
    selected_task = st.selectbox("Select Task", filtered_services["Task Name"].unique())
    task_info = filtered_services[filtered_services["Task Name"] == selected_task].iloc[0]
    
    overrides = st.session_state.task_modifiers.get(selected_task, {})
    effective_hours = overrides.get("Estimated Hours", task_info.get("Estimated Hours", 0))
    effective_base_cost = overrides.get("Base Cost", task_info.get("Base Cost", 0))
    effective_complexity = overrides.get("Complexity", task_info.get("Complexity", ""))
    effective_notes = overrides.get("Custom Notes", task_info.get("Notes", ""))
    
    st.markdown("### Task Details")
    st.markdown(f"**Task Name:** {task_info['Task Name']}")
    st.markdown(f"**Purpose:** {task_info['Purpose']}")
    st.markdown(f"**Complexity:** {effective_complexity}")
    st.markdown(f"**Estimated Hours:** {effective_hours}")
    st.markdown(f"**Base Cost:** ${effective_base_cost:,.2f}")
    st.markdown(f"**Staff Role(s):** {task_info['Staff Role(s)']}")
    st.markdown(f"**Participant Involvement:** {task_info['Participant Involvement']}")
    st.markdown(f"**Deliverables:** {task_info['Deliverables']}")
    st.markdown(f"**Notes:** {effective_notes}")
    
    if st.checkbox("Edit Task Details"):
        new_est_hours = st.number_input("Estimated Hours", value=effective_hours, key="edit_est_hours")
        new_base_cost = st.number_input("Base Cost", value=effective_base_cost, key="edit_base_cost")
        new_complexity = st.selectbox("Complexity", ["Low", "Medium", "High"],
                                      index=["Low", "Medium", "High"].index(effective_complexity) if effective_complexity in ["Low", "Medium", "High"] else 1, key="edit_complexity")
        new_notes = st.text_area("Notes", value=effective_notes, key="edit_notes")
        if st.button("Save Task Details", key="save_task_details"):
            st.session_state.task_modifiers[selected_task] = {
                "Estimated Hours": new_est_hours,
                "Base Cost": new_base_cost,
                "Complexity": new_complexity,
                "Custom Notes": new_notes
            }
            st.success("Task details updated!")
    
    st.markdown("---")
    st.markdown("### Assign Task to a Phase")
    phases_list = [phase["Title"] for phase in st.session_state.phases if phase.get("Title")]
    phase_assignment = st.selectbox("Select Phase for this Task", options=phases_list) if phases_list else None
    
    st.markdown("---")
    st.markdown("### Cost Simulation")
    if task_info["Category"] == "Data Collection & Management":
        if task_info["Subcategory"] == "Self-Reported Survey":
            num_units = st.number_input("Number of Surveys", min_value=1, value=st.session_state.scope_info.get("Estimated N", 50))
            labor_cost, t1, t2, t3 = compute_task_cost(task_info["Category"], task_info["Subcategory"], num_units, st.session_state.task_modifiers.get(selected_task, {}))
            direct_cost = labor_cost  # Direct cost (without overhead)
            st.markdown(f"**Computed Labor Cost:** ${labor_cost:,.2f}")
            st.markdown(f"Breakdown: Tier 1 = {t1} hrs, Tier 2 = {t2} hrs, Tier 3 = {t3} hrs")
            st.markdown(f"**Direct Cost:** ${direct_cost:,.2f}")
            quantity = num_units
        elif task_info["Subcategory"] == "Clinical Measure":
            num_units = st.number_input("Number of Tests", min_value=1, value=5)
            labor_cost, t1, t2, t3 = compute_task_cost(task_info["Category"], task_info["Subcategory"], num_units, st.session_state.task_modifiers.get(selected_task, {}))
            direct_cost = labor_cost
            st.markdown(f"**Computed Labor Cost:** ${labor_cost:,.2f}")
            st.markdown(f"Breakdown: Tier 1 = {t1} hrs, Tier 2 = {t2} hrs, Tier 3 = {t3} hrs")
            st.markdown(f"**Direct Cost:** ${direct_cost:,.2f}")
            quantity = num_units
        else:
            quantity = st.number_input("Quantity", min_value=1, value=1)
            direct_cost = effective_base_cost * quantity
            st.markdown(f"**Direct Cost:** ${direct_cost:,.2f}")
    else:
        quantity = st.number_input("Quantity", min_value=1, value=1)
        direct_cost = effective_base_cost * quantity
        st.markdown(f"**Direct Cost:** ${direct_cost:,.2f}")
    
    if st.button("➕ Add Task to Project"):
        task_entry = {
            "Category": task_info["Category"],
            "Subcategory": task_info["Subcategory"],
            "Task": task_info["Task Name"],
            "Quantity": quantity,
            "Direct Cost": round(direct_cost, 2),
            "Modifiers": st.session_state.task_modifiers.get(selected_task, {})
        }
        if phase_assignment:
            task_entry["Phase"] = phase_assignment
        st.session_state.sprint_log.append(task_entry)
        st.success("Task added to project!")

# ----------------- Tab 2: Project Cart and Dashboard -----------------
with tab2:
    st.subheader("Project Cart and Dashboard")
    
    scope = st.session_state.scope_info
    if scope:
        st.markdown("### Project Overview")
        st.markdown(f"**Project Name:** {scope.get('Project Name', '')}")
        st.markdown(f"**Partner:** {scope.get('Partner Name', '')}")
        st.markdown(f"**Project Type:** {scope.get('Project Type', '')}")
        st.markdown(f"**Target Sample Size (N):** {scope.get('Estimated N', '')}")
        st.markdown(f"**Budget Estimate:** ${scope.get('Budget Estimate', 0):,}")
        st.markdown(f"**Study Length (Months):** {scope.get('Study Length (Months)', '')}")
        st.markdown(f"**Timeline:** {scope.get('Timeline', '')}")
        st.markdown(f"**Project Dates:** {scope.get('Project Start Date', '')} to {scope.get('Project End Date', '')}")
        st.markdown("### Project Phases")
        for phase in st.session_state.phases:
            if phase.get("Title"):
                st.markdown(f"**{phase['Title']}**: {phase['Description']}")
                st.markdown(f"Dates: {phase['Start']} to {phase['End']}")
        st.markdown("### Broad Project Goals")
        st.markdown(scope.get("Project Goals", ""))
    
    # Display tasks with remove/edit capabilities
    if st.session_state.sprint_log:
        st.markdown("### Project Cart")
        # Iterate over tasks and include a Remove button for each.
        for idx, task in enumerate(st.session_state.sprint_log):
            col1, col2 = st.columns([8, 2])
            with col1:
                phase_info = f" (Phase: {task.get('Phase')})" if task.get("Phase") else ""
                st.markdown(f"**{task['Task']}** (Category: {task['Category']}){phase_info} — Qty: {task['Quantity']}, Direct Cost: ${task['Direct Cost']}, Total Cost: ${round(task['Direct Cost']*(1+overhead_percent/100),2)}")
                if task.get("Modifiers"):
                    st.markdown(f"*Modifiers:* {task['Modifiers'].get('Custom Notes', '')}")
            with col2:
                if st.button("Remove", key=f"remove_task_{idx}"):
                    st.session_state.sprint_log.pop(idx)
                    st.experimental_rerun()
                    
        df_log = pd.DataFrame(st.session_state.sprint_log)
        total_direct_cost = df_log["Direct Cost"].sum() if not df_log.empty else 0
        overhead_amount = total_direct_cost * (overhead_percent / 100)
        total_project_cost = total_direct_cost + overhead_amount
        st.markdown(f"**Total Direct Cost:** ${total_direct_cost:,.2f}")
        st.markdown(f"**Overhead:** ${overhead_amount:,.2f}")
        st.markdown(f"**Total Project Cost:** ${total_project_cost:,.2f}")
        # Warning if cost exceeds budget
        if scope and total_project_cost > scope.get("Budget Estimate", float('inf')):
            st.warning("Total project cost exceeds your rough budget estimate. Consider adjusting your cart.")
        
        # Charts
        cost_by_category = df_log.groupby("Category")["Direct Cost"].sum().reset_index()
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(cost_by_category["Category"], cost_by_category["Direct Cost"])
        ax.set_xlabel("Category")
        ax.set_ylabel("Direct Cost ($)")
        ax.set_title("Direct Cost by Category")
        st.pyplot(fig)
        
        if "Phase" in df_log.columns and df_log["Phase"].notna().any():
            cost_by_phase = df_log.groupby("Phase")["Direct Cost"].sum()
            fig2, ax2 = plt.subplots()
            ax2.pie(cost_by_phase, labels=cost_by_phase.index, autopct="%1.1f%%", startangle=90)
            ax2.set_title("Direct Cost Distribution by Phase")
            st.pyplot(fig2)
        
        phases_list = [phase for phase in st.session_state.phases if phase.get("Title")]
        if phases_list:
            st.markdown("### Project Timeline (Gantt Chart)")
            fig3, ax3 = plt.subplots(figsize=(10, len(phases_list) * 0.5 + 1))
            for i, phase in enumerate(phases_list):
                if phase["Start"] and phase["End"]:
                    start_num = mdates.date2num(phase["Start"])
                    end_num = mdates.date2num(phase["End"])
                    duration = end_num - start_num
                    ax3.barh(i, duration, left=start_num, height=0.3, color="skyblue")
                    ax3.text(start_num + duration/2, i, phase["Title"], va="center", ha="center", color="black")
            ax3.set_yticks(range(len(phases_list)))
            ax3.set_yticklabels([phase["Title"] for phase in phases_list])
            ax3.xaxis_date()
            ax3.set_xlabel("Date")
            ax3.set_title("Project Timeline")
            st.pyplot(fig3)
    else:
        st.info("No tasks have been added to the project yet.")

# ----------------- Tab 3: Exports & Proposal Generation -----------------
with tab3:
    st.subheader("Export & Proposal Generation")
    scope = st.session_state.scope_info
    sprint_log = st.session_state.sprint_log
    
    if scope:
        st.markdown(f"### Project: {scope.get('Project Name', 'Untitled')}")
        st.markdown(f"""
- **Partner:** {scope.get('Partner Name', '')}
- **Project Type:** {scope.get('Project Type', '')}
- **Target Sample Size (N):** {scope.get('Estimated N', '')}
- **Timeline:** {scope.get('Timeline', '')}
- **Study Length (Months):** {scope.get('Study Length (Months)', '')}
- **Budget Estimate:** ${scope.get('Budget Estimate', 0):,}
- **Project Dates:** {scope.get('Project Start Date', '')} to {scope.get('Project End Date', '')}
        """)
        st.markdown("### Project Phases")
        for phase in st.session_state.phases:
            if phase.get("Title"):
                st.markdown(f"**{phase['Title']}**: {phase['Description']} (Dates: {phase['Start']} to {phase['End']})")
        st.markdown("### Broad Project Goals")
        st.markdown(scope.get("Project Goals", ""))
    else:
        st.info("No project scope defined yet.")
    
    st.markdown("---")
    st.markdown("### Task Breakdown")
    if sprint_log:
        for task in sprint_log:
            phase_info = f" (Phase: {task.get('Phase')})" if task.get("Phase") else ""
            st.markdown(f"**{task['Task']}** (Category: {task['Category']}){phase_info} — Qty: {task['Quantity']}, Direct Cost: ${task['Direct Cost']}, Total Cost: ${round(task['Direct Cost']*(1+overhead_percent/100),2)}")
            if task.get("Modifiers"):
                st.markdown(f"*Modifiers:* {task['Modifiers'].get('Custom Notes', '')}")
    else:
        st.info("No tasks added to the project.")
    
    # AI Proposal Generation Section
    def generate_ai_prompt(scope, sprint_log):
        historical_inspiration = (
            "Our previous proposal, 'A Vision for the Development of a Protocol for a Longitudinal Healthy Aging Study in The Villages, Florida,' "
            "was structured around key sections including Approach, Proposed Work Plan, Project Timeline, Coordination Plan, Budget/Cost-Estimate, "
            "Material Assumptions, Staffing and Roles, and Prior Work & Established Expertise. These themes should inspire the tone, depth, and structure of the new proposal."
        )
        prompt = f"Generate a detailed, professional proposal for the following project using the provided structured data and historical inspiration.\n\n"
        prompt += f"Project Name: {scope.get('Project Name', 'Untitled Project')}\n"
        prompt += f"Project Description: {scope.get('Project Description', '')}\n"
        prompt += f"Partner: {scope.get('Partner Name', 'N/A')}\n"
        prompt += f"Project Type: {scope.get('Project Type', 'N/A')}\n"
        prompt += f"Target Sample Size: {scope.get('Estimated N', 'N/A')}\n"
        prompt += f"Budget: ${scope.get('Budget Estimate', 'N/A')}\n"
        prompt += f"Study Length: {scope.get('Study Length (Months)', 'N/A')} months (from {scope.get('Project Start Date', 'N/A')} to {scope.get('Project End Date', 'N/A')})\n\n"
        
        prompt += "Phases:\n"
        for phase in st.session_state.phases:
            if phase.get("Title"):
                prompt += f"- {phase['Title']}: {phase['Description']} (from {phase['Start']} to {phase['End']})\n"
        prompt += "\nTasks:\n"
        for task in sprint_log:
            phase_info = f" (Phase: {task.get('Phase')})" if task.get("Phase") else ""
            prompt += f"- {task['Task']}{phase_info}: Quantity {task['Quantity']}, Direct Cost ${task['Direct Cost']}\n"
            if task.get("Modifiers"):
                prompt += f"  - Notes: {task['Modifiers'].get('Custom Notes', '')}\n"
        prompt += "\nCost Summary:\n"
        df_log = pd.DataFrame(sprint_log)
        total_direct_cost = df_log["Direct Cost"].sum() if not df_log.empty else 0
        overhead_amount = total_direct_cost * (overhead_percent / 100)
        total_project_cost = total_direct_cost + overhead_amount
        prompt += f"Total Direct Cost: ${total_direct_cost:,.2f}\n"
        prompt += f"Overhead ({overhead_percent}%): ${overhead_amount:,.2f}\n"
        prompt += f"Total Project Cost: ${total_project_cost:,.2f}\n\n"
        
        prompt += "Historical Inspiration:\n"
        prompt += historical_inspiration + "\n\n"
        
        prompt += ("Based on these details, generate a detailed proposal narrative that includes the following sections: "
                   "Introduction, Approach, Proposed Work Plan, Project Timeline, Coordination Plan, Budget/Cost-Estimate, "
                   "Material Assumptions, Staffing and Roles, and Prior Work & Established Expertise. The narrative should be persuasive, "
                   "professional, and structured for a multi-page document.")
        return prompt

    if st.button("Generate Proposal with AI"):
        scope = st.session_state.scope_info
        sprint_log = st.session_state.sprint_log
        prompt = generate_ai_prompt(scope, sprint_log)
        st.markdown("**Prompt sent to AI:**")
        st.code(prompt)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1500,
            temperature=0.7
        )
        ai_proposal = response.choices[0].text.strip()
        st.text_area("AI-Generated Proposal", ai_proposal, height=400)
    
    if st.button("Generate Proposal Document"):
        def generate_proposal(scope, sprint_log):
            proposal = ""
            proposal += "# Proposal for " + scope.get("Project Name", "Untitled Project") + "\n\n"
            proposal += "## Introduction\n"
            proposal += ("This proposal outlines our comprehensive approach for the project, including methodology, timeline, and cost breakdown. "
                         "Our team is committed to delivering high-quality outcomes tailored to your needs.\n\n")
            proposal += "## Project Overview\n"
            proposal += f"- **Partner:** {scope.get('Partner Name', '')}\n"
            proposal += f"- **Project Type:** {scope.get('Project Type', '')}\n"
            proposal += f"- **Target Sample Size (N):** {scope.get('Estimated N', '')}\n"
            proposal += f"- **Timeline:** {scope.get('Timeline', '')}\n"
            proposal += f"- **Study Length (Months):** {scope.get('Study Length (Months)', '')}\n"
            proposal += f"- **Budget Estimate:** ${scope.get('Budget Estimate', 0):,}\n"
            proposal += f"- **Project Dates:** {scope.get('Project Start Date', '')} to {scope.get('Project End Date', '')}\n\n"
            
            proposal += "## Project Phases\n"
            for phase in st.session_state.phases:
                if phase.get("Title"):
                    proposal += f"### {phase['Title']}\n"
                    proposal += f"{phase['Description']}\n"
                    proposal += f"**Dates:** {phase['Start']} to {phase['End']}\n\n"
            
            proposal += "## Broad Project Goals\n"
            proposal += scope.get("Project Goals", "") + "\n\n"
            
            proposal += "## Detailed Task Breakdown\n"
            for task in sprint_log:
                phase_info = f" (Phase: {task.get('Phase')})" if task.get("Phase") else ""
                proposal += f"### {task['Task']} (Category: {task['Category']}){phase_info}\n"
                proposal += f"- **Quantity:** {task['Quantity']}\n"
                proposal += f"- **Direct Cost:** ${task['Direct Cost']}\n"
                proposal += f"- **Total Cost (with overhead):** ${round(task['Direct Cost']*(1+overhead_percent/100),2)}\n"
                if task.get("Modifiers"):
                    proposal += f"- **Modifiers:** {task['Modifiers'].get('Custom Notes', '')}\n"
                proposal += "\n"
            df_log = pd.DataFrame(sprint_log)
            if "Direct Cost" not in df_log.columns:
                df_log["Direct Cost"] = 0
            total_direct_cost = df_log["Direct Cost"].sum()
            overhead_amount = total_direct_cost * (overhead_percent / 100)
            total_project_cost = total_direct_cost + overhead_amount
            proposal += "## Cost Breakdown\n"
            proposal += f"**Total Direct Cost:** ${total_direct_cost:,.2f}\n\n"
            proposal += f"**Overhead ({overhead_percent}%):** ${overhead_amount:,.2f}\n\n"
            proposal += f"**Total Project Cost:** ${total_project_cost:,.2f}\n\n"
            proposal += "## Timeline & Deliverables\n"
            proposal += "A detailed timeline and deliverables will be provided upon project initiation.\n\n"
            proposal += "## Conclusion\n"
            proposal += ("Based on our experience and the defined scope, we are confident that our approach will maximize ROI "
                         "and deliver actionable outcomes for your organization.\n\n")
            proposal += "*(End of Proposal)*\n"
            return proposal
        
        prop_text = generate_proposal(st.session_state.scope_info, st.session_state.sprint_log)
        st.download_button("Download Proposal Markdown", prop_text, file_name="proposal.md")
