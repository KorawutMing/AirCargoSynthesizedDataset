import os
import pandas as pd
import numpy as np
import torch
from ...Forecasting.experiment import ForecastingExperiment

class ResidualDataManager:
    """
    Manages the data pipeline for the Global Residual Predictor.
    - registry: List of all unique (Origin, Destination, Flight_Sequence)
    - ground_truth: Matrix [Dates, N_flights] from Parquets
    - forecasts: Matrix [Dates, N_flights] from TS models
    """
    def __init__(self, unconstrained_dir, base_data_path):
        self.unconstrained_dir = unconstrained_dir
        self.base_data_path = base_data_path
        self.registry = []
        self._build_registry()

    def _build_registry(self):
        """Identifies all available flight sequences from the unconstrained results."""
        files = [f for f in os.listdir(self.unconstrained_dir) if f.endswith(".parquet")]
        for f in files:
            # Example: PVG_PEK_FS1.parquet
            parts = f.replace(".parquet", "").split("_")
            origin, dest = parts[0], parts[1]
            fs = int(parts[2].replace("FS", ""))
            self.registry.append({
                "origin": origin,
                "dest": dest,
                "fs": fs,
                "id": f"{origin}_{dest}_FS{fs}"
            })
        self.registry.sort(key=lambda x: x["id"])
        print(f"Registry built with {len(self.registry)} flight sequences.")

    def build_network_matrices(self, model_name="Transformer", horizon=30):
        """
        Constructs the Global Forecast and Global Truth matrices.
        Returns: 
            - X: (Dates, N_flights) Forecasts
            - Y: (Dates, N_flights) True Unconstrained Demand
            - M: (Dates, N_flights) Presence Mask
        """
        # This requires the experiment results to be saved.
        # For now, let's assume we have a processed CSV of all predictions.
        pass

    def get_flight_index(self, origin, dest, fs):
        flight_id = f"{origin}_{dest}_FS{fs}"
        for i, item in enumerate(self.registry):
            if item["id"] == flight_id:
                return i
        return -1
