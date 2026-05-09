import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

# your models
from models import NaiveUnconstrainer, EMUnconstrainer, MARSSEMUnconstrainer, EMPriceUnconstrainer, MARSSXPriceUnconstrainer

DATA_PATH = "../data/air_cargo_10yr_dataset.csv"
SAVE_DIR = "./unconstrained_results"
LOOKBACK = 365

os.makedirs(SAVE_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)
df["Date"] = pd.to_datetime(df["Date"])

def process_od_pair(args):
    origin, dest = args

    file_name = f"{origin}_{dest}.parquet"
    save_path = os.path.join(SAVE_DIR, file_name)

    # Skip if already done
    if os.path.exists(save_path):
        return f"Skipped {origin}->{dest}"

    sample_df = df[
        (df["Origin"] == origin) &
        (df["Destination"] == dest)
    ].copy()

    sample_df = sample_df.sort_values("Date").reset_index(drop=True)

    if len(sample_df) <= LOOKBACK:
        return f"Too short {origin}->{dest}"

    sample_df["Fuzzy_Capacity"] = np.where(
        sample_df["Is_Censored"],
        sample_df["Final_Constrained_Bookings"],
        100000
    )

    sample_df['Naive_Est'] = np.nan
    sample_df['EM_Est'] = np.nan
    sample_df['MARSS_Est'] = np.nan
    sample_df['EMXPrice_Est'] = np.nan
    sample_df['MARSSXPrice_Est'] = np.nan

    obs_arr = sample_df["Final_Constrained_Bookings"].values
    cens_arr = sample_df["Is_Censored"].values
    cap_arr = sample_df["Fuzzy_Capacity"].values

    models = {
        'Naive': (NaiveUnconstrainer(), 'Naive_Est'),
        'EM': (EMUnconstrainer(), 'EM_Est'),
        'MARSS': (MARSSEMUnconstrainer(), 'MARSS_Est'),
        'EM-X Price': (EMPriceUnconstrainer(), 'EMXPrice_Est'),
        'MARSS-X Price': (MARSSXPriceUnconstrainer(), 'MARSSXPrice_Est')
    }

    # Convert columns to numpy arrays for faster slicing
    # FIX: Extract Price_Index from sample_df, NOT the global df
    obs_arr = sample_df['Final_Constrained_Bookings'].values
    cens_arr = sample_df['Is_Censored'].values
    cap_arr = sample_df['Fuzzy_Capacity'].values
    price_arr = sample_df['Final_Price_per_kg'].values 

    for t in range(LOOKBACK, len(sample_df)):
            
        # SLICE THE PAST + TODAY
        win_start = t - LOOKBACK + 1
        win_end = t + 1
        
        win_obs = obs_arr[win_start:win_end]
        win_cens = cens_arr[win_start:win_end]
        win_cap = cap_arr[win_start:win_end]
        win_price = price_arr[win_start:win_end] 
        
        # Run each model on the isolated window
        for name, (model, col_name) in models.items():
            # If today is NOT censored, latent demand is simply the observed bookings.
            if not win_cens[-1]:
                sample_df.loc[t, col_name] = win_obs[-1]
                continue
                
            # FIX: Conditionally pass the price_index argument only to models that need it
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
            
            # Save the very last value in the array (Today's estimate)
            sample_df.loc[t, col_name] = imputed_window[-1]

    sample_df.to_parquet(save_path, index=False)

    return f"Done {origin}->{dest}"

od_pairs = df[["Origin", "Destination"]].drop_duplicates()
tasks = list(od_pairs.itertuples(index=False, name=None))

if __name__ == "__main__":

    workers = os.cpu_count() - 1

    with ProcessPoolExecutor(max_workers=workers) as executor:

        futures = [
            executor.submit(process_od_pair, task)
            for task in tasks
        ]

        for f in tqdm(as_completed(futures), total=len(futures)):
            print(f.result())