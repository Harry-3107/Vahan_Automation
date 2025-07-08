import pandas as pd
import random
import os
from faker import Faker
import mysql.connector as sql
from collections import defaultdict

# Initialize Faker
fake = Faker('en_IN')

# Allowed makers for simulation
allowed_makers = ["HONDA", "TATA", "HYUNDAI", "MARUTI"]

# Simplify maker name based on allowed brands
def simplify_maker(name):
    name = name.upper()
    for keyword in allowed_makers:
        if keyword in name:
            return keyword
    return None

# CSV mapping file paths inside 'SF_Branch_District_Mapping' folder
states_info = {
    "TAMIL NADU": {"code": "TN", "file": "Tamil_Nadu_SF_Branch_District_Mapping.csv"},
    "KARNATAKA": {"code": "KA", "file": "Karnataka_SF_Branch_District_Mapping.csv"},
    "KERALA": {"code": "KL", "file": "Kerala_SF_Branch_District_Mapping.csv"},
    "ANDHRA PRADESH": {"code": "AP", "file": "Andhra_Pradesh_SF_Branch_District_Mapping.csv"}
}

# Asset details
models = ["SANTRO", "NEXON", "SWIFT", "CITY"]
types = ["HATCHBACK", "SEDAN", "SUV"]
classes = ["SMALL CARS", "MID SIZE", "LUXURY"]
contributions = ["USED VEHICLES", "NEW VEHICLES"]

# Connect to MySQL
conn = sql.connect(
    host="localhost",
    user="root",
    password="Sanju0611!",
    database="Vahan_Project"
)
cur = conn.cursor(dictionary=True)

# Fetch aggregated market sales data
cur.execute("""
    SELECT STATE, DISTRICT, MAKER, SUM(LMV + LPV + MPV) AS TOTAL_SALES
    FROM all_state_market_data
    GROUP BY STATE, DISTRICT, MAKER
""")

market_sales_lookup = defaultdict(float)

for row in cur.fetchall():
    simple_maker = simplify_maker(row['MAKER'])
    if simple_maker:
        key = (
            row['STATE'].strip().upper(),
            row['DISTRICT'].strip().upper(),
            simple_maker
        )
        market_sales_lookup[key] += float(row['TOTAL_SALES'] or 0)

# Track generated sales per maker-district
company_sales_tracker = defaultdict(int)
all_data = []

# Generate synthetic data per state
for state_name, info in states_info.items():
    state_code = info["code"]
    csv_file = os.path.join("SF_Branch_District_Mapping", info["file"])  # Updated path

    try:
        branch_df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"❌ File not found: {csv_file}")
        continue

    # Clean columns
    branch_df.columns = branch_df.columns.str.strip().str.title()
    branch_records = branch_df.dropna().to_dict(orient="records")

    # Set target UTS for this state
    state_target = random.randint(4800, 5200)
    total_uts = 0
    attempts = 0

    while total_uts < state_target and attempts < 10000:
        attempts += 1
        record = random.choice(branch_records)
        district = record['District'].strip().upper()
        branch = record['Branch'].strip()
        maker = random.choice(allowed_makers)

        market_key = (state_name.upper(), district, maker)
        total_market_sales = market_sales_lookup.get(market_key, 0)
        current_maker_sales = company_sales_tracker[market_key]

        if total_market_sales == 0 or current_maker_sales >= total_market_sales:
            continue

        remaining = int(total_market_sales - current_maker_sales)
        max_uts = min(10, remaining, state_target - total_uts)
        if max_uts <= 0:
            continue

        uts = random.randint(1, max_uts)

        row = {
            "ACC_YYMM": fake.date_between(start_date='-1y', end_date='today').strftime("%Y%m"),
            "STATE_NAME": state_name,
            "STATE_CODE": state_code,
            "DISTRICT": district,
            "BRANCH_CODE": fake.random_int(min=100, max=999),
            "BRANCH_NAME": branch,
            "CONTR_DESC": random.choice(contributions),
            "ASSET_MAKE_DESC": maker,
            "ASSET_TYPE": random.choice(models),
            "ASSET_LEVEL2_DESC": random.choice(types),
            "ASSET_CLASS_DESC": random.choice(classes),
            "UNITS SOLD": uts
        }

        all_data.append(row)
        company_sales_tracker[market_key] += uts
        total_uts += uts

    print(f"✅ {state_name}: Generated {total_uts} UTS across {len(branch_records)} branches for allowed makers.")

# Save final dataset
df = pd.DataFrame(all_data)
df.to_csv("multi_state_vehicle_data.csv", index=False)
print(f"\n✅ Done. Total records: {len(df)}. Saved to 'multi_state_vehicle_data.csv'")
