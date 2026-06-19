import pandas as pd
import glob
import os

files = glob.glob('Unconstraining/results/unconstrained_3yr/*.parquet')
if not files:
    print("No files found.")
    exit()

all_data = []
for f in files:
    df = pd.read_parquet(f)
    # Get the first row since Selected_Model is constant for the whole file/segment
    selection = {c: df[c].iloc[0] for c in df.columns if "_Selected_Model" in c}
    if selection:
        selection['File'] = os.path.basename(f)
        all_data.append(selection)

if not all_data:
    print("No MoE selection data found in files.")
    exit()

df_sel = pd.DataFrame(all_data)

for col in df_sel.columns:
    if col == 'File': continue
    print(f"\n=== Frequency for {col} ===")
    counts = df_sel[col].value_counts()
    print(counts)
    print(f"Top choice: {counts.index[0]} ({counts.iloc[0]/len(df_sel)*100:.1f}%)")
