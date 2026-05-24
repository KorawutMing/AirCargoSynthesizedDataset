import numpy as np
import pandas as pd
import json
from collections import defaultdict

class ResidualDataManager:
    def __init__(self, harvested_json_path):
        with open(harvested_json_path, 'r') as f:
            raw_list = json.load(f)
        
        self.segments = ['Contract', 'General', 'Perishable', 'Express', 'Spot']
        self.seg_to_idx = {s: i for i, s in enumerate(self.segments)}
        self.num_segs = len(self.segments)
        
        self.data = defaultdict(lambda: defaultdict(dict))
        all_seqs = set()
        
        for record in raw_list:
            # Use Flight_ID + Segment as unique sequence
            fid = f"{record['Flight_ID']}_{record['Segment']}"
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
        
        # Max flight sequence number (e.g., 4)
        self.max_fs_num = max(int(f.split('_')[2][2:]) for f in self.all_sequences)
        # Total channels per OD pair (flights * segments)
        self.total_channels_per_od = self.max_fs_num * self.num_segs

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
            train_actuals = []
            for i, date in enumerate(d_dates):
                if date in date_to_row and date_to_row[date] < split_idx:
                    train_actuals.append(a_vals[i])
            
            if len(train_actuals) > 0:
                local_peak = np.max(train_actuals)
                cap = max(local_peak * 2.5, 20000) # Slightly higher cap for segments
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
        C = 2 * self.total_channels_per_od
        img = np.zeros((batch_size, C, H, W))
        for seq_idx, seq in enumerate(self.all_sequences):
            parts = seq.split('_')
            # Origin_Dest_FSX_Segment
            o_i = self.orig_to_idx[parts[0]]
            d_i = self.dest_to_idx[parts[1]]
            fs_i = int(parts[2][2:]) - 1
            seg_i = self.seg_to_idx[parts[3]]
            
            # Map (FlightSeq, Segment) to channel index
            channel_idx = fs_i * self.num_segs + seg_i
            
            img[:, channel_idx, o_i, d_i] = X[:, seq_idx]
            img[:, self.total_channels_per_od + channel_idx, o_i, d_i] = M[:, seq_idx]
        return img

    def flatten_prediction(self, img_pred):
        batch_size = img_pred.shape[0]
        out = np.zeros((batch_size, len(self.all_sequences)))
        for seq_idx, seq in enumerate(self.all_sequences):
            parts = seq.split('_')
            o_i = self.orig_to_idx[parts[0]]
            d_i = self.dest_to_idx[parts[1]]
            fs_i = int(parts[2][2:]) - 1
            seg_i = self.seg_to_idx[parts[3]]
            
            channel_idx = fs_i * self.num_segs + seg_i
            out[:, seq_idx] = img_pred[:, channel_idx, o_i, d_i]
        return out
