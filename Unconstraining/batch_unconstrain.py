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
    # Fallback if the path logic above fails in some environments
    SEGMENTS = {
        "Contract": {}, "General": {}, "Perishable": {}, "Express": {}, "Spot": {}
    }

# your models
from models import NaiveUnconstrainer, EMUnconstrainer, MARSSEMUnconstrainer, EMPriceUnconstrainer, MARSSXPriceUnconstrainer

DATA_PATH = "../data/air_cargo_10yr_dataset.csv"
SAVE_DIR = "./unconstrained_results"
LOOKBACK = 365

os.makedirs(SAVE_DIR, exist_ok=True)

# Check if data exists
if not os.path.exists(DATA_PATH):
    print(f"Error: Data file not found at {DATA_PATH}")
    sys.exit(1)

def process_od_pair(args):
    # args now contains (origin, dest, sample_df)
    origin, dest, sample_df = args

    file_name = f"{origin}_{dest}.parquet"
    save_path = os.path.join(SAVE_DIR, file_name)

    # Skip if already done
    if os.path.exists(save_path):
        return f"Skipped {origin}->{dest}"

    sample_df = sample_df.sort_values("Date").reset_index(drop=True)

    if len(sample_df) <= LOOKBACK:
        return f"Too short {origin}->{dest}"

    # Initialize columns for each model and each segment
    model_configs = {
        'Naive': (NaiveUnconstrainer(), 'Naive'),
        'EM': (EMUnconstrainer(), 'EM'),
        'MARSS': (MARSSEMUnconstrainer(), 'MARSS'),
        'EM-X Price': (EMPriceUnconstrainer(), 'EMXPrice'),
        'MARSS-X Price': (MARSSXPriceUnconstrainer(), 'MARSSXPrice')
    }

    # Initialize columns for each model and each segment
    for seg in SEGMENTS.keys():
        for _, (model, col_prefix) in model_configs.items():
            sample_df[f"{col_prefix}_{seg}_Est"] = np.nan

    cens_arr = sample_df["Is_Censored"].values

    for seg in SEGMENTS.keys():
        obs_col = f"Observed_{seg}_kg"
        price_col = f"Price_{seg}_DP15"
        
        if obs_col not in sample_df.columns or price_col not in sample_df.columns:
            continue

        obs_arr = sample_df[obs_col].values
        # User choice: Opening Price at DP 15
        price_arr = sample_df[price_col].values
        
        # User choice: Observed Bookings (Strict) as capacity when censored
        cap_arr = np.where(
            cens_arr,
            obs_arr,
            1000000.0 # Very large number for uncensored
        )

        for t in range(LOOKBACK, len(sample_df)):
            # If not censored, all models simply return the observed bookings
            if not cens_arr[t]:
                for _, (model, col_prefix) in model_configs.items():
                    sample_df.loc[t, f"{col_prefix}_{seg}_Est"] = obs_arr[t]
                continue

            # SLICE THE PAST + TODAY
            win_start = t - LOOKBACK + 1
            win_end = t + 1
            
            win_obs = obs_arr[win_start:win_end]
            win_cens = cens_arr[win_start:win_end]
            win_cap = cap_arr[win_start:win_end]
            win_price = price_arr[win_start:win_end] 
            
            for name, (model, col_prefix) in model_configs.items():
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
                    sample_df.loc[t, f"{col_prefix}_{seg}_Est"] = imputed_window[-1]
                except Exception as e:
                    # Robustness: fallback to observed if model fails
                    sample_df.loc[t, f"{col_prefix}_{seg}_Est"] = obs_arr[t]

    sample_df.to_parquet(save_path, index=False)

    return f"Done {origin}->{dest}"

if __name__ == "__main__":
    # Load data ONCE in the main process
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data file not found at {DATA_PATH}")
        sys.exit(1)

    print(f"Loading dataset: {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])

    od_pairs = df[["Origin", "Destination"]].drop_duplicates()
    
    # Prepare tasks by slicing the dataframe for each OD pair
    tasks = []
    for row in od_pairs.itertuples(index=False):
        origin, dest = row
        sample_df = df[(df["Origin"] == origin) & (df["Destination"] == dest)].copy()
        tasks.append((origin, dest, sample_df))

    # Free up the original large dataframe memory
    del df

    workers = max(1, os.cpu_count() - 1)
    print(f"Starting batch processing with {workers} workers for {len(tasks)} OD pairs...")

    with ProcessPoolExecutor(max_workers=workers) as executor:

        futures = [
            executor.submit(process_od_pair, task)
            for task in tasks
        ]

        for f in tqdm(as_completed(futures), total=len(futures)):
            try:
                print(f.result())
            except Exception as e:
                print(f"Task failed: {e}")
