
import streamlit as st
import openai
import matplotlib.pyplot as plt
import pandas as pd
import json
from io import StringIO

st.set_page_config(page_title="Agile Sprint App", layout="centered")
st.title("Agile Sprint Planning App")

openai.api_key = st.secrets["openai"]["api_key"]

tab1, tab2, tab3 = st.tabs(["🧩 Manual Builder", "🤖 GPT Planner", "📊 Sprint Log"])

# Sidebar settings
with st.sidebar:
    st.header("Staff Rates & Settings")
    tier1_rate = st.number_input("Tier 1 (Director)", value=300)
    tier2_rate = st.number_input("Tier 2 (Leadership)", value=200)
    tier3_rate = st.number_input("Tier 3 (Coordinator)", value=100)
    overhead_percent = st.number_input("Overhead (%)", min_value=0, max_value=100, value=39)
    unit_price = st.number_input("Unit Price ($)", value=5000)

# Session state
if "sprint_log" not in st.session_state:
    st.session_state["sprint_log"] = []

if "gpt_tasks" not in st.session_state:
    st.session_state["gpt_tasks"] = []

# Tab 1 - Manual Builder
with tab1:
    st.header("🧩 Manual Sprint Builder")

    domain_tasks = {
        "User & Stakeholder Research": {
            "Focus Group (1x)": ("Recruit, moderate, and analyze 1 focus group", 1, 2, 8),
            "Stakeholder Interviews": ("Conduct up to 5 interviews and synthesize insights", 1, 3, 6),
        },
        "Regulatory & Compliance": {
            "IRB Protocol Development": ("Full IRB submission and support docs", 2, 3, 3),
            "IRB Amendment": ("Change to existing protocol", 1, 1, 1),
        }
    }

    domain = st.selectbox("Domain", list(domain_tasks.keys()))
    task = st.selectbox("Task", list(domain_tasks[domain].keys()))
    desc, t1, t2, t3 = domain_tasks[domain][task]
    st.markdown(f"**Description:** {desc}")

    tier1_hours = st.number_input("Tier 1 Hours", value=t1)
    tier2_hours = st.number_input("Tier 2 Hours", value=t2)
    tier3_hours = st.number_input("Tier 3 Hours", value=t3)
    additional_costs = st.number_input("Additional Costs", value=500.0)

    staff_cost = (tier1_hours * tier1_rate) + (tier2_hours * tier2_rate) + (tier3_hours * tier3_rate)
    total_raw_cost = staff_cost + additional_costs
    total_cost = total_raw_cost * (1 + overhead_percent / 100)
    units = total_cost / unit_price

    st.markdown(f"### Total Cost: ${total_cost:,.2f}")
    st.markdown(f"### Total Units: {units:.2f}")

    if st.button("➕ Add to Sprint Log"):
        st.session_state.sprint_log.append({
            "Domain": domain,
            "Task": task,
            "Units": round(units, 2),
            "Cost": round(total_cost, 2)
        })
        st.success("Task added to Sprint Log ✅")

# Tab 2 - GPT Planner with Add-to-Log
with tab2:
    st.header("🤖 GPT Sprint Planner")
    goal = st.text_area("Describe your sprint goal")

    if st.button("Generate GPT Plan"):
        with st.spinner("Thinking..."):
            messages = [
                {"role": "system", "content": "You are a research strategist. When given a sprint goal, return a list of 2–4 recommended research tasks categorized by agile domain (Discovery & Design, User & Stakeholder Research, etc.). Format each suggestion as: Domain - Task Name (x units): short description"},
                {"role": "user", "content": f"My sprint goal is: {goal}"}
            ]
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=700
                )
                output = response.choices[0].message.content
                st.session_state["gpt_tasks"] = []

                st.markdown("### Suggested Sprint Plan")
                for line in output.split("\n"):
                    if "-" in line and ":" in line and "(" in line:
                        domain_task, desc = line.split(":")
                        domain, task_units = domain_task.split("-", 1)
                        task = task_units.split("(")[0].strip()
                        unit_str = task_units.split("(")[1].split(")")[0].replace("x", "").strip()
                        units = float(unit_str) if unit_str.replace('.', '', 1).isdigit() else 1.0
                        st.session_state["gpt_tasks"].append({"Domain": domain.strip(), "Task": task, "Units": units, "Cost": units * unit_price})
                
                for idx, item in enumerate(st.session_state["gpt_tasks"]):
                    if st.checkbox(f"Add: {item['Domain']} - {item['Task']} ({item['Units']} units)", key=f"gpt_add_{idx}"):
                        st.session_state.sprint_log.append(item)
                        st.success(f"Added '{item['Task']}' to Sprint Log")

            except Exception as e:
                st.error(f"GPT error: {e}")

# Tab 3 - Sprint Log with Edit, Export, Visualization
with tab3:
    st.header("📊 Sprint Log")

    if len(st.session_state.sprint_log) == 0:
        st.info("No tasks have been added to the Sprint Log yet.")
    else:
        df = pd.DataFrame(st.session_state.sprint_log)
        total_units = df["Units"].sum()
        total_cost = df["Cost"].sum()

        st.markdown(f"### Total Units Used: {total_units:.2f}")
        st.markdown(f"### Total Cost: ${total_cost:,.2f}")
        st.dataframe(df, use_container_width=True)

        # Pie chart by domain
        domain_summary = df.groupby("Domain")["Units"].sum()
        fig, ax = plt.subplots()
        ax.pie(domain_summary, labels=domain_summary.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

        # Export buttons
        st.download_button("📥 Export as CSV", data=df.to_csv(index=False), file_name="sprint_log.csv", mime="text/csv")
        st.download_button("📥 Export as Markdown", data=df.to_markdown(index=False), file_name="sprint_log.md", mime="text/markdown")

        # Save & load
        st.markdown("### 💾 Save or Load Log")
        if st.download_button("⬇️ Download Sprint Log (JSON)", data=json.dumps(st.session_state.sprint_log), file_name="sprint_log.json"):
            st.success("Log downloaded.")
        uploaded_file = st.file_uploader("⬆️ Upload Sprint Log (.json)", type="json")
        if uploaded_file:
            st.session_state.sprint_log = json.load(uploaded_file)
            st.success("Sprint log loaded!")

        # Delete rows
        st.markdown("### 🗑 Remove a Task")
        for i, entry in enumerate(st.session_state.sprint_log):
            if st.button(f"Remove '{entry['Task']}'", key=f"del_{i}"):
                st.session_state.sprint_log.pop(i)
                st.rerun() 
