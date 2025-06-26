import pandas as pd
import random
from faker import Faker

# Initialize Faker
fake = Faker('en_IN')

# State configurations
states_info = {
    "TAMIL NADU": {"code": "TN", "file": "Tamil_Nadu_SF_Branch_District_Mapping.csv"},
    "KARNATAKA": {"code": "KA", "file": "Karnataka_SF_Branch_District_Mapping.csv"},
    "KERALA": {"code": "KL", "file": "Kerala_SF_Branch_District_Mapping.csv"},
    "ANDHRA PRADESH": {"code": "AP", "file": "Andhra_Pradesh_SF_Branch_District_Mapping.csv"}
}

# Static options
makes = ["HYUNDAI", "TATA", "MARUTI", "HONDA"]
models = ["SANTRO", "NEXON", "SWIFT", "CITY"]
types = ["HATCHBACK", "SEDAN", "SUV"]
classes = ["SMALL CARS", "MID SIZE", "LUXURY"]
contributions = ["USED VEHICLES", "NEW VEHICLES"]

# Collect all rows across states
all_data = []

for state_name, info in states_info.items():
    state_code = info["code"]
    csv_file = info["file"]

    try:
        branch_df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"❌ File not found: {csv_file}")
        continue

    branch_records = branch_df.dropna().to_dict(orient='records')

    # Track total UTS for the state
    total_uts = 0
    target_uts = random.randint(4800, 5200)  # around 5000 with small variation

    while total_uts < target_uts:
        max_uts_for_row = min(10, target_uts - total_uts)
        uts = random.randint(1, max_uts_for_row)

        record = random.choice(branch_records)

        row = {
            "ACC_YYMM": fake.date_between(start_date='-1y', end_date='today').strftime("%Y%m"),
            "STATE_NAME": state_name,
            "STATE_CODE": state_code,
            "DISTRICT": record['District'],
            "BRANCH_CODE": fake.random_int(min=100, max=999),
            "BRANCH_NAME": record['Branch'],
            "CONTR_DESC": random.choice(contributions),
            "ASSET_MAKE_DESC": random.choice(makes),
            "ASSET_TYPE": random.choice(models),
            "ASSET_LEVEL2_DESC": random.choice(types),
            "ASSET_CLASS_DESC": random.choice(classes),
            "UTS": uts
        }

        all_data.append(row)
        total_uts += uts

    print(f"✅ {state_name}: Generated {total_uts} UTS across {len(branch_records)} branches.")

# Create DataFrame and save
df = pd.DataFrame(all_data)
df.to_csv("multi_state_vehicle_data.csv", index=False)

print(f"\n✅ Done. Total records: {len(df)}. Saved to 'multi_state_vehicle_data.csv'")
