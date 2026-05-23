import numpy as np
import pandas as pd
import json
from collections import defaultdict

class ResidualDataManager:
    def __init__(self, harvested_json_path):
        with open(harvested_json_path, 'r') as f:
            raw_list = json.load(f)
        
        # --- FIX: Group the flat list into nested dict ---
        # Structure: self.data[flight_id][model][horizon] = record
        self.data = defaultdict(lambda: defaultdict(dict))
        all_seqs = set()
        
        for record in raw_list:
            fid = record["Flight_ID"]
            model = record["Model"]
            horizon = str(record["Horizon"])
            
            # Save the latest fold or combine dates? 
            # In our experiment, each record is one fold's out-of-sample window.
            # We store them in a way that get_matrices can concatenate them by date.
            if horizon not in self.data[fid][model]:
                self.data[fid][model][horizon] = {
                    "forecasts": [],
                    "actuals": [],
                    "dates": []
                }
            
            # Use 'Predictions' key if 'forecasts' is missing (handle naming mismatch)
            preds = record.get("Predictions", record.get("forecasts", []))
            actuals = record.get("Actuals", record.get("actuals", []))
            dates = record.get("Dates", record.get("dates", []))
            
            self.data[fid][model][horizon]["forecasts"].extend(preds)
            self.data[fid][model][horizon]["actuals"].extend(actuals)
            self.data[fid][model][horizon]["dates"].extend(dates)
            all_seqs.add(fid)
            
        self.all_sequences = sorted(list(all_seqs))
        self.seq_to_idx = {seq: i for i, seq in enumerate(self.all_sequences)}
        print(f"Registry built with {len(self.all_sequences)} flight sequences from flat JSON.")

    def get_matrices(self, model_name, horizon):
        """
        Returns:
            X: Forecasts matrix (Dates, N_flights)
            Y: Actuals matrix (Dates, N_flights)
            M: Presence Mask (Dates, N_flights)
        """
        horizon = str(horizon)
        all_dates = set()
        for seq in self.all_sequences:
            if model_name in self.data[seq] and horizon in self.data[seq][model_name]:
                all_dates.update(self.data[seq][model_name][horizon]["dates"])
        
        sorted_dates = sorted(list(all_dates))
        date_to_row = {date: i for i, date in enumerate(sorted_dates)}
        
        num_rows = len(sorted_dates)
        num_cols = len(self.all_sequences)
        
        X = np.zeros((num_rows, num_cols))
        Y = np.zeros((num_rows, num_cols))
        M = np.zeros((num_rows, num_cols))
        
        for seq_idx, seq in enumerate(self.all_sequences):
            if model_name not in self.data[seq] or horizon not in self.data[seq][model_name]:
                continue
            
            d = self.data[seq][model_name][horizon]
            forecasts = d["forecasts"]
            actuals = d["actuals"]
            dates = d["dates"]
            
            # --- THESIS RESCUE: OUTLIER CLIPPING ---
            if len(actuals) > 0:
                # Clip extreme SARIMA errors
                max_cap = np.percentile(actuals, 99) * 5 
                if max_cap == 0: max_cap = 250000 
                forecasts = np.clip(forecasts, 0, max_cap)
            
            for i, date in enumerate(dates):
                if date in date_to_row:
                    row_idx = date_to_row[date]
                    X[row_idx, seq_idx] = forecasts[i]
                    Y[row_idx, seq_idx] = actuals[i]
                    M[row_idx, seq_idx] = 1.0

        return X, Y, M, sorted_dates
