
import streamlit as st
import pandas as pd
import openai
import matplotlib.pyplot as plt
import random
import json

st.set_page_config(page_title="Agile Sprint Planner", layout="centered")
st.title("🧠 Agile Sprint Planning Tool")
st.caption("Use units to design, price, and simulate strategic research sprints")

openai.api_key = st.secrets["openai"]["api_key"]

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🧩 Manual Builder", "🤖 GPT Planner", "📊 Sprint Log", "📈 Simulation", "💰 Unit Cost"])

# Global settings
with st.sidebar:
    st.header("🔧 Settings")
    tier1_rate = st.number_input("Tier 1 (Director)", value=300)
    tier2_rate = st.number_input("Tier 2 (Leadership)", value=200)
    tier3_rate = st.number_input("Tier 3 (Coordinator)", value=100)
    overhead_percent = st.number_input("Overhead (%)", 0, 100, 39)
    unit_price = st.number_input("Unit Price ($)", value=5000)

if "sprint_log" not in st.session_state:
    st.session_state.sprint_log = []

if "gpt_tasks" not in st.session_state:
    st.session_state.gpt_tasks = []

# Task Library
domain_tasks = {
    "Discovery & Design": [
        ("Landscape Scan", "Brief lit or market scan", 1, 2, 4, ["scan", "research"]),
        ("Discovery Workshop", "Identify goals and needs", 1, 2, 2, ["goals", "framing"]),
        ("Journey Mapping", "User experience mapping", 1, 3, 4, ["experience"])
    ],
    "User & Stakeholder Research": [
        ("Focus Group", "Moderated discussion with users", 1, 2, 8, ["focus group", "discussion"]),
        ("Stakeholder Interviews", "1:1 interviews for insights", 1, 3, 6, ["interview"]),
        ("Survey Design + Launch", "Deploy and analyze survey", 1, 3, 5, ["survey"])
    ],
    "Prototyping & Pilot Testing": [
        ("Rapid Pilot", "Deploy test in real world", 2, 4, 10, ["pilot"]),
        ("Concept Testing", "Get feedback on early ideas", 1, 3, 4, ["concept"])
    ],
    "Ongoing Strategic Guidance": [
        ("Advisory Session", "1-hour strategic check-in", 1, 1, 1, ["advisory"]),
        ("End-of-Phase Briefing", "Presentation of findings", 1, 2, 3, ["briefing"])
    ],
    "Implementation Feasibility & Real-World Value": [
        ("ROI Modeling", "Estimate costs and benefits", 2, 4, 4, ["roi"]),
        ("Community Pilot", "Test in local setting", 2, 4, 8, ["community"])
    ],
    "Regulatory & Compliance": [
        ("IRB Protocol Development", "Full IRB submission", 2, 3, 3, ["irb"]),
        ("IRB Amendment", "Modify existing protocol", 1, 1, 1, ["amendment"])
    ]
}

# ---------------- Tab 1: Manual Builder ----------------
with tab1:
    st.subheader("🧩 Manual Sprint Builder")
    domain = st.selectbox("Domain", list(domain_tasks.keys()))
    task_list = domain_tasks[domain]
    task_names = [t[0] for t in task_list]
    task_choice = st.selectbox("Task", task_names)

    selected = [t for t in task_list if t[0] == task_choice][0]
    desc, t1, t2, t3 = selected[1], selected[2], selected[3], selected[4]
    st.markdown(f"**Description:** {desc}")

    # Focus Group smart config
    if task_choice == "Focus Group":
        num_fg = st.number_input("Number of Focus Groups", 1, 10, 1)
        is_new = st.radio("New topic/theme?", ["Yes", "No"])
        irb_amend = st.checkbox("IRB Amendment Needed", value=False)

        setup_t1 = 1 if is_new == "Yes" else 0
        setup_t2 = 2 if is_new == "Yes" else 0
        setup_t3 = 2 if is_new == "Yes" else 0
        irb_cost = 1000 if is_new == "Yes" else 0
        if irb_amend:
            irb_cost += 500

        tier1_hours = setup_t1
        tier2_hours = setup_t2
        tier3_hours = setup_t3 + (6 * num_fg)
        additional_costs = st.number_input("Other Costs (travel, incentives)", value=500.0 * num_fg)
    else:
        tier1_hours = st.number_input("Tier 1 Hours", value=t1)
        tier2_hours = st.number_input("Tier 2 Hours", value=t2)
        tier3_hours = st.number_input("Tier 3 Hours", value=t3)
        additional_costs = st.number_input("Other Costs (travel, incentives)", value=500.0)
        irb_cost = 0

    staff_cost = (tier1_hours * tier1_rate + tier2_hours * tier2_rate + tier3_hours * tier3_rate)
    total_raw = staff_cost + additional_costs + irb_cost
    total_cost = total_raw * (1 + overhead_percent / 100)
    total_units = total_cost / unit_price

    st.markdown(f"**Total Cost:** ${total_cost:,.2f}")
    st.markdown(f"**Total Units:** {total_units:.2f}")

    if st.button("➕ Add to Sprint Log"):
        name = f"{num_fg}x Focus Group ({'New' if is_new == 'Yes' else 'Repeat'})" if task_choice == "Focus Group" else task_choice
        st.session_state.sprint_log.append({
            "Domain": domain, "Task": name, "Units": round(total_units, 2), "Cost": round(total_cost, 2)
        })
        st.success("Task added ✅")


# ---------------- Tab 2: GPT Planner ----------------
from openai import OpenAI
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

with tab2:
    st.subheader("🤖 GPT Sprint Planner")
    goal = st.text_area("Describe your sprint goal", key="gpt_goal_input_tab2")

    if st.button("Generate Plan with GPT"):
        prompt = "Choose 2–4 tasks from this library to match the following goal:\n"
        for domain, tasks in domain_tasks.items():
            for t in tasks:
                units = ((t[2]*tier1_rate + t[3]*tier2_rate + t[4]*tier3_rate)*(1 + overhead_percent/100))/unit_price
                prompt += f"- {domain}: {t[0]} ({units:.1f} units): {t[1]}\n"
        prompt += f"\nSprint goal: {goal}"

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=600
            )
            output = response.choices[0].message.content
            st.markdown("### Suggested Sprint Plan")
            st.markdown(output)
        except Exception as e:
            st.error(f"Error: {e}")

with tab2:
    st.subheader("🤖 GPT Sprint Planner")
    goal = st.text_area("Describe your sprint goal", key="gpt_goal_input_tab2")

    if st.button("Generate Plan with GPT"):
        prompt = "Choose 2–4 tasks from this library to match the following goal:\n"
        for domain, tasks in domain_tasks.items():
            for t in tasks:
                units = ((t[2]*tier1_rate + t[3]*tier2_rate + t[4]*tier3_rate)*(1 + overhead_percent/100))/unit_price
                prompt += f"- {domain}: {t[0]} ({units:.1f} units): {t[1]}\n"
        prompt += f"\nSprint goal: {goal}"

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7, max_tokens=600
            )
            output = response.choices[0].message.content
            st.markdown("### Suggested Sprint Plan")
            st.markdown(output)
        except Exception as e:
            st.error(f"Error: {e}")

# ---------------- Tab 3: Sprint Log ----------------
with tab3:
    st.subheader("📊 Sprint Log")
    if st.session_state.sprint_log:
        df = pd.DataFrame(st.session_state.sprint_log)
        st.dataframe(df, use_container_width=True)
        st.markdown(f"**Total Units Used:** {df['Units'].sum():.2f}")
        st.markdown(f"**Total Cost:** ${df['Cost'].sum():,.2f}")
        st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="sprint_log.csv")
    else:
        st.info("No tasks in sprint log yet.")

# ---------------- Tab 4: Simulation ----------------
with tab4:
    st.subheader("📈 Strategic Simulation")
    col1, col2 = st.columns(2)
    with col1:
        annual_units = st.number_input("Total Annual Units", value=100)
    with col2:
        quarters = st.number_input("Number of Quarters", value=4, min_value=1)

    theme = st.text_input("Optional Theme or Goal")
    sim_btn = st.button("🔮 Run Simulation")

    def weight_tasks(theme_text):
        weights = []
        for domain, tasks in domain_tasks.items():
            for name, desc, t1, t2, t3, keywords in tasks:
                score = sum(1 for word in keywords if word in theme_text.lower())
                units = ((t1 * tier1_rate + t2 * tier2_rate + t3 * tier3_rate) * (1 + overhead_percent / 100)) / unit_price
                weights.append((domain, name, units, score))
        return sorted(weights, key=lambda x: (-x[3], x[2]))

    if sim_btn:
        unit_per_q = annual_units / quarters
        task_pool = weight_tasks(theme) if theme else [
            (d, t[0], ((t[2]*tier1_rate + t[3]*tier2_rate + t[4]*tier3_rate)*(1 + overhead_percent/100))/unit_price, 0)
            for d, tasks in domain_tasks.items() for t in tasks
        ]

        plan, used = [], 0
        for q in range(quarters):
            uq = 0
            for d, t, u, _ in task_pool:
                if uq + u <= unit_per_q:
                    plan.append({"Quarter": f"Q{q+1}", "Domain": d, "Task": t, "Units": round(u, 2)})
                    uq += u
                    used += u

        df = pd.DataFrame(plan)
        st.markdown("#### Simulated Plan")
        st.dataframe(df, use_container_width=True)
        st.markdown(f"**Total Units Used:** {used:.2f} / {annual_units}")
        st.markdown(f"**Avg Units per Quarter:** {used / quarters:.2f}")

        st.markdown("#### Units by Domain")
        st.dataframe(df.groupby("Domain")["Units"].sum().reset_index())

# ---------------- Tab 5: Unit Cost Calculator ----------------
with tab5:
    st.subheader("💰 What Should a Unit Cost?")
    st.caption("Use this tool to test how much each task costs and what unit price makes sense.")

    task_data = [
        {"Task": "Focus Group", "Tier 1": 1, "Tier 2": 2, "Tier 3": 8, "Other Costs": 500},
        {"Task": "Survey + Report", "Tier 1": 1, "Tier 2": 2, "Tier 3": 5, "Other Costs": 300},
        {"Task": "Stakeholder Interviews", "Tier 1": 1, "Tier 2": 3, "Tier 3": 6, "Other Costs": 400},
    ]

    df = pd.DataFrame(task_data)
    st.markdown("### 🧩 Sample Tasks")
    st.dataframe(df, use_container_width=True)

    st.markdown("### 🔧 Cost Settings")
    c1, c2, c3, c4 = st.columns(4)
    t1 = c1.number_input("Tier 1 Rate", value=tier1_rate)
    t2 = c2.number_input("Tier 2 Rate", value=tier2_rate)
    t3 = c3.number_input("Tier 3 Rate", value=tier3_rate)
    oh = c4.number_input("Overhead %", value=overhead_percent)

    st.markdown("### 💸 Cost Per Task (with Overhead)")
    results = []
    for _, row in df.iterrows():
        base = row["Tier 1"] * t1 + row["Tier 2"] * t2 + row["Tier 3"] * t3
        cost = (base + row["Other Costs"]) * (1 + oh / 100)
        results.append({"Task": row["Task"], "Cost ($)": round(cost, 2)})

    result_df = pd.DataFrame(results)
    st.dataframe(result_df, use_container_width=True)

    total_cost = sum(r["Cost ($)"] for r in results)
    avg_cost = total_cost / len(results)
    st.markdown(f"### 📊 Average Task Cost: **${avg_cost:,.2f}**")

    proposed_price = st.slider("Try Unit Price ($)", 3000, 10000, step=250, value=int(avg_cost))
    st.markdown(f"#### 🔢 Each Task Would Use ~{avg_cost / proposed_price:.2f} Units at ${proposed_price} per Unit")
