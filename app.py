# ==============================================================
# app.py — Digital Twin Factory Simulator (FULL WORKING VERSION)
# ==============================================================

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import random
import pandas as pd
import plotly.express as px
import joblib
import os
import json
from datetime import datetime

# --------------------------------------------------------------
# PAGE CONFIG + GLOBAL AUTO REFRESH (5 SECONDS)
# --------------------------------------------------------------
st.set_page_config(page_title="Digital Twin Factory", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

# --------------------------------------------------------------
# PATHS
# --------------------------------------------------------------
FACTORY_CSV = "factory_data.csv"
ALERTS_FILE = "alerts.json"
AI_MODEL_PATH = "ai_model.pkl"

# --------------------------------------------------------------
# UPDATE FACTORY DATA EVERY REFRESH (CORE FIX)
# --------------------------------------------------------------
def update_factory_data():
    machines = [
        ("CNC-1", "Running"),
        ("CNC-2", "Running"),
        ("Lathe-1", "Running"),
        ("Mill-1", "Running"),
        ("Drill-1", "Running"),
    ]

    rows = []
    for m, status in machines:
        rows.append({
            "Machine": m,
            "Temperature": round(random.uniform(65, 100), 2),
            "Speed": round(random.uniform(500, 1500), 2),
            "Load": round(random.uniform(30, 100), 2),
            "Status": status
        })

    pd.DataFrame(rows).to_csv(FACTORY_CSV, index=False)

# --------------------------------------------------------------
# LOAD FACTORY DATA
# --------------------------------------------------------------
def read_factory_data():
    if not os.path.exists(FACTORY_CSV):
        return pd.DataFrame(
            columns=["Machine", "Temperature", "Speed", "Load", "Status"]
        )
    return pd.read_csv(FACTORY_CSV)

# --------------------------------------------------------------
# LOAD AI MODEL
# --------------------------------------------------------------
@st.cache_resource
def load_model():
    if os.path.exists(AI_MODEL_PATH):
        try:
            return joblib.load(AI_MODEL_PATH)
        except:
            return None
    return None

model = load_model()

def predict_efficiency(temp, speed, load):
    if model is None:
        return round(random.uniform(60, 95), 2)
    try:
        val = model.predict([[temp, speed, load]])[0]
        return round(max(0, min(100, val)), 2)
    except:
        return round(random.uniform(60, 95), 2)

# --------------------------------------------------------------
# ALERT SYSTEM
# --------------------------------------------------------------
def load_alerts():
    if not os.path.exists(ALERTS_FILE):
        return []
    with open(ALERTS_FILE, "r") as f:
        return json.load(f)

def save_alerts(alerts):
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)

def generate_alerts(df):
    alerts = load_alerts()

    for _, r in df.iterrows():
        if r["Temperature"] > 90 or r["Load"] > 90:
            alerts.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "machine": r["Machine"],
                "issue": "High Temperature / Load"
            })

    save_alerts(alerts[-50:])

# --------------------------------------------------------------
# UPDATE DATA + READ DATA (EVERY REFRESH)
# --------------------------------------------------------------
update_factory_data()
df = read_factory_data()
generate_alerts(df)

# --------------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------------
st.sidebar.markdown(
    "<h2 style='color:white;'>Developed by <b>Manoj C</b></h2>",
    unsafe_allow_html=True
)
st.sidebar.title("Navigation")

page = st.sidebar.selectbox(
    "Select Page",
    [
        "Dashboard",
        "CNC Machine 1",
        "CNC Machine 2",
        "Lathe Machine",
        "Milling Machine",
        "Drilling Machine",
        "Alerts"
    ]
)

# --------------------------------------------------------------
# MACHINE PAGE FUNCTION (PLACED BEFORE IF/ELIF — FIXES ERROR)
# --------------------------------------------------------------
def show_machine(machine_name, image_file=None):
    st.title(f"🔧 {machine_name}")

    d = df[df["Machine"] == machine_name].iloc[-1]

    eff = predict_efficiency(
        d["Temperature"], d["Speed"], d["Load"]
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Temperature (°C)", d["Temperature"])
    c2.metric("Speed (RPM)", d["Speed"])
    c3.metric("Load (%)", d["Load"])

    st.metric("Efficiency (%)", eff)

    fig = px.line(
        df[df["Machine"] == machine_name],
        y=["Temperature", "Speed", "Load"],
        title=f"{machine_name} Parameters Trend"
    )
    st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------------------
# PAGE ROUTING (NO FUNCTIONS BETWEEN IF / ELIF)
# --------------------------------------------------------------
if page == "Dashboard":
    st.title("🏭 Digital Twin Factory Dashboard")

    df["Efficiency"] = df.apply(
        lambda r: predict_efficiency(
            r["Temperature"], r["Speed"], r["Load"]
        ),
        axis=1
    )

    st.dataframe(df, use_container_width=True)

    fig = px.scatter(
        df,
        x="Temperature",
        y="Efficiency",
        size="Load",
        color="Machine",
        title="Machine Efficiency Overview"
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "CNC Machine 1":
    show_machine("CNC-1")

elif page == "CNC Machine 2":
    show_machine("CNC-2")

elif page == "Lathe Machine":
    show_machine("Lathe-1")

elif page == "Milling Machine":
    show_machine("Mill-1")

elif page == "Drilling Machine":
    show_machine("Drill-1")

elif page == "Alerts":
    st.title("🚨 Alerts Center")

    alerts = load_alerts()
    if alerts:
        st.dataframe(pd.DataFrame(alerts), use_container_width=True)
    else:
        st.success("No alerts detected")

# ==============================================================
# END OF FILE
# ==============================================================
