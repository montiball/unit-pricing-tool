import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date
from dateutil.relativedelta import relativedelta

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

# ----------------- Initialize Session State -----------------
if "sprint_log" not in st.session_state:
    st.session_state.sprint_log = []
if "scope_info" not in st.session_state:
    st.session_state.scope_info = {}
if "task_modifiers" not in st.session_state:
    st.session_state.task_modifiers = {}
if "phases" not in st.session_state:
    st.session_state.phases = []  # List of phase dictionaries

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
        "Units": 2.0,
        "Dependencies": "None",
        "Optional Bundles": "Needs Assessment + Competitive Analysis Bundle",
        "Tags/Modifiers": "Remote, Quick-turnaround",
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
        "Units": 2.5,
        "Dependencies": "Pre-screening of participants",
        "Optional Bundles": "Focus Group + Survey Pack",
        "Tags/Modifiers": "Culturally tailored, Virtual/In-person",
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
        "Units": 4.0,
        "Dependencies": "Needs Assessment completed",
        "Optional Bundles": "Protocol + Training Manual Bundle",
        "Tags/Modifiers": "Regulatory, Detailed",
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
        "Units": 1.0,
        "Dependencies": "Recruitment completed",
        "Optional Bundles": "Survey + Focus Group Bundle",
        "Tags/Modifiers": "Email, Online",
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
        "Units": 1.0,
        "Dependencies": "IRB Approval",
        "Optional Bundles": "Clinical Bundle",
        "Tags/Modifiers": "Standard, Advanced",
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
        "Units": 2.5,
        "Dependencies": "Initial Planning",
        "Optional Bundles": "Full-Service Management Bundle",
        "Tags/Modifiers": "Strategic, Comprehensive",
        "Notes": "Ideal for complex projects."
    }
]

df_services = pd.DataFrame(data)

# ----------------- Define Tabs -----------------
tab0, tab1, tab2, tab3 = st.tabs(["📋 Scope Setup", "🧩 Manual Builder", "📊 Dashboard", "📤 Exports"])

# ----------------- Tab 0: Scope Setup -----------------
with tab0:
    st.subheader("Define Project Scope")
    st.markdown("Enter high-level project details that will inform your proposal and planning. These details will automatically influence other sections of the app.")
    
    # Basic project info
    project_name = st.text_input("Project Name", value=st.session_state.scope_info.get("Project Name", ""))
    project_description = st.text_area("Project Description", value=st.session_state.scope_info.get("Project Description", ""))
    partner_name = st.text_input("Partner Name", value=st.session_state.scope_info.get("Partner Name", ""))
    
    # More specific project types
    project_type = st.selectbox("Project Type", 
                                ["Pilot Study", "Cross-sectional", "Longitudinal", "Mixed Methods", "Experimental", 
                                 "Evaluation", "Education", "Training", "Strategic Guidance", "Other"],
                                index=0)
    
    target_sample_size = st.number_input("Target Sample Size (N)", min_value=1, value=int(st.session_state.scope_info.get("Estimated N", 50)))
    rough_budget = st.number_input("Rough Budget Estimate ($)", min_value=0, value=int(st.session_state.scope_info.get("Budget Estimate", 100000)))
    
    study_length = st.number_input("Study Length (Months)", min_value=1, value=int(st.session_state.scope_info.get("Study Length (Months)", 12)))
    timeline_preference = st.selectbox("Timeline Preference", ["Standard", "Expedited"], index=0)
    
    project_start_date = st.date_input("Project Start Date", value=st.session_state.scope_info.get("Project Start Date", date.today()))
    # Automatically compute end date based on study length
    project_end_date = project_start_date + relativedelta(months=study_length)
    st.markdown(f"**Computed Project End Date:** {project_end_date}")
    
    st.markdown("---")
    st.markdown("### Define Project Phases / Milestones")
    st.markdown("Add as many phases as needed. Each phase is for internal planning and proposal structuring.")
    
    # Display current phases using expanders
    if st.session_state.phases:
        for idx, phase in enumerate(st.session_state.phases):
            with st.expander(f"Phase {idx+1}: {phase.get('Title', 'New Phase')}"):
                phase_title = st.text_input("Phase Title", value=phase.get("Title", ""), key=f"phase_title_{idx}")
                phase_desc = st.text_area("Phase Description", value=phase.get("Description", ""), key=f"phase_desc_{idx}")
                phase_start = st.date_input("Phase Start Date", value=phase.get("Start", project_start_date), key=f"phase_start_{idx}")
                phase_end = st.date_input("Phase End Date", value=phase.get("End", project_end_date), key=f"phase_end_{idx}")
                # Update the phase in session state
                st.session_state.phases[idx] = {
                    "Title": phase_title,
                    "Description": phase_desc,
                    "Start": phase_start,
                    "End": phase_end
                }
                if st.button("Remove Phase", key=f"remove_phase_{idx}"):
                    # Remove the phase without calling experimental_rerun()
                    phases_copy = st.session_state.phases.copy()
                    phases_copy.pop(idx)
                    st.session_state.phases = phases_copy
                    st.success("Phase removed. Please click 'Save / Update Scope Setup' to refresh.")
    
    if st.button("Add New Phase"):
        st.session_state.phases.append({
            "Title": "",
            "Description": "",
            "Start": project_start_date,
            "End": project_end_date
        })
        st.success("New phase added. Please review and update as needed.")
    
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
    effective_hours = overrides.get("Estimated Hours", task_info["Estimated Hours"])
    effective_base_cost = overrides.get("Base Cost", task_info["Base Cost"])
    effective_complexity = overrides.get("Complexity", task_info["Complexity"])
    effective_notes = overrides.get("Custom Notes", task_info["Notes"])
    
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
                                      index=["Low", "Medium", "High"].index(effective_complexity), key="edit_complexity")
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
    phases = [phase["Title"] for phase in st.session_state.phases if phase.get("Title")]
    phase_assignment = st.selectbox("Select Phase for this Task", options=phases) if phases else None
    
    st.markdown("---")
    st.markdown("### Cost Simulation")
    if selected_task == "Self-Reported Survey Administration":
        num_surveys = st.number_input("Number of Surveys", min_value=1, value=st.session_state.scope_info.get("Estimated N", 50))
        survey_length = st.selectbox("Survey Length", ["Short (<10 min)", "Medium (10-30 min)", "Long (>30 min)"])
        delivery_method = st.selectbox("Delivery Method", ["Email", "In-Person", "Online Portal"])
        cost_multiplier = 1.0
        if survey_length == "Medium (10-30 min)":
            cost_multiplier *= 1.2
        elif survey_length == "Long (>30 min)":
            cost_multiplier *= 1.5
        if delivery_method == "In-Person":
            cost_multiplier *= 1.3
        estimated_cost = effective_base_cost * num_surveys * cost_multiplier * (1 + overhead_percent/100)
        st.markdown(f"**Estimated Cost:** ${estimated_cost:,.2f}")
        quantity = num_surveys
    elif selected_task == "Point-of-Care Blood Test":
        num_tests = st.number_input("Number of Tests", min_value=1, value=5)
        test_type = st.selectbox("Test Type", ["Standard", "Advanced (biomarker panel)"])
        cost_multiplier = 1.0
        if test_type == "Advanced (biomarker panel)":
            cost_multiplier *= 1.8
        estimated_cost = effective_base_cost * num_tests * cost_multiplier * (1 + overhead_percent/100)
        st.markdown(f"**Estimated Cost:** ${estimated_cost:,.2f}")
        quantity = num_tests
    else:
        quantity = st.number_input("Quantity", min_value=1, value=1)
        estimated_cost = effective_base_cost * quantity * (1 + overhead_percent/100)
        st.markdown(f"**Estimated Cost:** ${estimated_cost:,.2f}")
    
    if st.button("➕ Add Task to Project"):
        task_entry = {
            "Category": task_info["Category"],
            "Subcategory": task_info["Subcategory"],
            "Task": task_info["Task Name"],
            "Quantity": quantity,
            "Estimated Cost": round(estimated_cost, 2),
            "Modifiers": st.session_state.task_modifiers.get(selected_task, {})
        }
        if phase_assignment:
            task_entry["Phase"] = phase_assignment
        st.session_state.sprint_log.append(task_entry)
        st.success("Task added to project!")

# ----------------- Tab 2: Dashboard -----------------
with tab2:
    st.subheader("Project Dashboard & Visualization")
    
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
    
    if st.session_state.sprint_log:
        df_log = pd.DataFrame(st.session_state.sprint_log)
        st.dataframe(df_log, use_container_width=True)
        
        total_cost = df_log["Estimated Cost"].sum()
        st.markdown(f"**Total Project Cost:** ${total_cost:,.2f}")
        
        # Bar chart by category
        cost_by_category = df_log.groupby("Category")["Estimated Cost"].sum().reset_index()
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(cost_by_category["Category"], cost_by_category["Estimated Cost"])
        ax.set_xlabel("Category")
        ax.set_ylabel("Cost ($)")
        ax.set_title("Cost by Category")
        st.pyplot(fig)
        
        # Pie chart by phase
        if "Phase" in df_log.columns and df_log["Phase"].notna().any():
            cost_by_phase = df_log.groupby("Phase")["Estimated Cost"].sum()
            fig2, ax2 = plt.subplots()
            ax2.pie(cost_by_phase, labels=cost_by_phase.index, autopct="%1.1f%%", startangle=90)
            ax2.set_title("Cost Distribution by Phase")
            st.pyplot(fig2)
        
        # Gantt chart for phases
        phases = [phase for phase in st.session_state.phases if phase.get("Title")]
        if phases:
            st.markdown("### Project Timeline (Gantt Chart)")
            fig3, ax3 = plt.subplots(figsize=(10, len(phases) * 0.5 + 1))
            for i, phase in enumerate(phases):
                if phase["Start"] and phase["End"]:
                    start_num = mdates.date2num(phase["Start"])
                    end_num = mdates.date2num(phase["End"])
                    duration = end_num - start_num
                    ax3.barh(i, duration, left=start_num, height=0.3, color="skyblue")
                    ax3.text(start_num + duration/2, i, phase["Title"], va="center", ha="center", color="black")
            ax3.set_yticks(range(len(phases)))
            ax3.set_yticklabels([phase["Title"] for phase in phases])
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
            st.markdown(f"**{task['Task']}** (Category: {task['Category']}){phase_info} — Qty: {task['Quantity']}, Cost: ${task['Estimated Cost']}")
            if task.get("Modifiers"):
                st.markdown(f"*Modifiers:* {task['Modifiers'].get('Custom Notes', '')}")
    else:
        st.info("No tasks added to the project.")
    
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
            proposal += f"- **Estimated Cost:** ${task['Estimated Cost']}\n"
            if task.get("Modifiers"):
                proposal += f"- **Modifiers:** {task['Modifiers'].get('Custom Notes', '')}\n"
            proposal += "\n"
        total_cost = sum(task["Estimated Cost"] for task in sprint_log)
        proposal += "## Cost Breakdown\n"
        proposal += f"**Total Project Cost:** ${total_cost:,.2f}\n\n"
        proposal += "## Timeline & Deliverables\n"
        proposal += "A detailed timeline and deliverables will be provided upon project initiation.\n\n"
        proposal += "## Conclusion\n"
        proposal += ("Based on our experience and the defined scope, we are confident that our approach will maximize ROI "
                     "and deliver actionable outcomes for your organization.\n\n")
        proposal += "*(End of Proposal)*\n"
        return proposal
    
    if st.button("Generate Proposal Document"):
        proposal_text = generate_proposal(scope, sprint_log)
        st.download_button("Download Proposal Markdown", proposal_text, file_name="proposal.md")
