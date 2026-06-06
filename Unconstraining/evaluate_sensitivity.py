import pandas as pd
import glob
import numpy as np
import os
from tqdm import tqdm
from sklearn.metrics import mean_squared_error

# Configuration
LF_LEVELS = [50, 60, 70, 80, 90, 95, 98, 99]
SEGMENTS = ["Contract", "General", "Perishable", "Express", "Spot"]
MODELS = ["Naive", "EM", "EMXPrice", "PD05", "PDXPrice05", "PD07", "PDXPrice07", "PD09", "PDXPrice09"]

results = []

print("Starting global sensitivity evaluation...")

for lf in LF_LEVELS:
    path = f"Unconstraining/lf_results/LF_{lf}/*.parquet"
    files = glob.glob(path)
    if not files:
        print(f"Warning: No files found for LF {lf}")
        continue
    
    # Process files for this LF level
    all_data = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    
    # Trim burn-in (last 4 years)
    all_data['Date'] = pd.to_datetime(all_data['Date'])
    min_date = all_data['Date'].min() + pd.Timedelta(days=365)
    df_eval = all_data[all_data['Date'] >= min_date].copy()
    
    # Calculate Total Oracle and Observed
    df_eval["Total_Oracle_kg"] = df_eval[[f"Oracle_{s}_kg" for s in SEGMENTS]].sum(axis=1)
    df_eval["Total_Oracle_cbm"] = df_eval[[f"Oracle_{s}_cbm" for s in SEGMENTS]].sum(axis=1)
    df_eval["Total_Observed_kg"] = df_eval[[f"Observed_{s}_kg" for s in SEGMENTS]].sum(axis=1)
    df_eval["Total_Observed_cbm"] = df_eval[[f"Observed_{s}_cbm" for s in SEGMENTS]].sum(axis=1)
    
    # Calculate Realized Load Factors (Average of all flights)
    realized_lf_kg = (df_eval["Total_Observed_kg"] / 100000.0).mean() * 100
    realized_lf_cbm = (df_eval["Total_Observed_cbm"] / 600.0).mean() * 100

    for m in MODELS:
        # 1. Reconstruct Total Estimate for this model
        est_cols_kg = [f"{m}_{s}_Est_kg" for s in SEGMENTS]
        est_cols_cbm = [f"{m}_{s}_Est_cbm" for s in SEGMENTS]
        
        # Check if model columns exist
        if not all(c in df_eval.columns for c in est_cols_kg):
            continue

        # CRITICAL FIX: Identify rows where the model has actually finished burn-in
        # We must NOT treat NaN as 0.0, or we get artificial 100% errors.
        valid_mask = df_eval[est_cols_kg].notna().all(axis=1)
        df_valid = df_eval[valid_mask].copy()
        
        if len(df_valid) == 0:
            continue

        df_valid[f"{m}_Total_Est_kg"] = df_valid[est_cols_kg].sum(axis=1)
        df_valid[f"{m}_Total_Est_cbm"] = df_valid[est_cols_cbm].sum(axis=1)
        
        # 2. Total Weight Metrics
        yt = df_valid["Total_Oracle_kg"].values
        yp = df_valid[f"{m}_Total_Est_kg"].values
        wape_kg = (np.sum(np.abs(yt - yp)) / np.sum(yt)) * 100
        
        # 3. Total Volume Metrics
        yt_c = df_valid["Total_Oracle_cbm"].values
        yp_c = df_valid[f"{m}_Total_Est_cbm"].values
        wape_cbm = (np.sum(np.abs(yt_c - yp_c)) / np.sum(yt_c)) * 100
        
        results.append({
            "Target_LF": lf,
            "Realized_LF_KG": realized_lf_kg,
            "Realized_LF_CBM": realized_lf_cbm,
            "Model": m,
            "WAPE_KG": wape_kg,
            "WAPE_CBM": wape_cbm,
            "Total_Censorship_Pct": df_valid["Is_Censored"].mean() * 100
        })

df_res = pd.DataFrame(results)
df_res.to_csv("Unconstraining/lf_sensitivity_results.csv", index=False)
print("\nSensitivity results saved to Unconstraining/lf_sensitivity_results.csv")
print(df_res.pivot(index="Model", columns="Target_LF", values="WAPE_KG"))
