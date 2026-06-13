import os
import sys
import pandas as pd
import json

# Add the current directory to path so Forecasting is recognized as a package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Forecasting.forecast import ForecastingExperiment

DATA_PATH = "data/air_cargo_3yr_LF_80.csv"
RESULTS_DIR = "Forecasting/results"

if __name__ == "__main__":
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    print(f"Loading data from {DATA_PATH}...")
    UNCONSTRAINED_DIR = "Unconstraining/results/unconstrained_3yr"
    experiment = ForecastingExperiment(
        DATA_PATH, 
        use_unconstrained=True, 
        unconstrained_dir=UNCONSTRAINED_DIR
    )
    
    # Run cross-validation on all routes
    # n_splits=26 for 3 years to ensure 1 year of contiguous test data (26 * 14 = 364 days)
    print("Starting cross-validation harvest for H=14...")
    df_results = experiment.run_ts_cross_validation(
        n_routes=None, 
        n_splits=26, 
        horizons=[14], 
        max_workers=None
    )
    
    print("\nForecasting Baseline Complete.")
    print(f"Results saved to {RESULTS_DIR}")
