# Aggregation of data for all the RTO Branches present in a district
import os
import re
import pandas as pd

states = ["Tamil Nadu", "Karnataka", "Kerala","Andhra Pradesh"]
columns_order = ['S No', 'Maker', '2WIC', '2WN', '2WT', '3WIC', '3WN', '3WT', '4WIC',
                 'HGV', 'HMV', 'HPV', 'LGV', 'LMV', 'LPV', 'MGV', 'MMV', 'MPV', 'OTH', 'TOTAL']

def normalize_filename(folder, state, parts):
    base_pattern = state.replace(" ", "_") + "_" + "_".join(parts)
    regex_pattern = re.compile(rf"^{re.escape(base_pattern)}\.xlsx$", re.IGNORECASE)
    for fname in os.listdir(folder):
        if fname.endswith(".xlsx") and regex_pattern.match(fname):
            return os.path.join(folder, fname)
    for fname in os.listdir(folder):
        if fname.endswith(".xlsx") and all(part in fname for part in parts):
            return os.path.join(folder, fname)
    return None

for state in states:
    print(f"\n=== Processing: {state} ===")
    dmapping_folder = "RTO_District_Mapping"
    state_csv = os.path.join(dmapping_folder, f"{state.replace(' ', '_')}_RTO_District_Mapping.csv")


    input_folder = f"{state.replace(' ', '_')}_Files"
    output_folder = f"Aggregated_{state.replace(' ', '_')}_Data"

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)


    try:
        mapping_df = pd.read_csv(state_csv)
        mapping_df.columns = mapping_df.columns.str.strip()
    except FileNotFoundError:
        print(f"❌ Missing mapping: {state_csv}")
        continue

    mapping_df['District'] = mapping_df['District'].astype(str).str.strip()
    mapping_df['Branch'] = mapping_df['Branch'].astype(str).str.strip()

    for district in mapping_df['District'].dropna().unique():
        branch_list = mapping_df[mapping_df['District'] == district]['Branch'].tolist()
        all_branch_data = []

        for branch in branch_list:
            parts = branch.split()
            if len(parts) < 2:
                print(f"⚠️ Skipping invalid branch: {branch}")
                continue

            filepath = normalize_filename(input_folder, state, parts)
            if not filepath:
                print(f"❌ File not found for branch: {branch}")
                continue

            try:
                df = pd.read_excel(filepath, skiprows=3)
                df.columns = df.columns.astype(str).str.strip()
                if 'Unnamed: 1' in df.columns:
                    df.rename(columns={'Unnamed: 1': 'Maker'}, inplace=True)
                df = df[df['Maker'].notna()]
                all_branch_data.append(df)
            except Exception as e:
                print(f"❌ Error reading {os.path.basename(filepath)}: {e}")

        if all_branch_data:
            combined_df = pd.concat(all_branch_data, ignore_index=True)
            combined_df.columns = combined_df.columns.str.strip()
            combined_df = combined_df.apply(lambda col: pd.to_numeric(col, errors='ignore'))

            # Group and sum
            agg_df = combined_df.groupby("Maker", as_index=False).sum(numeric_only=True)

            for col in columns_order[2:-1]: 
                if col not in agg_df.columns:
                    agg_df[col] = 0

            agg_df['TOTAL'] = agg_df[columns_order[2:-1]].sum(axis=1)
            agg_df.insert(0, 'S No', range(1, len(agg_df) + 1))
            final_df = agg_df[columns_order]

            output_file = os.path.join(output_folder, f"{district}_makerwise.xlsx")
            final_df.to_excel(output_file, index=False)
            print(f"✅ Saved: {output_file}")
        else:
            print(f"⚠️ No data for district: {district}")
