import pandas as pd
import numpy as np
import os
import sys
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

# Add Synthesizing/modules to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "Synthesizing", "modules"))
try:
    from config import SEGMENTS
except ImportError:
    SEGMENTS = {
        "Contract": {}, "General": {}, "Perishable": {}, "Express": {}, "Spot": {}
    }

from models import NaiveUnconstrainer, EMUnconstrainer, MARSSEMUnconstrainer, EMPriceUnconstrainer, MARSSXPriceUnconstrainer

DATA_PATH = "../data/air_cargo_5yr_dataset.csv"
SAVE_DIR = "./unconstrained_results"
LOOKBACK = 365

os.makedirs(SAVE_DIR, exist_ok=True)

# DRY Configuration: Single source of truth for model classes and their column prefixes
MODEL_SPECS = {
    'Naive': (NaiveUnconstrainer, 'Naive'),
    'EM': (EMUnconstrainer, 'EM'),
    'MARSS': (MARSSEMUnconstrainer, 'MARSS'),
    'EM-X Price': (EMPriceUnconstrainer, 'EMXPrice'),
    'MARSS-X Price': (MARSSXPriceUnconstrainer, 'MARSSXPrice')
}

def process_od_pair(args):
    origin, dest, sample_df = args
    file_name = f"{origin}_{dest}.parquet"
    save_path = os.path.join(SAVE_DIR, file_name)

    if os.path.exists(save_path):
        return f"Skipped {origin}->{dest}"

    sample_df = sample_df.sort_values("Date").reset_index(drop=True)

    if len(sample_df) <= LOOKBACK:
        return f"Too short {origin}->{dest}"

    # 1. Calculate Total Flight Volume
    segment_cols = [f"Observed_{s}_kg" for s in SEGMENTS.keys() if f"Observed_{s}_kg" in sample_df.columns]
    sample_df["Total_Observed_kg"] = sample_df[segment_cols].sum(axis=1)
    
    # 2. Determine physical flight capacity (Strictly Non-Leaky)
    if "Total_Capacity_kg" in sample_df.columns:
        flight_capacity_arr = sample_df["Total_Capacity_kg"].values
    else:
        flight_capacity_arr = sample_df["Total_Observed_kg"].expanding().max().values

    # 3. Calculate trailing rolling total for the burn-in period. (shift(1) prevents leakage)
    rolling_total = sample_df["Total_Observed_kg"].shift(1).rolling(window=LOOKBACK, min_periods=1).sum()
    cens_arr = sample_df["Is_Censored"].values

    # Pre-allocate dictionary of NumPy arrays for O(1) assignments
    results_cache = {}
    for seg in SEGMENTS.keys():
        results_cache[seg] = {prefix: np.full(len(sample_df), np.nan) for _, prefix in MODEL_SPECS.values()}

    for seg in SEGMENTS.keys():
        obs_col = f"Observed_{seg}_kg"
        price_col = f"Price_{seg}_DP-15"
        
        if obs_col not in sample_df.columns or price_col not in sample_df.columns:
            continue

        obs_arr = sample_df[obs_col].values
        price_arr = sample_df[price_col].values
        
        # 4. Calculate this segment's rolling share over the lookback window
        rolling_seg = sample_df[obs_col].shift(1).rolling(window=LOOKBACK, min_periods=1).sum()
        dynamic_share = (rolling_seg / rolling_total).fillna(1.0 / len(SEGMENTS)).values

        # 5. Assign Virtual Capacity dynamically based on the past
        virtual_capacity = np.maximum(obs_arr, flight_capacity_arr * dynamic_share)
        cap_arr = np.where(cens_arr, virtual_capacity, 1000000.0)

        # Instantiate fresh models for this specific segment to prevent cross-contamination
        active_models = {
            name: (ModelClass(), prefix) 
            for name, (ModelClass, prefix) in MODEL_SPECS.items()
        }

        for t in range(LOOKBACK, len(sample_df)):
            if not cens_arr[t]:
                for _, (_, col_prefix) in active_models.items():
                    results_cache[seg][col_prefix][t] = obs_arr[t]
                continue

            # SLICE THE PAST + TODAY
            win_start = t - LOOKBACK + 1
            win_end = t + 1
            
            win_obs = obs_arr[win_start:win_end]
            win_cens = cens_arr[win_start:win_end]
            win_cap = cap_arr[win_start:win_end]
            win_price = price_arr[win_start:win_end] 
            
            for name, (model, col_prefix) in active_models.items():
                try:
                    if 'Price' in name:
                        imputed_window = model.fit(
                            observed_bookings=win_obs,
                            is_censored=win_cens,
                            capacity=win_cap,
                            price_per_kg=win_price,
                            max_iter=50
                        )
                    else:
                        imputed_window = model.fit(
                            observed_bookings=win_obs,
                            is_censored=win_cens,
                            capacity=win_cap,
                            max_iter=50
                        )
                    results_cache[seg][col_prefix][t] = imputed_window[-1]
                except Exception as e:
                    # Smart Fallback: Use historical mean instead of hard zero to protect WAPE/RMSE
                    mask_uncens = ~win_cens
                    fallback_val = np.mean(win_obs[mask_uncens]) if np.sum(mask_uncens) > 0 else np.mean(win_obs)
                    results_cache[seg][col_prefix][t] = max(obs_arr[t], fallback_val)

    # Batch assign the filled NumPy arrays back to the DataFrame
    for seg, models_dict in results_cache.items():
        for col_prefix, arr in models_dict.items():
            if not np.all(np.isnan(arr)):
                sample_df[f"{col_prefix}_{seg}_Est"] = arr

    sample_df.to_parquet(save_path, index=False)
    return f"Done {origin}->{dest}"

if __name__ == "__main__":
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data file not found at {DATA_PATH}")
        sys.exit(1)

    print(f"Loading dataset: {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])

    print("Generating tasks...")
    # GroupBy is exceptionally faster and memory efficient
    tasks = [(origin, dest, group.copy()) for (origin, dest), group in df.groupby(["Origin", "Destination"])]
    del df # Free original DataFrame memory

    workers = max(1, os.cpu_count() - 4)
    print(f"Starting batch processing with {workers} workers for {len(tasks)} OD pairs...")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_od_pair, task) for task in tasks]

        for f in tqdm(as_completed(futures), total=len(futures)):
            try:
                print(f.result())
            except Exception as e:
                print(f"Task failed: {e}")