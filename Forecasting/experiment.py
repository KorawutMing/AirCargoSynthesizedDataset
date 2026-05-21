import pandas as pd
import numpy as np
import os
import random
from sklearn.model_selection import TimeSeriesSplit

from .models.baseline import NaiveForecaster, SMAForecaster, WeightedPersistenceForecaster
from .models.statistical import ARIMAForecaster, SARIMAForecaster
from .models.transformer import TransformerForecaster
from .utils.metrics import calculate_metrics

class ForecastingExperiment:
    """
    Robust suite for cross-validating forecasting models on air cargo demand.
    Uses TimeSeriesSplit to ensure no temporal data leakage.
    """
    def __init__(self, data_path, segments=None):
        self.data_path = data_path
        self.segments = segments or ["Contract", "General", "Perishable", "Express", "Spot"]
        self._df = None

    def load_data(self):
        if self._df is None:
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f"Data file not found at {self.data_path}")
            self._df = pd.read_csv(self.data_path)
            self._df["Date"] = pd.to_datetime(self._df["Date"])
        return self._df

    def get_route_data(self, origin, destination):
        df = self.load_data()
        route_df = df[(df["Origin"] == origin) & (df["Destination"] == destination)]
        oracle_cols = [f"Oracle_{s}_kg" for s in self.segments]
        return route_df.groupby("Date")[oracle_cols].sum()

    def run_ts_cross_validation(self, n_routes=5, n_splits=3, horizon=30, seed=42):
        """
        Runs TimeSeriesSplit CV on selected routes.
        """
        random.seed(seed)
        df = self.load_data()
        all_routes = df.groupby(['Origin', 'Destination']).size().index.tolist()
        selected_routes = random.sample(all_routes, min(n_routes, len(all_routes)))
        
        print(f"Starting TimeSeries Cross-Validation (splits={n_splits}) on {len(selected_routes)} routes...")
        
        results = []
        tscv = TimeSeriesSplit(n_splits=n_splits, test_size=horizon)
        
        for origin, dest in selected_routes:
            ts_data = self.get_route_data(origin, dest)
            
            for segment_col in ts_data.columns:
                y = ts_data[segment_col].values
                if len(y) < (n_splits + 1) * horizon:
                    continue # Skip if series is too short
                
                segment_name = segment_col.replace("Oracle_", "").replace("_kg", "")
                
                for i, (train_index, test_index) in enumerate(tscv.split(y)):
                    y_train, y_test = y[train_index], y[test_index]
                    
                    models = {
                        "Naive": NaiveForecaster(horizon=horizon),
                        "Persistence+": WeightedPersistenceForecaster(horizon=horizon),
                        "SMA": SMAForecaster(window=30, horizon=horizon),
                        "ARIMA": ARIMAForecaster(horizon=horizon),
                        "SARIMA": SARIMAForecaster(horizon=horizon),
                        "Transformer": TransformerForecaster(horizon=horizon, epochs=50, patience=10)
                    }
                    
                    for name, model in models.items():
                        try:
                            model.train(y_train)
                            y_pred = model.predict(steps=horizon)
                            
                            metrics = calculate_metrics(y_test, y_pred)
                            metrics.update({
                                "Route": f"{origin}-{dest}",
                                "Segment": segment_name,
                                "Model": name,
                                "Fold": i
                            })
                            results.append(metrics)
                        except Exception as e:
                            print(f"Error training {name} on fold {i}: {e}")
                            
        return pd.DataFrame(results)

if __name__ == "__main__":
    DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/air_cargo_10yr_dataset.csv")
    experiment = ForecastingExperiment(DATA_PATH)
    
    # Run on 5 routes with 3 splits for a robust report
    df_results = experiment.run_ts_cross_validation(n_routes=5, n_splits=3, horizon=30)
    
    if not df_results.empty:
        print("\n--- Summary Performance (Mean Metrics across Folds) ---")
        summary = df_results.groupby("Model")[["MAE", "RMSE", "WAPE", "Trend (Corr)", "Bias"]].mean()
        print(summary.sort_values("MAE"))
        
        print("\n--- Model Win Rates (%) by MAE ---")
        # Best model per Route/Segment/Fold
        df_results["Is_Best"] = df_results.groupby(["Route", "Segment", "Fold"])["MAE"].transform(lambda x: x == x.min())
        win_rates = (df_results[df_results["Is_Best"]].groupby("Model").size() / 
                     df_results.groupby(["Route", "Segment", "Fold"]).ngroups * 100)
        print(win_rates.sort_values(ascending=False))
    else:
        print("No results generated.")
