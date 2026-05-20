import pandas as pd
import numpy as np
import os
import random
from scipy.stats import pearsonr
from .base_models import NaiveForecaster, YoloForecaster
from .transformer_forecaster import TransformerForecaster

class ForecastingExperiment:
    """
    Academic suite for cross-validating forecasting models on air cargo demand.
    
    Args:
        data_path (str): Path to the oracle 10yr dataset.
        segments (list): Cargo segments to evaluate.
    """
    def __init__(self, data_path, segments=None):
        self.data_path = data_path
        self.segments = segments or ["Contract", "General", "Perishable", "Express", "Spot"]
        self._df = None

    def load_data(self):
        if self._df is None:
            self._df = pd.read_csv(self.data_path)
            self._df["Date"] = pd.to_datetime(self._df["Date"])
        return self._df

    def get_route_data(self, origin, destination):
        df = self.load_data()
        route_df = df[(df["Origin"] == origin) & (df["Destination"] == destination)]
        oracle_cols = [f"Oracle_{s}_kg" for s in self.segments]
        return route_df.groupby("Date")[oracle_cols].sum()

    def analyze_metrics(self, y_true, y_pred):
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        
        # Pearson correlation for trend capture
        if len(y_true) > 1 and np.std(y_true) > 0 and np.std(y_pred) > 0:
            corr, _ = pearsonr(y_true, y_pred)
        else:
            corr = 0.0
            
        bias = np.mean(y_pred - y_true)
        mae = np.mean(np.abs(y_pred - y_true))
        rmse = np.sqrt(np.mean((y_true - y_pred)**2))
        
        return {"MAE": mae, "RMSE": rmse, "Trend (Corr)": corr, "Bias": bias}

    def run_cross_validation(self, n_routes=10, horizon=30, seed=42):
        random.seed(seed)
        df = self.load_data()
        all_routes = df.groupby(['Origin', 'Destination']).size().index.tolist()
        selected_routes = random.sample(all_routes, min(n_routes, len(all_routes)))
        
        print(f"Starting Cross-Validation on {len(selected_routes)} routes...")
        
        results = []
        for origin, dest in selected_routes:
            ts_data = self.get_route_data(origin, dest)
            split_idx = int(len(ts_data) * 0.8)
            train_ts = ts_data.iloc[:split_idx]
            test_ts = ts_data.iloc[split_idx:split_idx+horizon]
            
            for segment_col in ts_data.columns:
                y_train = train_ts[segment_col].values
                y_test = test_ts[segment_col].values
                
                models = {
                    "Naive": NaiveForecaster(horizon=horizon),
                    "Yolo": YoloForecaster(horizon=horizon),
                    "Transformer": TransformerForecaster(horizon=horizon, epochs=30)
                }
                
                for name, model in models.items():
                    model.train(y_train)
                    y_pred = model.predict(steps=horizon)
                    
                    metrics = self.analyze_metrics(y_test, y_pred)
                    metrics.update({
                        "Route": f"{origin}-{dest}",
                        "Segment": segment_col.replace("Oracle_", "").replace("_kg", ""),
                        "Model": name
                    })
                    results.append(metrics)
                    
        return pd.DataFrame(results)

if __name__ == "__main__":
    DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/air_cargo_10yr_dataset.csv")
    experiment = ForecastingExperiment(DATA_PATH)
    
    # Quick verification on 2 routes
    df_results = experiment.run_cross_validation(n_routes=2, horizon=30)
    
    print("\n--- Summary Performance (Mean Metrics) ---")
    summary = df_results.groupby("Model")[["MAE", "RMSE", "Trend (Corr)", "Bias"]].mean()
    print(summary)
    
    print("\n--- Win Rates (%) ---")
    df_results["Is_Best"] = df_results.groupby(["Route", "Segment"])["MAE"].transform(lambda x: x == x.min())
    win_rates = (df_results[df_results["Is_Best"]].groupby("Model").size() / df_results.groupby(["Route", "Segment"]).ngroups * 100)
    print(win_rates.sort_values(ascending=False))
