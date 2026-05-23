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
        
        # Parse Hubs
        self.origins = set()
        self.destinations = set()
        
        for record in raw_list:
            fid = record["Flight_ID"]
            model = record["Model"]
            horizon = str(record["Horizon"])
            seg = record.get("Segment", "Unknown")
            
            # Parse components (e.g. PEK_SIN_FS1)
            parts = fid.split('_')
            self.origins.add(parts[0])
            self.destinations.add(parts[1])
            
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
        
        # Fixed Grid Mapping
        self.sorted_origins = sorted(list(self.origins))
        self.sorted_destinations = sorted(list(self.destinations))
        self.orig_to_idx = {o: i for i, o in enumerate(self.sorted_origins)}
        self.dest_to_idx = {d: i for i, d in enumerate(self.sorted_destinations)}
        
        # Determine Max FS
        self.max_fs = 0
        for seq in self.all_sequences:
            fs_num = int(seq.split('FS')[1])
            if fs_num > self.max_fs: self.max_fs = fs_num
        
        print(f"Registry built: {len(self.all_sequences)} flights, {len(self.sorted_segments)} segments.")
        print(f"Grid: {len(self.sorted_origins)}x{len(self.sorted_destinations)}, Max FS: {self.max_fs}")

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
            f_vals = np.clip(f_vals, 0, 1000000) 

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

    def build_image_tensors(self, X, M):
        """
        Converts flat (Batch, 180) matrices into (Batch, Channels, H, W) images.
        Channels = 2 * Max_FS (Forecasts followed by Masks)
        H = N_Origins, W = N_Destinations
        """
        batch_size = X.shape[0]
        H, W = len(self.sorted_origins), len(self.sorted_destinations)
        C = 2 * self.max_fs
        
        img = np.zeros((batch_size, C, H, W))
        
        for seq_idx, seq in enumerate(self.all_sequences):
            parts = seq.split('_')
            o_idx = self.orig_to_idx[parts[0]]
            d_idx = self.dest_to_idx[parts[1]]
            fs_idx = int(parts[2][2:]) - 1 # FS1 -> 0
            
            # Forecast channels: 0 to max_fs-1
            img[:, fs_idx, o_idx, d_idx] = X[:, seq_idx]
            # Mask channels: max_fs to 2*max_fs-1
            img[:, self.max_fs + fs_idx, o_idx, d_idx] = M[:, seq_idx]
            
        return img

    def flatten_image_prediction(self, img_pred):
        """
        Converts (Batch, Max_FS, H, W) U-Net output back to (Batch, 180).
        """
        batch_size = img_pred.shape[0]
        out = np.zeros((batch_size, len(self.all_sequences)))
        
        for seq_idx, seq in enumerate(self.all_sequences):
            parts = seq.split('_')
            o_idx = self.orig_to_idx[parts[0]]
            d_idx = self.dest_to_idx[parts[1]]
            fs_idx = int(parts[2][2:]) - 1
            
            out[:, seq_idx] = img_pred[:, fs_idx, o_idx, d_idx]
            
        return out
