import pandas as pdpython
from sklearn.linear_model import LinearRegression
import joblib

# Load simulated factory data
df = pd.read_csv("factory_data.csv")

# Create a target variable (Efficiency) if not exists
if "Efficiency" not in df.columns:
    # Example: Efficiency decreases with high temperature, increases with load
    df["Efficiency"] = df["Load"] - (df["Temperature"] - 60) * 0.5

# Features and target
X = df[["Temperature", "Speed", "Load"]]
y = df["Efficiency"]

# Train Linear Regression model
model = LinearRegression()
model.fit(X, y)

# Save model for dashboard
joblib.dump(model, "ai_model.pkl")
print("✅ AI Model trained and saved as ai_model.pkl")
