import numpy as np
import pandas as pd
import json
from collections import defaultdict

class ResidualDataManager:
    def __init__(self, harvested_json_path):
        with open(harvested_json_path, 'r') as f:
            raw_list = json.load(f)
        
        self.data = defaultdict(lambda: defaultdict(dict))
        self.seq_to_segment = {}
        all_seqs = set()
        self.segments = set()
        
        for record in raw_list:
            fid = record["Flight_ID"]
            model = record["Model"]
            horizon = str(record["Horizon"])
            seg = record.get("Segment", "Unknown")
            
            self.seq_to_segment[fid] = seg
            self.segments.add(seg)
            
            if horizon not in self.data[fid][model]:
                self.data[fid][model][horizon] = {"forecasts": [], "actuals": [], "dates": []}
            
            preds = record.get("Predictions", record.get("forecasts", []))
            actuals = record.get("Actuals", record.get("actuals", []))
            dates = record.get("Dates", record.get("dates", []))
            
            self.data[fid][model][horizon]["forecasts"].extend(preds)
            self.data[fid][model][horizon]["actuals"].extend(actuals)
            self.data[fid][model][horizon]["dates"].extend(dates)
            all_seqs.add(fid)
            
        self.all_sequences = sorted(list(all_seqs))
        self.sorted_segments = sorted(list(self.segments))
        print(f"Registry built: {len(self.all_sequences)} flights, {len(self.sorted_segments)} segments.")

    def get_matrices(self, model_name, horizon):
        horizon = str(horizon)
        all_dates = set()
        for seq in self.all_sequences:
            if model_name in self.data[seq] and horizon in self.data[seq][model_name]:
                all_dates.update(self.data[seq][model_name][horizon]["dates"])
        
        sorted_dates = sorted(list(all_dates))
        date_to_row = {date: i for i, date in enumerate(sorted_dates)}
        
        X = np.zeros((len(sorted_dates), len(self.all_sequences)))
        Y = np.zeros((len(sorted_dates), len(self.all_sequences)))
        M = np.zeros((len(sorted_dates), len(self.all_sequences)))
        
        for seq_idx, seq in enumerate(self.all_sequences):
            if model_name not in self.data[seq] or horizon not in self.data[seq][model_name]: continue
            d = self.data[seq][model_name][horizon]
            
            f_vals = np.array(d["forecasts"])
            a_vals = np.array(d["actuals"])

            # --- LEAK-FREE CLIPPING ---
            # We use a hard-cap heuristic (e.g. 500 tons for a cargo flight) 
            # or a very high fixed value to only catch the SARIMA 'infinity' errors.
            # This is safer than using np.percentile on the whole series.
            f_vals = np.clip(f_vals, 0, 1000000) # 1000 tons is a safe upper bound for any single flight sequence

            for i, date in enumerate(d["dates"]):
                if date in date_to_row:
                    r = date_to_row[date]
                    X[r, seq_idx] = f_vals[i]
                    Y[r, seq_idx] = a_vals[i]
                    M[r, seq_idx] = 1.0

        # Feature Engineering: DOW and Market Aggregates
        df_dates = pd.to_datetime(sorted_dates)
        dow = pd.get_dummies(df_dates.dayofweek).values
        if dow.shape[1] < 7:
            temp = np.zeros((len(sorted_dates), 7))
            temp[:, :dow.shape[1]] = dow
            dow = temp

        net_total = X.sum(axis=1, keepdims=True)
        seg_totals = np.zeros((len(sorted_dates), len(self.sorted_segments)))
        for i, seg in enumerate(self.sorted_segments):
            seg_indices = [idx for idx, s in enumerate(self.all_sequences) if self.seq_to_segment[s] == seg]
            seg_totals[:, i] = X[:, seg_indices].sum(axis=1)

        extras = np.hstack([dow, net_total, seg_totals])
        return X, Y, M, extras, sorted_dates
