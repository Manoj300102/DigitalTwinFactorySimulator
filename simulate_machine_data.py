import random
import time
import pandas as pd

def simulate_machine_data():
    """Simulate machine temperature, speed, and load."""
    machines = ["CNC-1", "CNC-2", "Lathe-1", "Drill-1", "Mill-1"]
    data = []

    for machine in machines:
        temperature = round(random.uniform(60, 100), 2)  # °C
        speed = round(random.uniform(800, 1500), 2)      # RPM
        load = round(random.uniform(40, 100), 2)         # %
        status = random.choice(["Running", "Idle", "Maintenance"])
        data.append({
            "Machine": machine,
            "Temperature": temperature,
            "Speed": speed,
            "Load": load,
            "Status": status
        })
    return data

if __name__ == "__main__":
    print("🔄 Real-time simulation started... Updating every 5 seconds")

    while True:
        # 1. Generate new data
        simulated_data = simulate_machine_data()

        # 2. Convert to dataframe
        df = pd.DataFrame(simulated_data)

        # 3. Save CSV (this is what Streamlit reads)
        df.to_csv("factory_data.csv", index=False)

        print("✔ Updated factory_data.csv")

        # 4. Wait 5 seconds
        time.sleep(5)
