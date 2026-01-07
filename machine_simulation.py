import random
import time

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
print("Digital Twin Factory Simulator is running...")

for i in range(5):
    print(f"Machine {i+1}: Running | Temperature: {60 + i*5}°C | Load: {50 + i*3}%")


def display_machine_data(data):
    print("\n--- Digital Twin Factory Simulator ---")
    for machine in data:
        print(f"{machine['Machine']:10} | Temp: {machine['Temperature']}°C | "
              f"Speed: {machine['Speed']} RPM | Load: {machine['Load']}% | Status: {machine['Status']}")


if __name__ == "__main__":
    print("Starting Machine Simulation...\n")
    for i in range(5):  # simulate 5 cycles
        simulated_data = simulate_machine_data()
        display_machine_data(simulated_data)
        time.sleep(2)  # wait 2 seconds before next update
