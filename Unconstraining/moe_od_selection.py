import pandas as pd
import numpy as np
import os
import glob
from tqdm import tqdm

RESULTS_DIR = "Unconstraining/results/unconstrained_3yr"
BURN_IN_DAYS = 365
SEGMENTS = ["Contract", "General", "Perishable", "Express", "Spot"]

def process_file(f_path):
    df = pd.read_parquet(f_path)
    n = len(df)
    
    cens_arr = df["Is_Censored"].values
    
    for seg in SEGMENTS:
        # Calculate stats over the burn-in period for this specific OD pair and segment
        burn_cens = cens_arr[:BURN_IN_DAYS]
        cens_rate = np.mean(burn_cens) if len(burn_cens) > 0 else 0
        
        # Calculate correlation and CV on uncensored data in burn-in
        uncens_mask = ~burn_cens
        if np.sum(uncens_mask) > 10:
            obs = df[f"Observed_{seg}_kg"].values[:BURN_IN_DAYS][uncens_mask]
            price = df[f"Price_{seg}_DP-15"].values[:BURN_IN_DAYS][uncens_mask]
            
            # Prevent division by zero or constant arrays
            if np.std(obs) > 1e-6 and np.std(price) > 1e-6:
                corr = np.corrcoef(obs, price)[0, 1]
            else:
                corr = 0
                
            cv = np.std(obs) / (np.mean(obs) + 1e-6)
        else:
            corr = 0
            cv = 0
            
        # --- OD-Level Dynamic Rule ---
        if cens_rate < 0.05:
            # Very low censoring: unconstraining introduces more variance than it fixes
            winner = "Naive"
        else:
            # Price Elasticity check
            if corr < -0.3:
                # Strong negative price elasticity: price model is highly effective
                winner = "PDXPrice07"
            elif corr < -0.1:
                # Moderate elasticity: use price model but be more conservative (lower tau)
                winner = "PDXPrice05"
            else:
                # Weak or no price elasticity: use standard PD
                if cv > 0.8:
                    # High variance demand: be conservative
                    winner = "PD05"
                else:
                    # Stable variance: standard PD
                    winner = "PD07"
            
        # Apply the selected model for all days
        df[f"MoEOD_{seg}_Est_kg"] = df[f"{winner}_{seg}_Est_kg"]
        df[f"MoEOD_{seg}_Est_cbm"] = df[f"{winner}_{seg}_Est_cbm"]
        df[f"MoEOD_{seg}_Selected_Model"] = winner
        
    df.to_parquet(f_path, index=False)

if __name__ == "__main__":
    files = glob.glob(os.path.join(RESULTS_DIR, "*.parquet"))
    print(f"Applying OD-Level Feature-Based MoE Selection to {len(files)} files...")
    
    for f_path in tqdm(files, desc="OD MoE"):
        try:
            process_file(f_path)
        except Exception as e:
            print(f"FAILED {os.path.basename(f_path)}: {e}")
            
    print("Done. New columns updated.")
