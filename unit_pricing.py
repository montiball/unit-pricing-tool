import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date, timedelta

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

# ----------------- Comprehensive Service Database -----------------
# (Sample entries; you can expand this to include all 13 core buckets.)
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
    project_type = st.selectbox("Project Type", ["Research", "Program Evaluation", "Consulting", "Other"], index=0)
    target_sample_size = st.number_input("Target Sample Size (N)", min_value=1, value=int(st.session_state.scope_info.get("Estimated N", 50)))
    rough_budget = st.number_input("Rough Budget Estimate ($)", min_value=0, value=int(st.session_state.scope_info.get("Budget Estimate", 100000)))
    study_length = st.number_input("Study Length (Months)", min_value=1, value=int(st.session_state.scope_info.get("Study Length (Months)", 12)))
    timeline_preference = st.selectbox("Timeline Preference", ["Standard", "Expedited"], index=0)
    
    # Date fields for overall project
    project_start_date = st.date_input("Project Start Date", value=st.session_state.scope_info.get("Project Start Date", date.today()))
    project_end_date = st.date_input("Project End Date", value=st.session_state.scope_info.get("Project End Date", date.today() + timedelta(days=365)))
    
    st.markdown("---")
    st.markdown("### Define Key Phases / Milestones")
    st.markdown("Define up to three phases. For each phase, provide a title, a brief description, and the phase start and end dates.")
    
    phase1_title = st.text_input("Phase 1 Title", value=st.session_state.scope_info.get("Phase 1 Title", "Phase 1: Discovery"))
    phase1_desc = st.text_area("Phase 1 Description", value=st.session_state.scope_info.get("Phase 1 Description", "Initial exploration, needs assessment, and stakeholder mapping."))
    phase1_start = st.date_input("Phase 1 Start Date", value=st.session_state.scope_info.get("Phase 1 Start Date", project_start_date))
    phase1_end = st.date_input("Phase 1 End Date", value=st.session_state.scope_info.get("Phase 1 End Date", project_start_date + timedelta(days=90)))
    
    phase2_title = st.text_input("Phase 2 Title", value=st.session_state.scope_info.get("Phase 2 Title", "Phase 2: Implementation"))
    phase2_desc = st.text_area("Phase 2 Description", value=st.session_state.scope_info.get("Phase 2 Description", "Execute data collection, interventions, and initial analysis."))
    phase2_start = st.date_input("Phase 2 Start Date", value=st.session_state.scope_info.get("Phase 2 Start Date", phase1_end + timedelta(days=1)))
    phase2_end = st.date_input("Phase 2 End Date", value=st.session_state.scope_info.get("Phase 2 End Date", phase2_start + timedelta(days=180)))
    
    phase3_title = st.text_input("Phase 3 Title", value=st.session_state.scope_info.get("Phase 3 Title", "Phase 3: Reporting"))
    phase3_desc = st.text_area("Phase 3 Description", value=st.session_state.scope_info.get("Phase 3 Description", "Final analysis, reporting, and dissemination of findings."))
    phase3_start = st.date_input("Phase 3 Start Date", value=st.session_state.scope_info.get("Phase 3 Start Date", phase2_end + timedelta(days=1)))
    phase3_end = st.date_input("Phase 3 End Date", value=st.session_state.scope_info.get("Phase 3 End Date", project_end_date))
    
    st.markdown("---")
    st.markdown("### Objectives / Deliverables")
    objectives = st.text_area("Key Objectives / Deliverables", value=st.session_state.scope_info.get("Objectives", "List the main deliverables (e.g., Final Report, Data Dashboard, Strategic Roadmap)."))
    
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
            "Phase 1 Title": phase1_title,
            "Phase 1 Description": phase1_desc,
            "Phase 1 Start Date": phase1_start,
            "Phase 1 End Date": phase1_end,
            "Phase 2 Title": phase2_title,
            "Phase 2 Description": phase2_desc,
            "Phase 2 Start Date": phase2_start,
            "Phase 2 End Date": phase2_end,
            "Phase 3 Title": phase3_title,
            "Phase 3 Description": phase3_desc,
            "Phase 3 Start Date": phase3_start,
            "Phase 3 End Date": phase3_end,
            "Objectives": objectives
        }
        st.success("Scope Setup saved or updated!")

# ----------------- Tab 1: Manual Builder -----------------
with tab1:
    st.subheader("Manual Builder & Service Selection")
    
    st.markdown("#### 1. Choose a Core Service Category")
    core_categories = df_services["Category"].unique()
    selected_category = st.selectbox("Core Category", core_categories)
    
    # Filter services based on selected category
    filtered_services = df_services[df_services["Category"] == selected_category]
    # If Subcategory is available, let user choose it
    if filtered_services["Subcategory"].nunique() > 1 or (filtered_services["Subcategory"].nunique() == 1 and filtered_services.iloc[0]["Subcategory"] != ""):
        subcategories = filtered_services["Subcategory"].unique()
        selected_subcategory = st.selectbox("Subcategory", subcategories)
        filtered_services = filtered_services[filtered_services["Subcategory"] == selected_subcategory]
    
    selected_task = st.selectbox("Select Task", filtered_services["Task Name"].unique())
    task_info = filtered_services[filtered_services["Task Name"] == selected_task].iloc[0]
    
    # Check for overrides in session_state for this task
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
    
    # Editable task details: let the user override key parameters
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
    st.markdown("### Cost Simulation")
    
    # For tasks with specific simulation options
    if selected_task == "Self-Reported Survey Administration":
        num_surveys = st.number_input("Number of Surveys", min_value=1, value=target_sample_size)
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
        st.session_state.sprint_log.append({
            "Category": task_info["Category"],
            "Subcategory": task_info["Subcategory"],
            "Task": task_info["Task Name"],
            "Quantity": quantity,
            "Estimated Cost": round(estimated_cost, 2),
            "Modifiers": st.session_state.task_modifiers.get(selected_task, {})
        })
        st.success("Task added to project!")

# ----------------- Tab 2: Dashboard -----------------
with tab2:
    st.subheader("Project Dashboard & Visualization")
    
    # Display scope info summary if available
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
        st.markdown("### Phases")
        phases = []
        for i in range(1, 4):
            phase = {
                "Title": scope.get(f"Phase {i} Title", ""),
                "Description": scope.get(f"Phase {i} Description", ""),
                "Start": scope.get(f"Phase {i} Start Date", None),
                "End": scope.get(f"Phase {i} End Date", None)
            }
            if phase["Title"]:
                phases.append(phase)
        for phase in phases:
            st.markdown(f"**{phase['Title']}**: {phase['Description']}")
            st.markdown(f"Dates: {phase['Start']} to {phase['End']}")
        st.markdown("### Objectives / Deliverables")
        st.markdown(scope.get("Objectives", ""))
    
    if st.session_state.sprint_log:
        df_log = pd.DataFrame(st.session_state.sprint_log)
        st.dataframe(df_log, use_container_width=True)
        
        total_cost = df_log["Estimated Cost"].sum()
        st.markdown(f"**Total Project Cost:** ${total_cost:,.2f}")
        
        cost_by_category = df_log.groupby("Category")["Estimated Cost"].sum().reset_index()
        fig, ax = plt.subplots()
        ax.bar(cost_by_category["Category"], cost_by_category["Estimated Cost"])
        ax.set_xlabel("Category")
        ax.set_ylabel("Cost ($)")
        ax.set_title("Cost Breakdown by Category")
        st.pyplot(fig)
        
        # Gantt chart for phases
        if scope and phases:
            st.markdown("### Project Timeline (Gantt Chart)")
            fig2, ax2 = plt.subplots(figsize=(10, len(phases) * 0.5 + 1))
            for i, phase in enumerate(phases):
                if phase["Start"] and phase["End"]:
                    start_num = mdates.date2num(phase["Start"])
                    end_num = mdates.date2num(phase["End"])
                    duration = end_num - start_num
                    ax2.barh(i, duration, left=start_num, height=0.3, color="skyblue")
                    ax2.text(start_num + duration/2, i, phase["Title"], va="center", ha="center", color="black")
            ax2.set_yticks(range(len(phases)))
            ax2.set_yticklabels([phase["Title"] for phase in phases])
            ax2.xaxis_date()
            ax2.set_xlabel("Date")
            ax2.set_title("Project Timeline")
            st.pyplot(fig2)
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
- **Study Type:** {scope.get('Study Type', '')}
- **Target Sample Size (N):** {scope.get('Estimated N', '')}
- **Timeline:** {scope.get('Timeline', '')}
- **Study Length (Months):** {scope.get('Study Length (Months)', '')}
- **Budget Estimate:** ${scope.get('Budget Estimate', 0):,}
- **Project Dates:** {scope.get('Project Start Date', '')} to {scope.get('Project End Date', '')}
- **Phases:**
  - **{scope.get('Phase 1 Title', '')}:** {scope.get('Phase 1 Description', '')} (Dates: {scope.get('Phase 1 Start Date', '')} to {scope.get('Phase 1 End Date', '')})
  - **{scope.get('Phase 2 Title', '')}:** {scope.get('Phase 2 Description', '')} (Dates: {scope.get('Phase 2 Start Date', '')} to {scope.get('Phase 2 End Date', '')})
  - **{scope.get('Phase 3 Title', '')}:** {scope.get('Phase 3 Description', '')} (Dates: {scope.get('Phase 3 Start Date', '')} to {scope.get('Phase 3 End Date', '')})
        """)
    else:
        st.info("No project scope defined yet.")
    
    st.markdown("---")
    st.markdown("### Task Breakdown")
    if sprint_log:
        for task in sprint_log:
            st.markdown(f"**{task['Task']}** (Category: {task['Category']}) — Qty: {task['Quantity']}, Cost: ${task['Estimated Cost']}")
            if task.get("Modifiers"):
                st.markdown(f"*Modifiers:* {task['Modifiers'].get('Custom Notes', '')}")
    else:
        st.info("No tasks added to the project.")
    
    def generate_proposal(scope, sprint_log):
        proposal = ""
        proposal += "# Proposal for " + scope.get("Project Name", "Untitled Project") + "\n\n"
        proposal += "## Introduction\n"
        proposal += ("This proposal outlines our comprehensive approach for the project, including our methodology, timeline, and cost breakdown. "
                     "Our team is committed to delivering high-quality outcomes tailored to your needs.\n\n")
        proposal += "## Project Overview\n"
        proposal += f"- **Partner:** {scope.get('Partner Name', '')}\n"
        proposal += f"- **Project Type:** {scope.get('Project Type', '')}\n"
        proposal += f"- **Target Sample Size (N):** {scope.get('Estimated N', '')}\n"
        proposal += f"- **Timeline:** {scope.get('Timeline', '')}\n"
        proposal += f"- **Study Length (Months):** {scope.get('Study Length (Months)', '')}\n"
        proposal += f"- **Budget Estimate:** ${scope.get('Budget Estimate', 0):,}\n"
        proposal += f"- **Project Dates:** {scope.get('Project Start Date', '')} to {scope.get('Project End Date', '')}\n\n"
        
        proposal += "## Phases\n"
        proposal += f"### {scope.get('Phase 1 Title', '')}\n{scope.get('Phase 1 Description', '')}\n"
        proposal += f"**Dates:** {scope.get('Phase 1 Start Date', '')} to {scope.get('Phase 1 End Date', '')}\n\n"
        proposal += f"### {scope.get('Phase 2 Title', '')}\n{scope.get('Phase 2 Description', '')}\n"
        proposal += f"**Dates:** {scope.get('Phase 2 Start Date', '')} to {scope.get('Phase 2 End Date', '')}\n\n"
        proposal += f"### {scope.get('Phase 3 Title', '')}\n{scope.get('Phase 3 Description', '')}\n"
        proposal += f"**Dates:** {scope.get('Phase 3 Start Date', '')} to {scope.get('Phase 3 End Date', '')}\n\n"
        
        proposal += "## Objectives / Deliverables\n"
        proposal += scope.get("Objectives", "") + "\n\n"
        
        proposal += "## Detailed Task Breakdown\n"
        for task in sprint_log:
            proposal += f"### {task['Task']} (Category: {task['Category']})\n"
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
        proposal += "We look forward to partnering with you on this project.\n\n"
        proposal += "*(End of Proposal)*\n"
        return proposal
    
    if st.button("Generate Proposal Document"):
        proposal_text = generate_proposal(scope, sprint_log)
        st.download_button("Download Proposal Markdown", proposal_text, file_name="proposal.md")
