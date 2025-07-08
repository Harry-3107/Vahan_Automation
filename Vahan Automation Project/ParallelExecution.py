# Executes all the data collection, aggregation and dumping of total market sales obtained from Vahan Dashboard
import subprocess
import os

# Get current script's folder
base_dir = os.path.dirname(os.path.abspath(__file__))
script_dir = os.path.join(base_dir, "Phase 2")

# List of script filenames
scripts = ["andhra.py", "kerala.py", "karnataka.py", "tn.py"]
processes = []

def launch_script(script_name):
    script_path = os.path.join(script_dir, script_name)
    return subprocess.Popen(["python", script_path]) 

# Step 1: Launch all 4 scripts in parallel
for script in scripts:
    p = launch_script(script)
    processes.append(p)

# Step 2: Wait for all to finish
for p in processes:
    p.wait()

# Step 3: Run the District_Data_Aggregation.py
step3_script = os.path.join(base_dir, "District_Data_Aggregation.py")
subprocess.run(["python", step3_script])

# Step 4: Run DayWiseData.py which calculates the day wise data and stores them back in the same source file
step4_script = os.path.join(base_dir, "DayWiseData.py")
subprocess.run(["python", step4_script])

# Step 5: Finally dump the aggregated daily district data into the database
final_script = os.path.join(base_dir, "MySQL_Data_Dumping.py")
subprocess.run(["python", final_script])
