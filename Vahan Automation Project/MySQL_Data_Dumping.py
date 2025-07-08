import mysql.connector as sql
import datetime
import pandas as pd
import os

conn = sql.connect(host="localhost", port=3306, user="root", password="Sanju0611!")
cur = conn.cursor()
cur.execute("CREATE DATABASE IF NOT EXISTS Vahan_Project")
conn.database = 'Vahan_Project'
cur.execute("Use Vahan_Project")
cur.execute('''
    CREATE TABLE IF NOT EXISTS RTO_District_Mapping (
        Branch VARCHAR(75) PRIMARY KEY,
        Code VARCHAR(10) NOT NULL,
        District VARCHAR(75) NOT NULL,
        State VARCHAR(25) NOT NULL
    );
''')

all_states = ["Tamil_Nadu", "Andhra_Pradesh", "Karnataka", "Kerala"]

for state in all_states:
    mapping_folder = "RTO_District_Mapping"
    filename = os.path.join(mapping_folder, state + "_RTO_District_Mapping.csv")
    df = pd.read_csv(filename)

    print(f"\n✅ Loaded {len(df)} records from {filename}")
    print(df.head()) 

    insert_query = '''INSERT INTO RTO_District_Mapping (Branch, Code, District, State) VALUES (%s, %s, %s, %s);'''

    for _, row in df.iterrows():
        values = (
            str(row['Branch']),
            str(row['Code']),
            str(row['District']),
            state
        )
        try:
            cur.execute(insert_query, values)
        except sql.IntegrityError as e:
            print(f"⚠️ Skipping duplicate Branch: {row['Branch']} — {e}")

print("\n✅ All data committed to RTO_District_Mapping table.")

df=pd.read_csv("multi_state_vehicle_data.csv")

create_table_query = """
CREATE TABLE IF NOT EXISTS SF_branch_data (
    ACC_YYMM VARCHAR(20),
    STATE_NAME VARCHAR(100),
    STATE_CODE VARCHAR(10),
    DISTRICT VARCHAR(100),
    BRANCH_CODE VARCHAR(20),
    BRANCH_NAME VARCHAR(100),
    CONTR_DESC VARCHAR(100),
    ASSET_MAKE_DESC VARCHAR(100),
    ASSET_TYPE VARCHAR(50),
    ASSET_LEVEL2_DESC VARCHAR(100),
    ASSET_CLASS_DESC VARCHAR(100),
    UNITS_SOLD INT,
    DATA_TIMESTAMP DATETIME
);
"""
cur.execute(create_table_query)

insert_query = """
INSERT INTO SF_branch_data (
    ACC_YYMM, STATE_NAME, STATE_CODE, DISTRICT, BRANCH_CODE, BRANCH_NAME,
    CONTR_DESC, ASSET_MAKE_DESC, ASSET_TYPE, ASSET_LEVEL2_DESC, ASSET_CLASS_DESC, UNITS_SOLD,DATA_TIMESTAMP
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

for _, row in df.iterrows():
    values = (
        str(row['ACC_YYMM']),
        str(row['STATE_NAME']),
        str(row['STATE_CODE']),
        str(row['DISTRICT']),
        str(row['BRANCH_CODE']),
        str(row['BRANCH_NAME']),
        str(row['CONTR_DESC']),
        str(row['ASSET_MAKE_DESC']),
        str(row['ASSET_TYPE']),
        str(row['ASSET_LEVEL2_DESC']),
        str(row['ASSET_CLASS_DESC']),
        int(row['UNITS SOLD']) if pd.notna(row['UNITS SOLD']) else 0,
        datetime.now()
    )
    cur.execute(insert_query, values)

conn.commit()
print("✅ Data inserted into SF_branch_data")

# Create the table only once
cquery = '''
    CREATE TABLE IF NOT EXISTS all_state_market_data(
        SOURCE_NAME varchar(100),
        SNO INT,
        MAKER VARCHAR(100),
        2WIC INT,
        2WN INT,
        2WT INT,
        3WIC INT,
        3WN INT,
        3WT INT,
        4WIC INT,
        HGV INT,
        HMV INT,
        HPV INT,
        LGV INT,
        LMV INT,
        LPV INT,
        MGV INT,
        MMV INT,
        MPV INT,
        OTH INT,
        TOTAL INT,
        DISTRICT VARCHAR(50) NOT NULL,
        STATE VARCHAR(50) NOT NULL,
        DATA_TIMESTAMP DATETIME
    );
'''
cur.execute(cquery)

states = ["Tamil_Nadu", "Kerala", "Karnataka", "Andhra_Pradesh"]
for state in states:
    squery = f"SELECT DISTRICT FROM RTO_DISTRICT_MAPPING WHERE STATE = '{state}' GROUP BY DISTRICT;"
    cur.execute(squery)
    rows = cur.fetchall()

    all_districts = set()
    for row in rows:
        district_name = row[0].strip()
        all_districts.add(district_name.capitalize())

    folder = "Aggregated_" + state + "_Data"
    print(folder)
    for district in all_districts:
        filename = district + "_makerwise.xlsx"
        filepath = os.path.join(folder, filename)

        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue    

        df = pd.read_excel(filepath)  # No skiprows
        df.columns = [col.strip() for col in df.columns]  # Clean headers
        df.fillna(0, inplace=True)

        # Convert numeric columns to int safely
        numeric_cols = [col for col in df.columns if col != 'Maker']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        iquery = '''
            INSERT INTO all_state_market_data 
            (SOURCE_NAME,SNO, MAKER, 2WIC, 2WN, 2WT, 3WIC, 3WN, 3WT, 4WIC, HGV, HMV, HPV, LGV, LMV, LPV, MGV, MMV, MPV, OTH, TOTAL,DISTRICT,STATE,DATA_TIMESTAMP)
            VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)
        '''

        for _, row in df.iterrows():
            try:
                values = (
                    filename,
                    int(row['S No']),
                    str(row['Maker']),
                    int(row['2WIC']),
                    int(row['2WN']),
                    int(row['2WT']),
                    int(row['3WIC']),
                    int(row['3WN']),
                    int(row['3WT']),
                    int(row['4WIC']),
                    int(row['HGV']),
                    int(row['HMV']),
                    int(row['HPV']),
                    int(row['LGV']),
                    int(row['LMV']),
                    int(row['LPV']),
                    int(row['MGV']),
                    int(row['MMV']),
                    int(row['MPV']),
                    int(row['OTH']),
                    int(row['TOTAL']),
                    district,
                    state.replace("_"," "),
                    datetime.now()
                    
                )

                cur.execute(iquery, values)
                conn.commit()  # Commit after each state's districts
                
            except Exception as e:
                print(f"\n❌ Error inserting row in file: {filename}")
                print("Row contents:", row.to_dict())
                print("Error message:", e)
        print("Added data from state:",state)
            

conn.close()
