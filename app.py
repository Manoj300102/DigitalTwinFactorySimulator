# app.py
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import random
import pandas as pd
import plotly.express as px
import joblib
import os
import json
from datetime import datetime

st.set_page_config(page_title="Digital Twin Factory", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")
st.write("🔁 Refresh Test Number:", random.randint(1, 1000))

# --------------------------------------------------------------
# CONFIG PATHS
# --------------------------------------------------------------
FACTORY_CSV = "factory_data.csv"
ALERTS_FILE = "alerts.json"
AI_MODEL_PATHS = ["ai_model.pkl", "/mnt/data/ai_model.pkl"]

# --------------------------------------------------------------
# AUTO UPDATE FACTORY DATA EVERY 5 SECONDS  ✅ (ADDED)
# --------------------------------------------------------------
def auto_update_factory_data():
    machines = ["CNC-1", "CNC-2", "Lathe-1", "Mill-1", "Drill-1"]
    rows = []

    for m in machines:
        rows.append({
            "Machine": m,
            "Temperature": round(random.uniform(65, 100), 2),
            "Speed": round(random.uniform(500, 1500), 2),
            "Load": round(random.uniform(30, 100), 2),
            "Status": "Running"
        })

    pd.DataFrame(rows).to_csv(FACTORY_CSV, index=False)

# --------------------------------------------------------------
# SOUND ALERT FUNCTION
# --------------------------------------------------------------
def play_alert_sound():
    sound_path = "static/sounds/alert.mp3"
    js = f"""
        <script>
            var audio = new Audio('{sound_path}');
            audio.play();
        </script>
    """
    st.markdown(js, unsafe_allow_html=True)

# --------------------------------------------------------------
# LOAD AI MODEL
# --------------------------------------------------------------
@st.cache_resource
def load_ai_model():
    for p in AI_MODEL_PATHS:
        if os.path.exists(p):
            try:
                return joblib.load(p)
            except:
                pass
    return None

model = load_ai_model()

# --------------------------------------------------------------
# UTILITY HELPERS
# --------------------------------------------------------------
def safe_read_csv(path):
    try:
        return pd.read_csv(path)
    except:
        return None

def try_float(v):
    try:
        return float(v)
    except:
        return None

def read_factory_data():
    df = safe_read_csv(FACTORY_CSV)
    if df is None:
        return pd.DataFrame(columns=["Machine","Temperature","Speed","Load","Status"])
    return df

def status_light(status):
    s = str(status).lower()
    if s == "running":
        return "🟢"
    elif s == "idle":
        return "🟡"
    elif s == "maintenance":
        return "🔴"
    return "⚪"

# --------------------------------------------------------------
# AI PREDICTION
# --------------------------------------------------------------
def predict_efficiency(temp, speed, load):
    if model is None:
        return None
    try:
        val = float(model.predict([[temp, speed, load]])[0])
        return max(0, min(100, val * 100 if val <= 1 else val))
    except:
        return None

# --------------------------------------------------------------
# PREDICTIVE MAINTENANCE
# --------------------------------------------------------------
def maintenance_prediction(temp, speed, load, efficiency):
    if efficiency is None:
        efficiency = 100

    if temp > 95:
        return "🔥 Overheat Failure Predicted", 6
    elif temp > 90:
        return "🔥 High Temperature Risk", 12
    elif temp > 85:
        return "⚠️ Temperature Rising", 24

    if load > 95:
        return "⚙️ Load Overstress Likely", 8
    elif load > 90:
        return "⚙️ Heavy Load Trend", 18
    elif load > 85:
        return "⚠️ Load Increasing", 36

    if efficiency < 30:
        return "🔩 Critical Efficiency Drop", 10
    elif efficiency < 50:
        return "🔩 Efficiency Declining", 24
    elif efficiency < 70:
        return "🛠 Maintenance Suggested Soon", 48

    return "✅ No Issues — Stable", 72

# --------------------------------------------------------------
# ALERT SYSTEM
# --------------------------------------------------------------
def load_alerts():
    if not os.path.exists(ALERTS_FILE):
        return []
    try:
        with open(ALERTS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_alerts(alerts):
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)

def make_alert(machine, severity, reason, row):
    return {
        "id": f"{machine}_{int(datetime.utcnow().timestamp()*1000)}",
        "machine": machine,
        "severity": severity,
        "reason": reason,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "acknowledged": False,
        "data": {
            "Temperature": try_float(row["Temperature"]),
            "Load": try_float(row["Load"]),
            "Speed": try_float(row["Speed"]),
            "Status": row["Status"]
        }
    }

def severity_for_value(temp, load, eff):
    if temp and temp > 95 or load > 95 or (eff and eff < 30):
        return "critical"
    if temp and temp > 85 or load > 85 or (eff and eff < 60):
        return "warning"
    return "info"

def generate_alerts(df):
    existing = load_alerts()
    ids = {a["id"] for a in existing}
    new_alerts = []

    if df.empty:
        return []

    last = df.groupby("Machine", as_index=False).last()

    for _, row in last.iterrows():
        temp = try_float(row["Temperature"])
        loadv = try_float(row["Load"])
        speed = try_float(row["Speed"])
        eff = predict_efficiency(temp, speed, loadv)

        reason = []
        if temp and temp > 85:
            reason.append(f"High Temp {temp}")
        if loadv and loadv > 85:
            reason.append(f"High Load {loadv}")
        if eff and eff < 60:
            reason.append(f"Low Efficiency {round(eff,1)}%")

        if reason:
            alert = make_alert(row["Machine"], "warning", "; ".join(reason), row)
            if alert["id"] not in ids:
                new_alerts.append(alert)

    if new_alerts:
        save_alerts(existing + new_alerts)

# --------------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------------
st.sidebar.title("Navigation")

page = st.sidebar.selectbox("Select Page", [
    "Dashboard",
    "Machine Gallery",
    "CNC Machine 1",
    "CNC Machine 2",
    "Lathe Machine",
    "Milling Machine",
    "Drilling Machine",
    "Predictive Maintenance",
    "Alerts"
])

# --------------------------------------------------------------
# LOAD DATA + GENERATE ALERTS  ✅ (ONLY ADDITION USED HERE)
# --------------------------------------------------------------
auto_update_factory_data()
df = read_factory_data()
generate_alerts(df)

# --------------------------------------------------------------
# MACHINE DETAIL FUNCTION
# --------------------------------------------------------------
def show_machine(machine_key, title, img_file):
    st.title(title)
    st.image(f"static/images/{img_file}", use_container_width=True)

    df2 = df[df["Machine"] == machine_key]
    st.dataframe(df2, use_container_width=True)

    if not df2.empty:
        r = df2.iloc[-1]
        eff = predict_efficiency(
            try_float(r["Temperature"]),
            try_float(r["Speed"]),
            try_float(r["Load"])
        )

        st.metric("Temperature", r["Temperature"])
        st.metric("Speed", r["Speed"])
        st.metric("Load", r["Load"])
        st.metric("Efficiency", eff if eff else "N/A")

# --------------------------------------------------------------
# PAGE ROUTING (UNCHANGED)
# --------------------------------------------------------------
if page == "Dashboard":
    st.title("📊 Dashboard")
    st.dataframe(df, use_container_width=True)

elif page == "Machine Gallery":
    st.title("🏭 Machine Gallery")

elif page == "CNC Machine 1":
    show_machine("CNC-1", "CNC Machine 1", "cnc1_machine.png")

elif page == "CNC Machine 2":
    show_machine("CNC-2", "CNC Machine 2", "cnc2_machine.png")

elif page == "Lathe Machine":
    show_machine("Lathe-1", "Lathe Machine", "lathe_machine.png")

elif page == "Milling Machine":
    show_machine("Mill-1", "Milling Machine", "milling_machine.png")

elif page == "Drilling Machine":
    show_machine("Drill-1", "Drilling Machine", "drilling_machine.png")

elif page == "Alerts":
    st.title("🚨 Alerts")
    st.dataframe(pd.DataFrame(load_alerts()), use_container_width=True)
