import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
# This sample database covers 13 core service categories.
data = [
    # 1. Discovery & Design
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
        "Category": "Discovery & Design",
        "Subcategory": "",
        "Task Name": "Tech Scan and Innovation Brief",
        "Purpose": "Explore emerging technologies for the client’s industry.",
        "Complexity": "High",
        "Estimated Hours": 30,
        "Base Cost": 3000,
        "Staff Role(s)": "Director, Technologist",
        "Participant Involvement": "No",
        "Deliverables": "Technology Brief, Innovation Roadmap",
        "Units": 3.0,
        "Dependencies": "Initial Needs Assessment",
        "Optional Bundles": "Combined with Needs Assessment for discounted rate",
        "Tags/Modifiers": "High complexity, Industry-specific",
        "Notes": "Use for clients looking to adopt new tech."
    },
    # 2. Stakeholder & Community Engagement
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
        "Category": "Stakeholder & Community Engagement",
        "Subcategory": "",
        "Task Name": "Stakeholder Interview Series",
        "Purpose": "Conduct in-depth interviews with key stakeholders.",
        "Complexity": "Low",
        "Estimated Hours": 15,
        "Base Cost": 1500,
        "Staff Role(s)": "Interviewer, Analyst",
        "Participant Involvement": "Yes ($75 per interview)",
        "Deliverables": "Interview Summaries, Thematic Analysis",
        "Units": 1.5,
        "Dependencies": "Stakeholder identification",
        "Optional Bundles": "Interview series bundle (5 interviews)",
        "Tags/Modifiers": "Remote, On-site options",
        "Notes": "Ideal for qualitative insights."
    },
    # 3. Study Planning & IRB
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
        "Category": "Study Planning & IRB",
        "Subcategory": "",
        "Task Name": "IRB Submission & Amendment Support",
        "Purpose": "Support the IRB submission process and handle amendments.",
        "Complexity": "Medium",
        "Estimated Hours": 20,
        "Base Cost": 2000,
        "Staff Role(s)": "IRB Specialist, Research Coordinator",
        "Participant Involvement": "No",
        "Deliverables": "IRB Submission Package, Amendment Documents",
        "Units": 2.5,
        "Dependencies": "Protocol Development",
        "Optional Bundles": "IRB Bundle with Protocol Support",
        "Tags/Modifiers": "Regulatory compliance",
        "Notes": "Streamlines IRB interactions."
    },
    # 4. Participant Recruitment & Retention
    {
        "Category": "Participant Recruitment & Retention",
        "Subcategory": "",
        "Task Name": "Recruitment Strategy Design",
        "Purpose": "Develop strategies for participant recruitment.",
        "Complexity": "Medium",
        "Estimated Hours": 25,
        "Base Cost": 2500,
        "Staff Role(s)": "Recruitment Specialist, Marketing",
        "Participant Involvement": "No",
        "Deliverables": "Recruitment Plan, Screening Tools",
        "Units": 2.0,
        "Dependencies": "Study Protocol",
        "Optional Bundles": "Recruitment + Retention Bundle",
        "Tags/Modifiers": "Targeted, Demographically tailored",
        "Notes": "Key for representative samples."
    },
    {
        "Category": "Participant Recruitment & Retention",
        "Subcategory": "",
        "Task Name": "Retention & Incentive Planning",
        "Purpose": "Design strategies for participant retention and incentives.",
        "Complexity": "Low",
        "Estimated Hours": 15,
        "Base Cost": 1500,
        "Staff Role(s)": "Program Manager, Analyst",
        "Participant Involvement": "Yes (varies)",
        "Deliverables": "Retention Plan, Incentive Budget",
        "Units": 1.5,
        "Dependencies": "Recruitment Strategy",
        "Optional Bundles": "Retention Bundle",
        "Tags/Modifiers": "Flexible, Scalable",
        "Notes": "Focus on long-term engagement."
    },
    # 5. Data Collection & Management
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
        "Category": "Data Collection & Management",
        "Subcategory": "Electronic Data Capture",
        "Task Name": "REDCap Survey Administration",
        "Purpose": "Administer surveys using REDCap.",
        "Complexity": "Low",
        "Estimated Hours": 4,
        "Base Cost": 1200,
        "Staff Role(s)": "Data Manager, Analyst",
        "Participant Involvement": "Yes ($20 per participant)",
        "Deliverables": "Survey Data, Data Export",
        "Units": 1.0,
        "Dependencies": "Recruitment completed",
        "Optional Bundles": "REDCap + Self-Report Bundle",
        "Tags/Modifiers": "Automated, Secure",
        "Notes": "Efficient and scalable."
    },
    # 6. Longitudinal & Population Health Studies
    {
        "Category": "Longitudinal & Population Health Studies",
        "Subcategory": "",
        "Task Name": "Cohort Management & Follow-up",
        "Purpose": "Manage multi-timepoint data collection and follow-ups.",
        "Complexity": "High",
        "Estimated Hours": 50,
        "Base Cost": 5000,
        "Staff Role(s)": "Project Manager, Data Analyst",
        "Participant Involvement": "Yes (incentives required)",
        "Deliverables": "Cohort Dashboard, Follow-up Reports",
        "Units": 4.0,
        "Dependencies": "Initial Data Collection",
        "Optional Bundles": "Longitudinal Study Bundle",
        "Tags/Modifiers": "Multi-phase, Extended",
        "Notes": "Essential for long-term studies."
    },
    # 7. Technology & Tool Development
    {
        "Category": "Technology & Tool Development",
        "Subcategory": "",
        "Task Name": "mHealth App Prototyping",
        "Purpose": "Develop a mobile health application prototype.",
        "Complexity": "High",
        "Estimated Hours": 60,
        "Base Cost": 6000,
        "Staff Role(s)": "Software Developer, UX Designer",
        "Participant Involvement": "No",
        "Deliverables": "App Prototype, Technical Documentation",
        "Units": 5.0,
        "Dependencies": "Needs Assessment",
        "Optional Bundles": "Tech Development + Testing Bundle",
        "Tags/Modifiers": "Innovative, Agile",
        "Notes": "Prototype to validate concepts."
    },
    # 8. Implementation & Evaluation
    {
        "Category": "Implementation & Evaluation",
        "Subcategory": "",
        "Task Name": "Pilot Rollout & Evaluation",
        "Purpose": "Implement pilot studies and evaluate fidelity.",
        "Complexity": "Medium",
        "Estimated Hours": 40,
        "Base Cost": 4000,
        "Staff Role(s)": "Implementation Specialist, Analyst",
        "Participant Involvement": "Yes (pilot group)",
        "Deliverables": "Pilot Report, Evaluation Metrics",
        "Units": 3.5,
        "Dependencies": "Protocol Development",
        "Optional Bundles": "Pilot + Feedback Bundle",
        "Tags/Modifiers": "Iterative, Real-world",
        "Notes": "Monitor closely for adjustments."
    },
    # 9. Training & Capacity Building
    {
        "Category": "Training & Capacity Building",
        "Subcategory": "",
        "Task Name": "Staff Onboarding & Training",
        "Purpose": "Train staff on research protocols and tools.",
        "Complexity": "Low",
        "Estimated Hours": 20,
        "Base Cost": 2000,
        "Staff Role(s)": "Trainer, Coordinator",
        "Participant Involvement": "No",
        "Deliverables": "Training Manuals, Certification",
        "Units": 2.0,
        "Dependencies": "Protocol Finalized",
        "Optional Bundles": "Onboarding + Toolkit Bundle",
        "Tags/Modifiers": "Interactive, Modular",
        "Notes": "Essential for new team members."
    },
    # 10. Analysis & Visualization
    {
        "Category": "Analysis & Visualization",
        "Subcategory": "",
        "Task Name": "Statistical Analysis & Dashboard Creation",
        "Purpose": "Conduct analysis and create interactive dashboards.",
        "Complexity": "High",
        "Estimated Hours": 50,
        "Base Cost": 4000,
        "Staff Role(s)": "Data Scientist, Analyst",
        "Participant Involvement": "No",
        "Deliverables": "Analysis Report, Interactive Dashboard",
        "Units": 4.0,
        "Dependencies": "Data Collection completed",
        "Optional Bundles": "Analysis + Visualization Bundle",
        "Tags/Modifiers": "Data-driven, Customizable",
        "Notes": "Advanced analytics may be applied."
    },
    # 11. Dissemination & Knowledge Translation
    {
        "Category": "Dissemination & Knowledge Translation",
        "Subcategory": "",
        "Task Name": "Report Writing & Manuscript Preparation",
        "Purpose": "Develop comprehensive reports and manuscripts.",
        "Complexity": "Medium",
        "Estimated Hours": 35,
        "Base Cost": 3000,
        "Staff Role(s)": "Writer, Researcher",
        "Participant Involvement": "No",
        "Deliverables": "Final Report, Draft Manuscript",
        "Units": 3.0,
        "Dependencies": "Analysis completed",
        "Optional Bundles": "Report + Presentation Bundle",
        "Tags/Modifiers": "Academic, Peer-reviewed",
        "Notes": "Suitable for grant proposals and publications."
    },
    # 12. Strategic Advisory & Program Management
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
    },
    # 13. Data Governance, Compliance & Security
    {
        "Category": "Data Governance, Compliance & Security",
        "Subcategory": "",
        "Task Name": "HIPAA Compliance Audit & Data Governance Setup",
        "Purpose": "Ensure HIPAA compliance and set up data governance protocols.",
        "Complexity": "High",
        "Estimated Hours": 40,
        "Base Cost": 4000,
        "Staff Role(s)": "Compliance Officer, Legal Advisor",
        "Participant Involvement": "No",
        "Deliverables": "Compliance Audit Report, Governance Framework",
        "Units": 3.5,
        "Dependencies": "IRB Approval, Existing Data Policies",
        "Optional Bundles": "Compliance Bundle",
        "Tags/Modifiers": "Regulatory, Secure",
        "Notes": "Mandatory for healthcare data projects."
    }
]

df_services = pd.DataFrame(data)

# ----------------- Define Tabs -----------------
tab0, tab1, tab2, tab3 = st.tabs(["📋 Scope Setup", "🧩 Manual Builder", "📊 Dashboard", "📤 Exports"])

# ----------------- Tab 0: Scope Setup -----------------
with tab0:
    st.subheader("Define Project Scope")
    st.markdown("Enter high-level project details and key phases that inform your proposal.")
    
    scope_name = st.text_input("Project Name", value=st.session_state.scope_info.get("Project Name", ""))
    project_type = st.selectbox("Project Type", ["Research", "Program Evaluation", "Consulting", "Other"], index=0)
    study_type = st.selectbox("Study Type", ["Exploratory", "Cross-sectional", "Longitudinal", "Pilot", "RCT", "Registry"], index=0)
    estimated_n = st.number_input("Target Sample Size (N)", min_value=1, value=int(st.session_state.scope_info.get("Estimated N", 10)))
    timeline = st.selectbox("Timeline Preference", ["Standard", "Expedited"], index=0)
    study_length = st.number_input("Estimated Study Length (Months)", min_value=1, value=int(st.session_state.scope_info.get("Study Length (Months)", 6)))
    budget_estimate = st.number_input("Rough Budget Estimate ($)", min_value=0, value=int(st.session_state.scope_info.get("Budget Estimate", 100000)))
    
    st.markdown("---")
    st.markdown("### Define Key Phases")
    phase1_name = st.text_input("Phase 1 Title", value=st.session_state.scope_info.get("Phase 1 Title", "Phase 1: Discovery"))
    phase1_desc = st.text_area("Phase 1 Description", value=st.session_state.scope_info.get("Phase 1 Description", "Initial exploration, needs assessment, and stakeholder mapping."))
    phase2_name = st.text_input("Phase 2 Title", value=st.session_state.scope_info.get("Phase 2 Title", "Phase 2: Implementation"))
    phase2_desc = st.text_area("Phase 2 Description", value=st.session_state.scope_info.get("Phase 2 Description", "Execute data collection, intervention, and initial analysis."))
    phase3_name = st.text_input("Phase 3 Title", value=st.session_state.scope_info.get("Phase 3 Title", "Phase 3: Reporting"))
    phase3_desc = st.text_area("Phase 3 Description", value=st.session_state.scope_info.get("Phase 3 Description", "Final analysis, reporting, and dissemination."))
    
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
    
    st.markdown("### Task Details")
    st.markdown(f"**Task Name:** {task_info['Task Name']}")
    st.markdown(f"**Purpose:** {task_info['Purpose']}")
    st.markdown(f"**Complexity:** {task_info['Complexity']}")
    st.markdown(f"**Estimated Hours:** {task_info['Estimated Hours']}")
    st.markdown(f"**Base Cost:** ${task_info['Base Cost']:,.2f}")
    st.markdown(f"**Staff Role(s):** {task_info['Staff Role(s)']}")
    st.markdown(f"**Participant Involvement:** {task_info['Participant Involvement']}")
    st.markdown(f"**Deliverables:** {task_info['Deliverables']}")
    st.markdown(f"**Notes:** {task_info['Notes']}")
    
    # Editable modifiers stored in session_state.task_modifiers
    current_mods = st.session_state.task_modifiers.get(selected_task, {})
    
    # Optional: Let the user edit task modifiers
    if st.checkbox("Edit Task Modifiers"):
        new_modifier = st.text_area("Custom Notes / Modifiers", value=current_mods.get("Custom Notes", task_info["Notes"]))
        if st.button("Save Modifiers"):
            st.session_state.task_modifiers[selected_task] = {"Custom Notes": new_modifier}
            st.success("Modifiers updated!")
    
    st.markdown("---")
    st.markdown("### Cost Simulation")
    
    # For certain tasks, offer detailed simulation inputs; otherwise, use a generic quantity multiplier.
    if selected_task == "Self-Reported Survey Administration":
        num_surveys = st.number_input("Number of Surveys", min_value=1, value=10)
        survey_length = st.selectbox("Survey Length", ["Short (<10 min)", "Medium (10-30 min)", "Long (>30 min)"])
        delivery_method = st.selectbox("Delivery Method", ["Email", "In-Person", "Online Portal"])
        cost_multiplier = 1.0
        if survey_length == "Medium (10-30 min)":
            cost_multiplier *= 1.2
        elif survey_length == "Long (>30 min)":
            cost_multiplier *= 1.5
        if delivery_method == "In-Person":
            cost_multiplier *= 1.3
        estimated_cost = task_info["Base Cost"] * num_surveys * cost_multiplier * (1 + overhead_percent/100)
        st.markdown(f"**Estimated Cost:** ${estimated_cost:,.2f}")
        quantity = num_surveys
    elif selected_task == "Point-of-Care Blood Test":
        num_tests = st.number_input("Number of Tests", min_value=1, value=5)
        test_type = st.selectbox("Test Type", ["Standard", "Advanced (biomarker panel)"])
        cost_multiplier = 1.0
        if test_type == "Advanced (biomarker panel)":
            cost_multiplier *= 1.8
        estimated_cost = task_info["Base Cost"] * num_tests * cost_multiplier * (1 + overhead_percent/100)
        st.markdown(f"**Estimated Cost:** ${estimated_cost:,.2f}")
        quantity = num_tests
    else:
        # For tasks without detailed simulation inputs, allow the user to define a quantity.
        quantity = st.number_input("Quantity", min_value=1, value=1)
        estimated_cost = task_info["Base Cost"] * quantity * (1 + overhead_percent/100)
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
    
    if st.session_state.sprint_log:
        df_log = pd.DataFrame(st.session_state.sprint_log)
        st.dataframe(df_log, use_container_width=True)
        
        total_cost = df_log["Estimated Cost"].sum()
        st.markdown(f"**Total Project Cost:** ${total_cost:,.2f}")
        
        # Simple cost breakdown by Category
        cost_by_category = df_log.groupby("Category")["Estimated Cost"].sum().reset_index()
        fig, ax = plt.subplots()
        ax.bar(cost_by_category["Category"], cost_by_category["Estimated Cost"])
        ax.set_xlabel("Category")
        ax.set_ylabel("Cost ($)")
        ax.set_title("Cost Breakdown by Category")
        st.pyplot(fig)
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
    if sprint_log:
        for task in sprint_log:
            st.markdown(f"**{task['Task']}** (Category: {task['Category']}) — Qty: {task['Quantity']}, Cost: ${task['Estimated Cost']}")
            if task.get("Modifiers"):
                st.markdown(f"*Modifiers:* {task['Modifiers'].get('Custom Notes', '')}")
    else:
        st.info("No tasks added to the project.")
    
    # Proposal Generation Function
    def generate_proposal(scope, sprint_log):
        proposal = ""
        proposal += "# Proposal for " + scope.get("Project Name", "Untitled Project") + "\n\n"
        proposal += "## Introduction\n"
        proposal += ("This proposal outlines our comprehensive approach for the project, including our methodology, timeline, and cost breakdown. "
                     "Our team is committed to delivering high-quality outcomes tailored to your needs.\n\n")
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
