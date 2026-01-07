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
    """
    Returns: (issue_text, hours_remaining)
    """

    if efficiency is None:
        efficiency = 100

    # Temperature rules
    if temp > 95:
        return "🔥 Overheat Failure Predicted", 6
    elif temp > 90:
        return "🔥 High Temperature Risk", 12
    elif temp > 85:
        return "⚠️ Temperature Rising", 24

    # Load rules
    if load > 95:
        return "⚙️ Load Overstress Likely", 8
    elif load > 90:
        return "⚙️ Heavy Load Trend", 18
    elif load > 85:
        return "⚠️ Load Increasing", 36

    # AI efficiency rules
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

        m = row["Machine"]
        temp = try_float(row["Temperature"])
        loadv = try_float(row["Load"])
        speed = try_float(row["Speed"])
        status = row["Status"]
        eff = predict_efficiency(temp, speed, loadv)

        sev = severity_for_value(temp, loadv, eff)

        reason = []
        if temp and temp > 85:
            reason.append(f"High Temp {temp}")
        if loadv and loadv > 85:
            reason.append(f"High Load {loadv}")
        if eff and eff < 60:
            reason.append(f"Low Efficiency {round(eff,1)}%")
        if status.lower() == "maintenance":
            reason.append("Maintenance State")

        if reason:
            alert = make_alert(m, sev, "; ".join(reason), row)
            if alert["id"] not in ids:
                new_alerts.append(alert)

    if new_alerts:
        save_alerts(existing + new_alerts)

    return new_alerts


# --------------------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------------------
st.sidebar.markdown("""
<h2 style='color:white; font-size:26px; margin-bottom:0px;'>
    Developed by <b>Manoj C</b>
</h2>
<hr style='border:1px solid #444;'>
""", unsafe_allow_html=True)

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

refresh = st.sidebar.button("Force Refresh")


# --------------------------------------------------------------
# LOAD DATA + GENERATE ALERTS
# --------------------------------------------------------------
df = read_factory_data()
generate_alerts(df)


# --------------------------------------------------------------
# MACHINE DETAIL PAGE FUNCTION
# --------------------------------------------------------------
def show_machine(machine_key, title, img_file):
    st_autorefresh(interval=5000, key=machine_key)

    st.title(title)
    st.image(f"static/images/{img_file}", use_container_width=True)

    df2 = df[df["Machine"] == machine_key]
    st.dataframe(df2, use_container_width=True)

    if not df2.empty:
        r = df2.iloc[-1]

        temp = try_float(r["Temperature"])
        loadv = try_float(r["Load"])
        speed = try_float(r["Speed"])
        status = r["Status"]
        eff = predict_efficiency(temp, speed, loadv)

        st.metric("Status", f"{status_light(status)} {status}")
        st.metric("Temperature", temp)
        st.metric("Load", loadv)
        st.metric("Speed", speed)
        st.metric("Efficiency", round(eff,2) if eff else "N/A")

        fig = px.scatter(df2, x="Temperature", y="Load",
                         color="Status", size="Speed")
        st.plotly_chart(fig, use_container_width=True, key=f"{machine_key}_chart")


# --------------------------------------------------------------
# DASHBOARD PAGE
# --------------------------------------------------------------
if page == "Dashboard":
    st_autorefresh(interval=5000, key="dash")
    st.markdown("""
<h1 style='font-size: 48px; color: white; text-align: center;'>
    🏭 Digital Twin Factory
</h1>
<br>
""", unsafe_allow_html=True)

    st.title("📊 Dashboard")

    if not df.empty:
        df["Status Light"] = df["Status"].apply(status_light)
        df["Predicted_Efficiency"] = df.apply(
            lambda r: predict_efficiency(
                try_float(r["Temperature"]),
                try_float(r["Speed"]),
                try_float(r["Load"])
            ), axis=1
        )

        st.dataframe(df, use_container_width=True)

        fig = px.scatter(df, x="Temperature", y="Predicted_Efficiency",
                         color="Machine", size="Load")
        st.plotly_chart(fig, use_container_width=True, key="dash_plot")


# --------------------------------------------------------------
# MACHINE GALLERY
# --------------------------------------------------------------
elif page == "Machine Gallery":
    st.title("🏭 Machine Gallery")

    col1, col2 = st.columns(2)
    with col1:
        st.write("🟢 CNC Machine 1")
        st.image("static/images/cnc1_machine.png", use_container_width=True)

        st.write("🛠 Lathe Machine")
        st.image("static/images/lathe_machine.png", use_container_width=True)

    with col2:
        st.write("🟡 CNC Machine 2")
        st.image("static/images/cnc2_machine.png", use_container_width=True)

        st.write("🔧 Milling Machine")
        st.image("static/images/milling_machine.png", use_container_width=True)

    st.write("🔩 Drilling Machine")
    st.image("static/images/drilling_machine.png", use_container_width=True)


# --------------------------------------------------------------
# MACHINE PAGES
# --------------------------------------------------------------
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


# --------------------------------------------------------------
# PREDICTIVE MAINTENANCE TIMELINE
# --------------------------------------------------------------
elif page == "Predictive Maintenance":
    st_autorefresh(interval=5000, key="pm_page")

    st.title("🔮 Predictive Maintenance Timeline")

    machines = ["CNC-1","CNC-2","Lathe-1","Mill-1","Drill-1"]
    rows = []

    for m in machines:
        d = df[df["Machine"] == m]
        if d.empty:
            continue

        latest = d.iloc[-1]

        temp = try_float(latest["Temperature"])
        loadv = try_float(latest["Load"])
        speed = try_float(latest["Speed"])
        eff = predict_efficiency(temp, speed, loadv)

        issue, hours_left = maintenance_prediction(temp, speed, loadv, eff)

        rows.append({
            "Machine": m,
            "Issue": issue,
            "Hours Left": hours_left
        })

    df_pm = pd.DataFrame(rows)
    st.dataframe(df_pm, use_container_width=True)

    fig = px.bar(df_pm, x="Machine", y="Hours Left",
                 color="Issue",
                 title="⏳ Predicted Hours Before Maintenance Needed",
                 text="Hours Left")
    st.plotly_chart(fig, use_container_width=True, key="pm_chart")


# --------------------------------------------------------------
# ALERTS PAGE
# --------------------------------------------------------------
elif page == "Alerts":
    st_autorefresh(interval=5000, key="alert_page")
    st.title("🚨 Alerts Center")

    alerts = load_alerts()

    if not alerts:
        st.success("No alerts.")
    else:
        dfA = pd.DataFrame(alerts)
        st.dataframe(dfA, use_container_width=True)

        if any(a["severity"] == "critical" for a in alerts):
            play_alert_sound()

        for _, row in dfA.iterrows():
            with st.expander(f"{row['timestamp']} — {row['machine']} — {row['severity']}"):
                st.write("Reason:", row["reason"])
                st.json(row["data"])

