import streamlit as st
import pandas as pd
import plotly.express as px
import joblib

st.title("🏭 Digital Twin Factory Simulator")

# Load AI model
model = joblib.load("ai_model.pkl")

# Load latest machine data
df = pd.read_csv("factory_data.csv")

# Predict efficiency
X = df[["Temperature", "Speed", "Load"]]
df["Predicted_Efficiency"] = model.predict(X)

# Scatter plot of predicted efficiency
fig = px.scatter(df, x="Temperature", y="Load", size="Predicted_Efficiency",
                 color="Predicted_Efficiency", title="Predicted Machine Efficiency")
st.plotly_chart(fig)

# Show table
st.subheader("Machine Data")
st.dataframe(df)

