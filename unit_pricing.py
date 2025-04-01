
import streamlit as st
import pandas as pd
import uuid
from openai import OpenAI

st.set_page_config(page_title="Agile Unit Pricing Tool", layout="wide")
st.title("Agile Unit Pricing Tool")

st.markdown("""
Use this tool to scope, simulate, and track research and strategy work using unit-based pricing.
- **Sprint Builder**: Add tasks manually or use GPT to generate plans
- **Sprint Log**: Track scoped tasks like a cart
- **Simulation**: Test what a sprint or quarter looks like with X units
- **Pricing Strategy**: See margin, internal costs, and partner pricing
""")
mode = st.radio("Pricing Mode", ["Partner (Rounded + Floors)", "Internal (Exact Costs)"], horizontal=True)
partner_mode = (mode == "Partner (Rounded + Floors)")
unit_price = 5000
overhead_pct = 32.9
rates = {"Tier 1": 300, "Tier 2": 200, "Tier 3": 100}
complexity_floors = {"Low": 0.5, "Medium": 1.0, "High": 1.5}

if "sprint_log" not in st.session_state:
    st.session_state["sprint_log"] = []

tabs = st.tabs(["Sprint Builder", "Sprint Log", "Simulation", "Pricing Strategy"])

# Task Library
task_library = {
    "Discovery & Design": [
        ("Discovery Workshop", "Strategic workshop to uncover needs", 1.0, 2.0, 2.0),
        ("Journey Mapping", "Experience mapping exercise", 0.5, 1.0, 2.0)
    ],
    "User & Stakeholder Research": [
        ("Focus Group (2x)", "Moderate and synthesize 2 groups", 1.0, 1.5, 6.0),
        ("Survey + Report", "Survey creation and summary", 0.5, 1.0, 2.0)
    ],
    "Prototyping & Pilot Testing": [
        ("Concept Testing", "Feedback on early idea", 0.5, 1.0, 2.0)
    ],
    "Ongoing Strategic Guidance": [
        ("Advisory Session", "1-hour consult and notes", 0.5, 0.5, 0.5)
    ],
    "Implementation Feasibility": [
        ("ROI Modeling", "High-level value analysis", 1.0, 1.5, 2.0)
    ],
    "Regulatory & Compliance": [
        ("IRB Protocol Development", "Initial IRB docs and submission", 0.5, 1.0, 3.0)
    ]
}

# Tab 1: Sprint Builder
with tabs[0]:
    st.subheader("Manual Task Builder")
    domain = st.selectbox("Domain", list(task_library.keys()))
    task_tuple = st.selectbox("Task", task_library[domain])
    task, desc, h1, h2, h3 = task_tuple
    complexity = st.selectbox("Complexity", ["Low", "Medium", "High"])

    add_costs = st.number_input("Additional Costs", value=500)
    cost = ((h1 * rates["Tier 1"]) + (h2 * rates["Tier 2"]) + (h3 * rates["Tier 3"]) + add_costs) * (1 + overhead_pct / 100)
    raw_units = cost / unit_price
    units = round(raw_units * 2) / 2 if partner_mode else round(raw_units, 2)
    if partner_mode:
        units = max(units, complexity_floors[complexity])

    st.markdown(f"**Cost:** ${cost:,.0f} | **Units:** {units}")

    if st.button("Add to Sprint Log"):
        st.session_state["sprint_log"].append({
            "Domain": domain, "Task": task, "Units": units, "Complexity": complexity
        })
        st.success("Added.")

    st.divider()
    st.subheader("GPT Plan Generator")
    if "gpt_key" not in st.session_state:
        st.session_state["gpt_key"] = f"gpt_input_{uuid.uuid4()}"
    goal = st.text_area("Describe your goal", key=st.session_state["gpt_key"])
    if st.button("Generate Plan with GPT"):
        client = OpenAI(api_key=st.secrets["openai"]["api_key"])
        prompt = "Choose 3–5 tasks from this list to match the goal below. Return the plan with 1-2 sentences per task.\n\n"
        for d, tasks in task_library.items():
            for t in tasks:
                u = ((t[2]*rates["Tier 1"] + t[3]*rates["Tier 2"] + t[4]*rates["Tier 3"])*(1 + overhead_pct/100)) / unit_price
                prompt += f"- {d}: {t[0]} ({round(u,1)} units): {t[1]}\n"
        prompt += f"\nGoal: {goal}"
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
            st.error(f"GPT Error: {e}")

# Tab 2: Sprint Log
with tabs[1]:
    st.subheader("Sprint Log")
    if not st.session_state["sprint_log"]:
        st.info("Nothing added yet.")
    else:
        df = pd.DataFrame(st.session_state["sprint_log"])
        st.dataframe(df, use_container_width=True)
        st.markdown(f"**Total Units:** {df['Units'].sum():.1f}")
        st.bar_chart(df.groupby("Domain")["Units"].sum())

# Tab 3: Simulation
with tabs[2]:
    st.subheader("Simulation")
    available = st.slider("Total Available Units", 10, 100, 25)
    example = [
        {"Domain": "Discovery & Design", "Task": "Discovery Workshop", "Units": 2.5},
        {"Domain": "User & Stakeholder Research", "Task": "Focus Group (2x)", "Units": 4.0},
        {"Domain": "Prototyping & Pilot Testing", "Task": "Concept Testing", "Units": 2.0},
        {"Domain": "Ongoing Strategic Guidance", "Task": "Advisory Session", "Units": 1.0}
    ]
    total = sum(t["Units"] for t in example)
    df = pd.DataFrame(example)
    st.dataframe(df)
    st.markdown(f"**Simulated Total Units:** {total} / {available}")

# Tab 4: Pricing Strategy
with tabs[3]:
    st.subheader("Pricing Strategy")
    margin_sample = [
        {"Task": "Discovery Workshop", "Internal": 12000, "Units": 2.5},
        {"Task": "Focus Group (2x)", "Internal": 21000, "Units": 4},
        {"Task": "Concept Testing", "Internal": 9800, "Units": 2},
        {"Task": "Advisory Session", "Internal": 4100, "Units": 1}
    ]
    for t in margin_sample:
        partner_val = t["Units"] * unit_price
        t["Partner Value"] = partner_val
        t["Margin"] = partner_val - t["Internal"]
        t["Margin %"] = round((t["Margin"] / t["Internal"]) * 100, 1)
    st.dataframe(pd.DataFrame(margin_sample), use_container_width=True)
