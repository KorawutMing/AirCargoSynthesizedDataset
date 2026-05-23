import numpy as np
import pandas as pd
import json
from collections import defaultdict

class ResidualDataManager:
    def __init__(self, harvested_json_path):
        with open(harvested_json_path, 'r') as f:
            raw_list = json.load(f)
        
        self.data = defaultdict(lambda: defaultdict(dict))
        all_seqs = set()
        
        for record in raw_list:
            fid = record["Flight_ID"]
            model = record["Model"]
            horizon = str(record["Horizon"])
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
        self.origins = sorted(list(set(f.split('_')[0] for f in self.all_sequences)))
        self.destinations = sorted(list(set(f.split('_')[1] for f in self.all_sequences)))
        self.orig_to_idx = {o: i for i, o in enumerate(self.origins)}
        self.dest_to_idx = {d: i for i, d in enumerate(self.destinations)}
        self.max_fs = max(int(f.split('FS')[1]) for f in self.all_sequences)

    def get_matrices(self, model_name, horizon):
        horizon = str(horizon)
        all_dates = set()
        for seq in self.all_sequences:
            if model_name in self.data[seq] and horizon in self.data[seq][model_name]:
                all_dates.update(self.data[seq][model_name][horizon]["dates"])
        
        sorted_dates = sorted(list(all_dates))
        date_to_row = {date: i for i, date in enumerate(sorted_dates)}
        split_idx = int(len(sorted_dates) * 0.8)
        
        X = np.zeros((len(sorted_dates), len(self.all_sequences)))
        Y = np.zeros((len(sorted_dates), len(self.all_sequences)))
        M = np.zeros((len(sorted_dates), len(self.all_sequences)))
        
        for seq_idx, seq in enumerate(self.all_sequences):
            if model_name not in self.data[seq] or horizon not in self.data[seq][model_name]: continue
            d = self.data[seq][model_name][horizon]
            
            f_vals = np.array(d["forecasts"])
            a_vals = np.array(d["actuals"])
            d_dates = d["dates"]

            # --- THESIS RESCUE: LOCAL MAXIMUM GUARD ---
            # 1. Identify training portion of this specific flight
            train_actuals = []
            for i, date in enumerate(d_dates):
                if date in date_to_row and date_to_row[date] < split_idx:
                    train_actuals.append(a_vals[i])
            
            # 2. Clip forecasts to 2x the historical peak for this route
            # This prevents SARIMA spikes from ruining the spatial image
            if len(train_actuals) > 0:
                local_peak = np.max(train_actuals)
                cap = max(local_peak * 2, 50000) # Minimum cap of 50t
                f_vals = np.clip(f_vals, 0, cap)
            else:
                f_vals = np.clip(f_vals, 0, 1000000)

            for i, date in enumerate(d_dates):
                if date in date_to_row:
                    r = date_to_row[date]
                    X[r, seq_idx] = f_vals[i]
                    Y[r, seq_idx] = a_vals[i]
                    M[r, seq_idx] = 1.0

        df_dates = pd.to_datetime(sorted_dates)
        dow = pd.get_dummies(df_dates.dayofweek).values
        if dow.shape[1] < 7:
            temp = np.zeros((len(sorted_dates), 7)); temp[:, :dow.shape[1]] = dow; dow = temp

        return X, Y, M, dow, sorted_dates

    def build_image_tensors(self, X, M):
        batch_size = X.shape[0]
        H, W = len(self.origins), len(self.destinations)
        C = 2 * self.max_fs
        img = np.zeros((batch_size, C, H, W))
        for seq_idx, seq in enumerate(self.all_sequences):
            parts = seq.split('_')
            o_i, d_i, fs_i = self.orig_to_idx[parts[0]], self.dest_to_idx[parts[1]], int(parts[2][2:]) - 1
            img[:, fs_i, o_i, d_i] = X[:, seq_idx]
            img[:, self.max_fs + fs_i, o_i, d_i] = M[:, seq_idx]
        return img

    def flatten_prediction(self, img_pred):
        batch_size = img_pred.shape[0]
        out = np.zeros((batch_size, len(self.all_sequences)))
        for seq_idx, seq in enumerate(self.all_sequences):
            parts = seq.split('_')
            o_i, d_i, fs_i = self.orig_to_idx[parts[0]], self.dest_to_idx[parts[1]], int(parts[2][2:]) - 1
            out[:, seq_idx] = img_pred[:, fs_i, o_i, d_i]
        return out
