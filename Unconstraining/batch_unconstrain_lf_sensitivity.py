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

LOOKBACK = 365

# MODEL Configuration
MODEL_SPECS = {
    'Naive': (NaiveUnconstrainer, 'Naive', {}),
    'EM': (EMUnconstrainer, 'EM', {}),
    'EM-X Price': (EMPriceUnconstrainer, 'EMXPrice', {})
}

for tau in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    tau_str = str(tau).replace('.', '')
    MODEL_SPECS[f'PD_{tau}'] = (PDUnconstrainer, f'PD{tau_str}', {'tau': tau})
    MODEL_SPECS[f'PD-X Price_{tau}'] = (PDPriceUnconstrainer, f'PDXPrice{tau_str}', {'tau': tau})

def process_od_pair(args):
    origin, dest, flight_seq, sample_df, save_dir = args
    file_name = f"{origin}_{dest}_FS{flight_seq}.parquet"
    save_path = os.path.join(save_dir, file_name)

    if os.path.exists(save_path):
        return f"Skipped {origin}->{dest}"

    sample_df = sample_df.sort_values("Date").reset_index(drop=True)
    if len(sample_df) <= LOOKBACK: return f"Too short {origin}->{dest}"

    # 1. Calculate Totals
    kg_cols = [f"Observed_{s}_kg" for s in SEGMENTS.keys()]
    cbm_cols = [f"Observed_{s}_cbm" for s in SEGMENTS.keys()]
    sample_df["Total_Observed_kg"] = sample_df[kg_cols].sum(axis=1)
    sample_df["Total_Observed_cbm"] = sample_df[cbm_cols].sum(axis=1)
    
    cap_kg_arr = np.full(len(sample_df), AIRCRAFT_CAPACITY_KG)
    cap_cbm_arr = np.full(len(sample_df), AIRCRAFT_CAPACITY_CBM)

    rolling_total_kg = sample_df["Total_Observed_kg"].shift(1).rolling(window=LOOKBACK, min_periods=1).sum()
    rolling_total_cbm = sample_df["Total_Observed_cbm"].shift(1).rolling(window=LOOKBACK, min_periods=1).sum()
    
    cens_arr = sample_df["Is_Censored"].values
    cens_by_arr = sample_df["Censored_By"].values

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
        
        rolling_seg_kg = sample_df[f"Observed_{seg}_kg"].shift(1).rolling(window=LOOKBACK, min_periods=1).sum()
        rolling_seg_cbm = sample_df[f"Observed_{seg}_cbm"].shift(1).rolling(window=LOOKBACK, min_periods=1).sum()
        
        share_kg = (rolling_seg_kg / rolling_total_kg).fillna(1.0 / len(SEGMENTS)).values
        share_cbm = (rolling_seg_cbm / rolling_total_cbm).fillna(1.0 / len(SEGMENTS)).values

        virt_cap_kg = np.maximum(obs_kg, cap_kg_arr * share_kg)
        virt_cap_cbm = np.maximum(obs_cbm, cap_cbm_arr * share_cbm)
        
        model_cap_kg = np.where(cens_arr, virt_cap_kg, 1e9)
        model_cap_cbm = np.where(cens_arr, virt_cap_cbm, 1e9)

        models_kg = {name: (ModelClass(), prefix, kwargs) for name, (ModelClass, prefix, kwargs) in MODEL_SPECS.items()}
        models_cbm = {name: (ModelClass(), prefix, kwargs) for name, (ModelClass, prefix, kwargs) in MODEL_SPECS.items()}

        for t in range(LOOKBACK, len(sample_df)):
            if not cens_arr[t]:
                for _, (_, prefix, _) in models_kg.items():
                    results_cache[seg][prefix]['KG'][t] = obs_kg[t]
                    results_cache[seg][prefix]['CBM'][t] = obs_cbm[t]
                continue

            w_start, w_end = t - LOOKBACK + 1, t + 1
            win_cens = cens_arr[w_start:w_end]
            win_price = price_arr[w_start:w_end]
            win_obs_kg = obs_kg[w_start:w_end]
            win_cap_kg = model_cap_kg[w_start:w_end]
            win_obs_cbm = obs_cbm[w_start:w_end]
            win_cap_cbm = model_cap_cbm[w_start:w_end]
            
            for name in MODEL_SPECS.keys():
                _, prefix, model_kwargs = MODEL_SPECS[name]
                m_kg, _, _ = models_kg[name]
                m_cbm, _, _ = models_cbm[name]
                try:
                    if cens_by_arr[t] == "Volume":
                        fk_cbm = {'observed_bookings': win_obs_cbm, 'is_censored': win_cens, 'capacity': win_cap_cbm, 'max_iter': 50}
                        fk_cbm.update(model_kwargs)
                        if 'Price' in name: fk_cbm['price_per_kg'] = win_price
                        est_cbm = m_cbm.fit(**fk_cbm)[-1]
                        est_kg = est_cbm * density
                    else:
                        fk_kg = {'observed_bookings': win_obs_kg, 'is_censored': win_cens, 'capacity': win_cap_kg, 'max_iter': 50}
                        fk_kg.update(model_kwargs)
                        if 'Price' in name: fk_kg['price_per_kg'] = win_price
                        est_kg = m_kg.fit(**fk_kg)[-1]
                        est_cbm = est_kg / density
                    results_cache[seg][prefix]['KG'][t] = est_kg
                    results_cache[seg][prefix]['CBM'][t] = est_cbm
                except Exception:
                    results_cache[seg][prefix]['KG'][t] = obs_kg[t]
                    results_cache[seg][prefix]['CBM'][t] = obs_cbm[t]

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
    VAR_DIR = "data/varied_lf_datasets"
    BASE_SAVE_DIR = "Unconstraining/lf_results"
    
    files = [f for f in os.listdir(VAR_DIR) if f.endswith(".csv")]
    print(f"Found {len(files)} LF datasets to process.")

    for csv_file in files:
        # Extract LF from filename, e.g., air_cargo_5yr_LF_90.csv -> 90
        lf_str = csv_file.split("_LF_")[-1].replace(".csv", "")
        save_dir = os.path.join(BASE_SAVE_DIR, f"LF_{lf_str}")
        os.makedirs(save_dir, exist_ok=True)
        
        data_path = os.path.join(VAR_DIR, csv_file)
        print(f"\n>>> Processing {csv_file} (Saving to {save_dir})")
        
        df = pd.read_csv(data_path)
        df["Date"] = pd.to_datetime(df["Date"])
        
        tasks = [
            (o, d, fs, g.copy(), save_dir) 
            for (o, d, fs), g in df.groupby(["Origin", "Destination", "Flight_Sequence"])
        ]
        del df

        workers = max(1, os.cpu_count() - 2)
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(process_od_pair, task) for task in tasks]
            for f in tqdm(as_completed(futures), total=len(futures), desc=f"LF {lf_str}"):
                pass
    
    print("\nAll Sensitivity Unconstraining Complete!")
