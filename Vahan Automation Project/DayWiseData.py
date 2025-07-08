import mysql.connector as sql
import pandas as pd
import os

# === 1. Connect to MySQL ===
conn = sql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="Sanju0611!",
    database="Vahan_Project"
)
cur = conn.cursor()

# === 2. States list ===
states = ["Tamil Nadu", "Kerala", "Karnataka", "Andhra Pradesh"]

# === 3. Column names ===
columns = ['sno', 'maker', '2WIC', '2WN', '2WT', '3WIC', '3WN', '3WT', '4WIC',
           'HGV', 'HMV', 'HPV', 'LGV', 'LMV', 'LPV', 'MGV', 'MMV', 'MPV', 'OTH', 'TOTAL']
numeric_columns = columns[2:]  # Exclude 'sno' and 'maker'

# === 4. Process each state ===
for state_name in states:
    cur.execute("SELECT DISTINCT district FROM all_state_market_data WHERE state = %s", (state_name,))
    districts = [row[0] for row in cur.fetchall()]
    print(f"\n🔄 Processing State: {state_name} | Districts Found: {len(districts)}")

    # Define folder for Excel files
    input_folder = "Aggregated_" + state_name.replace(" ", "_") + "_Data"

    # === 5. Process each district ===
    for district in districts:
        safe_name = district.title().replace("_", " ")
        excel_file = os.path.join(input_folder, f"{safe_name}_makerwise.xlsx")

        if not os.path.exists(excel_file):
            print(f"❌ Excel file not found: {excel_file}")
            continue

        # === a. Read Excel file ===
        try:
            df = pd.read_excel(excel_file)
            df.columns = columns
        except Exception as e:
            print(f"⚠️ Failed to read Excel file: {excel_file} | Error: {e}")
            continue

        # === b. Fetch DB data for district ===
        cur.execute(f'''
            SELECT sno, maker, 2WIC, 2WN, 2WT, 3WIC, 3WN, 3WT, 4WIC, HGV, HMV, HPV, 
                   LGV, LMV, LPV, MGV, MMV, MPV, OTH, TOTAL
            FROM all_state_market_data 
            WHERE district = %s
        ''', (district,))
        data = cur.fetchall()

        if not data:
            print(f"⚠️ No DB data found for: {district}")
            continue

        db_df = pd.DataFrame(data, columns=columns)

        # === c. Convert numeric columns to float ===
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            db_df[col] = pd.to_numeric(db_df[col], errors='coerce')

        # === d. Merge both dataframes on maker ===
        merged = pd.merge(df, db_df, on='maker', suffixes=('_excel', '_db'))

        if merged.empty:
            print(f"⚠️ No matching makers to compare for: {district}")
            continue

        # === e. Compute difference for matching rows ===
        difference_df = merged[['sno_excel', 'maker']].copy().rename(columns={'sno_excel': 'sno'})
        for col in numeric_columns:
            excel_col = f"{col}_excel"
            db_col = f"{col}_db"
            difference_df[col] = merged[excel_col] - merged[db_col]

        # === f. Overwrite the Excel file ===
        try:
            difference_df.to_excel(excel_file, index=False)
            print(f"✅ Overwritten with differences: {excel_file}")
        except Exception as e:
            print(f"❌ Failed to write Excel file: {excel_file} | Error: {e}")

# === 6. Close DB connection ===
cur.close()
conn.close()
