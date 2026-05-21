import os
import pandas as pd
import numpy as np
import torch
import json

class ResidualDataManager:
    """
    Manages the data pipeline for the Global Residual Predictor.
    """
    def __init__(self, unconstrained_dir, base_data_path):
        self.unconstrained_dir = unconstrained_dir
        self.base_data_path = base_data_path
        self.registry = []
        self._build_registry()

    def _build_registry(self):
        """Identifies all available flight sequences."""
        # Use the base dataset to build a comprehensive registry
        df = pd.read_csv(self.base_data_path)
        groups = df.groupby(['Origin', 'Destination', 'Flight_Sequence']).size().index.tolist()
        for origin, dest, fs in groups:
            self.registry.append({
                "origin": origin,
                "dest": dest,
                "fs": fs,
                "id": f"{origin}_{dest}_FS{fs}"
            })
        self.registry.sort(key=lambda x: x["id"])
        self.flight_id_to_idx = {item["id"]: i for i, item in enumerate(self.registry)}
        print(f"Registry built with {len(self.registry)} flight sequences.")

    def build_network_matrices(self, harvested_json_path, model_name="Transformer", horizon=30):
        """
        Pivots harvested predictions into global matrices.
        Returns tensors:
            - X: (N_samples, N_flights) Forecasts
            - Y: (N_samples, N_flights) True Demand
            - M: (N_samples, N_flights) Presence Mask
            - Dates: List of dates
        """
        print(f"Building matrices for {model_name} (H={horizon})...")
        with open(harvested_json_path, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        # Filter for the specific model and horizon
        df = df[(df["Model"] == model_name) & (df["Horizon"] == horizon)]
        
        # We need to expand the lists of Predictions/Actuals/Dates into individual daily records
        expanded_rows = []
        for _, row in df.iterrows():
            f_id = row["Flight_ID"]
            preds = row["Predictions"]
            acts = row["Actuals"]
            dates = row["Dates"]
            
            for i in range(len(dates)):
                expanded_rows.append({
                    "Date": dates[i],
                    "Flight_ID": f_id,
                    "Pred": preds[i],
                    "Act": acts[i]
                })
        
        exp_df = pd.DataFrame(expanded_rows)
        
        # Pivot to get (Date, Flight_ID) matrices
        # We use 'mean' for aggregation in case of overlapping folds (though CV usually doesn't overlap)
        pivot_pred = exp_df.pivot_table(index="Date", columns="Flight_ID", values="Pred", aggfunc='mean')
        pivot_act = exp_df.pivot_table(index="Date", columns="Flight_ID", values="Act", aggfunc='mean')
        
        all_dates = sorted(pivot_pred.index.tolist())
        n_flights = len(self.registry)
        n_samples = len(all_dates)
        
        X = np.zeros((n_samples, n_flights))
        Y = np.zeros((n_samples, n_flights))
        M = np.zeros((n_samples, n_flights))
        
        for i, date in enumerate(all_dates):
            for j, flight in enumerate(self.registry):
                f_id = flight["id"]
                if f_id in pivot_pred.columns:
                    val_p = pivot_pred.loc[date, f_id]
                    val_a = pivot_act.loc[date, f_id]
                    
                    if not np.isnan(val_p):
                        X[i, j] = val_p
                        Y[i, j] = val_a
                        M[i, j] = 1.0
        
        return (
            torch.FloatTensor(X), 
            torch.FloatTensor(Y), 
            torch.FloatTensor(M), 
            all_dates
        )

    def get_flight_index(self, flight_id):
        return self.flight_id_to_idx.get(flight_id, -1)
