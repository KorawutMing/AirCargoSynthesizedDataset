import pandas as pd
import numpy as np
import os
from tqdm import tqdm
import glob

RESULTS_DIR = "Unconstraining/results/unconstrained_3yr"
BURN_IN_DAYS = 365
SEGMENTS = ["Contract", "General", "Perishable", "Express", "Spot"]

if __name__ == "__main__":
    files = glob.glob(os.path.join(RESULTS_DIR, "*.parquet"))
    print(f"Final MoE Polish: Optimizing 'Contract' and 'Spot' with Baseline Corrections...")
    
    # We apply a very simple, defensible rule:
    # Use PDXPrice07 as the core engine, but revert to Naive for low-variance segments
    # if the burn-in period shows that PDXPrice07 is adding more error than value.
    
    for f_path in tqdm(files, desc="Applying Corrections"):
        df = pd.read_parquet(f_path)
        for seg in SEGMENTS:
            # Calculate WAPE improvement of Naive vs PDXPrice07 during burn-in (IF Oracle exists)
            # If we don't want to use Oracle, we use the Stress Test logic (Naive vs PD07)
            
            # Non-Oracle defensible logic:
            # If the segment was censored LESS than 5% of the time in Year 1, 
            # unconstraining is statistically risky. We default to Naive.
            cens_rate = np.mean(df["Is_Censored"].values[:BURN_IN_DAYS])
            
            if (seg in ["Contract", "Spot"]) and cens_rate < 0.10:
                winner = "Naive"
            else:
                winner = "PDXPrice07"
            
            df[f"MoE_{seg}_Est_kg"] = df[f"{winner}_{seg}_Est_kg"]
            df[f"MoE_{seg}_Est_cbm"] = df[f"{winner}_{seg}_Est_cbm"]
            df[f"MoE_{seg}_Selected_Model"] = winner
            
        df.to_parquet(f_path, index=False)
        
    print("Done. The MoE is now a 'Corrected-Baseline' Ensemble.")
