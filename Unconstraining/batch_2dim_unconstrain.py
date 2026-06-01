import pandas as pd
import numpy as np
import os
import sys
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

# Add Synthesizing/modules to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "Synthesizing", "modules"))
try:
    from config import SEGMENTS, AIRCRAFT_CAPACITY_KG, AIRCRAFT_CAPACITY_CBM
except ImportError:
    SEGMENTS = {
        "Contract": {"density": 180}, 
        "General": {"density": 167}, 
        "Perishable": {"density": 140}, 
        "Express": {"density": 120}, 
        "Spot": {"density": 167}
    }
    AIRCRAFT_CAPACITY_KG = 100000
    AIRCRAFT_CAPACITY_CBM = 600

# Import all unconstrainer models
from models import (
    NaiveUnconstrainer, 
    EMUnconstrainer, 
    EMPriceUnconstrainer, 
    PDUnconstrainer, 
    PDPriceUnconstrainer
)

DATA_PATH = "data/air_cargo_5yr_volumetric_dataset.csv"
SAVE_DIR = "Unconstraining/unconstrained_2dim_results"
LOOKBACK = 365

os.makedirs(SAVE_DIR, exist_ok=True)

# MODEL Configuration
MODEL_SPECS = {
    'Naive': (NaiveUnconstrainer, 'Naive', {}),
    'EM': (EMUnconstrainer, 'EM', {}),
    'EM-X Price': (EMPriceUnconstrainer, 'EMXPrice', {})
}

# Dynamically add PD and PD-Price models for each tau
for tau in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    tau_str = str(tau).replace('.', '')
    MODEL_SPECS[f'PD_{tau}'] = (PDUnconstrainer, f'PD{tau_str}', {'tau': tau})
    MODEL_SPECS[f'PD-X Price_{tau}'] = (PDPriceUnconstrainer, f'PDXPrice{tau_str}', {'tau': tau})


def process_od_pair(args):
    origin, dest, flight_seq, sample_df = args
    file_name = f"{origin}_{dest}_FS{flight_seq}.parquet"
    save_path = os.path.join(SAVE_DIR, file_name)

    if os.path.exists(save_path):
        return f"Skipped {origin}->{dest} (FS:{flight_seq})"

    sample_df = sample_df.sort_values("Date").reset_index(drop=True)

    if len(sample_df) <= LOOKBACK:
        return f"Too short {origin}->{dest}"

    # 1. Calculate Totals
    kg_cols = [f"Observed_{s}_kg" for s in SEGMENTS.keys()]
    cbm_cols = [f"Observed_{s}_cbm" for s in SEGMENTS.keys()]
    sample_df["Total_Observed_kg"] = sample_df[kg_cols].sum(axis=1)
    sample_df["Total_Observed_cbm"] = sample_df[cbm_cols].sum(axis=1)
    
    # 2. Heuristic for Capacity (if not provided)
    # Note: In the new dataset, we know AIRCRAFT_CAPACITY_KG and AIRCRAFT_CAPACITY_CBM from config
    cap_kg_arr = np.full(len(sample_df), AIRCRAFT_CAPACITY_KG)
    cap_cbm_arr = np.full(len(sample_df), AIRCRAFT_CAPACITY_CBM)

    # 3. Rolling totals for shares
    rolling_total_kg = sample_df["Total_Observed_kg"].shift(1).rolling(window=LOOKBACK, min_periods=1).sum()
    rolling_total_cbm = sample_df["Total_Observed_cbm"].shift(1).rolling(window=LOOKBACK, min_periods=1).sum()
    
    cens_arr = sample_df["Is_Censored"].values
    cens_by_arr = sample_df["Censored_By"].values

    # Results cache: seg -> model_prefix -> {KG: arr, CBM: arr}
    results_cache = {}
    for seg in SEGMENTS.keys():
        results_cache[seg] = {}
        for _, prefix, _ in MODEL_SPECS.values():
            results_cache[seg][prefix] = {
                'KG': np.full(len(sample_df), np.nan),
                'CBM': np.full(len(sample_df), np.nan)
            }

    for seg in SEGMENTS.keys():
        obs_kg = sample_df[f"Observed_{seg}_kg"].values
        obs_cbm = sample_df[f"Observed_{seg}_cbm"].values
        price_arr = sample_df[f"Price_{seg}_DP-15"].values
        density = SEGMENTS[seg]['density']
        
        # Calculate dynamic shares
        rolling_seg_kg = sample_df[f"Observed_{seg}_kg"].shift(1).rolling(window=LOOKBACK, min_periods=1).sum()
        rolling_seg_cbm = sample_df[f"Observed_{seg}_cbm"].shift(1).rolling(window=LOOKBACK, min_periods=1).sum()
        
        share_kg = (rolling_seg_kg / rolling_total_kg).fillna(1.0 / len(SEGMENTS)).values
        share_cbm = (rolling_seg_cbm / rolling_total_cbm).fillna(1.0 / len(SEGMENTS)).values

        # Virtual Capacities
        virt_cap_kg = np.maximum(obs_kg, cap_kg_arr * share_kg)
        virt_cap_cbm = np.maximum(obs_cbm, cap_cbm_arr * share_cbm)
        
        # Effective cap arrays for models (only used when Is_Censored is True)
        model_cap_kg = np.where(cens_arr, virt_cap_kg, 1e9)
        model_cap_cbm = np.where(cens_arr, virt_cap_cbm, 1e9)

        # Active models
        models_kg = {name: (ModelClass(), prefix, kwargs) for name, (ModelClass, prefix, kwargs) in MODEL_SPECS.items()}
        models_cbm = {name: (ModelClass(), prefix, kwargs) for name, (ModelClass, prefix, kwargs) in MODEL_SPECS.items()}

        for t in range(LOOKBACK, len(sample_df)):
            if not cens_arr[t]:
                for _, (_, prefix, _) in models_kg.items():
                    results_cache[seg][prefix]['KG'][t] = obs_kg[t]
                    results_cache[seg][prefix]['CBM'][t] = obs_cbm[t]
                continue

            # Rolling window boundaries
            w_start, w_end = t - LOOKBACK + 1, t + 1
            
            # Common inputs
            win_cens = cens_arr[w_start:w_end]
            win_price = price_arr[w_start:w_end]

            # Fit KG models
            win_obs_kg = obs_kg[w_start:w_end]
            win_cap_kg = model_cap_kg[w_start:w_end]
            
            # Fit CBM models
            win_obs_cbm = obs_cbm[w_start:w_end]
            win_cap_cbm = model_cap_cbm[w_start:w_end]
            
            for name in MODEL_SPECS.keys():
                _, prefix, model_kwargs = MODEL_SPECS[name]
                m_kg, _, _ = models_kg[name]
                m_cbm, _, _ = models_cbm[name]
                
                try:
                    # Decide which dimension to unconstrain based on "Censored_By"
                    # User: "unconstrain the variable that is constrained and then uplift"
                    if cens_by_arr[t] == "Volume":
                        # Unconstrain CBM
                        fk_cbm = {'observed_bookings': win_obs_cbm, 'is_censored': win_cens, 'capacity': win_cap_cbm, 'max_iter': 50}
                        fk_cbm.update(model_kwargs)
                        if 'Price' in name: fk_cbm['price_per_kg'] = win_price # Note: Price is still per KG, used as feature
                        
                        est_cbm = m_cbm.fit(**fk_cbm)[-1]
                        est_kg = est_cbm * density
                    else:
                        # Unconstrain Weight (Default if "Weight" or None but censored)
                        fk_kg = {'observed_bookings': win_obs_kg, 'is_censored': win_cens, 'capacity': win_cap_kg, 'max_iter': 50}
                        fk_kg.update(model_kwargs)
                        if 'Price' in name: fk_kg['price_per_kg'] = win_price
                        
                        est_kg = m_kg.fit(**fk_kg)[-1]
                        est_cbm = est_kg / density
                        
                    results_cache[seg][prefix]['KG'][t] = est_kg
                    results_cache[seg][prefix]['CBM'][t] = est_cbm
                    
                except Exception as e:
                    # Fallback
                    results_cache[seg][prefix]['KG'][t] = obs_kg[t]
                    results_cache[seg][prefix]['CBM'][t] = obs_cbm[t]

    # Assemble results
    new_columns = {}
    for seg, models_dict in results_cache.items():
        for prefix, dims in models_dict.items():
            if not np.all(np.isnan(dims['KG'])):
                new_columns[f"{prefix}_{seg}_Est_kg"] = dims['KG']
                new_columns[f"{prefix}_{seg}_Est_cbm"] = dims['CBM']
    
    if new_columns:
        new_cols_df = pd.DataFrame(new_columns, index=sample_df.index)
        sample_df = pd.concat([sample_df, new_cols_df], axis=1)

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
    tasks = [
        (origin, dest, flight_seq, group.copy()) 
        for (origin, dest, flight_seq), group in df.groupby(["Origin", "Destination", "Flight_Sequence"])
    ]
    del df

    workers = max(1, os.cpu_count() - 4)
    print(f"Starting 2-Dim batch processing with {workers} workers for {len(tasks)} series...")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_od_pair, task) for task in tasks]
        for f in tqdm(as_completed(futures), total=len(futures)):
            try:
                pass # print(f.result())
            except Exception as e:
                print(f"Task failed: {e}")
