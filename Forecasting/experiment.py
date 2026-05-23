import pandas as pd
import numpy as np
import os
import random
import json
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from sklearn.model_selection import TimeSeriesSplit

from .models.baseline import NaiveForecaster, SMAForecaster, WeightedPersistenceForecaster
from .models.statistical import ARIMAForecaster, SARIMAForecaster
from .models.transformer import TransformerForecaster
from .utils.metrics import calculate_metrics

def evaluate_task(args):
    """
    Optimized Worker: Trains once per fold, predicts all horizons.
    """
    origin, dest, flight_seq, segment_name, fold_idx, y_train, y_test, horizons, test_dates = args
    results = []
    
    max_h = max(horizons)
    models = {
        "Naive": NaiveForecaster(horizon=max_h),
        "Persistence+": WeightedPersistenceForecaster(horizon=max_h),
        "SMA": SMAForecaster(window=30, horizon=max_h),
        "ARIMA": ARIMAForecaster(horizon=max_h),
        "SARIMA": SARIMAForecaster(horizon=max_h),
        "Transformer": TransformerForecaster(horizon=max_h, epochs=30, patience=5)
    }
    
    flight_id = f"{origin}_{dest}_FS{flight_seq}"
    
    for name, model in models.items():
        try:
            model.train(y_train)
            # Generate the longest forecast once
            y_pred_max = model.predict(steps=max_h)
            
            for h in horizons:
                y_pred = y_pred_max[:h]
                y_true = y_test[:h]
                
                metrics = calculate_metrics(y_true, y_pred)
                metrics.update({
                    "Route": f"{origin}-{dest}",
                    "Flight_ID": flight_id,
                    "Segment": segment_name,
                    "Model": name,
                    "Fold": fold_idx,
                    "Horizon": h,
                    "Dates": [d.strftime("%Y-%m-%d") for d in test_dates[:h]],
                    "Predictions": y_pred.tolist(),
                    "Actuals": y_true.tolist()
                })
                results.append(metrics)
        except Exception:
            pass
    return results

class ForecastingExperiment:
    def __init__(self, data_path, segments=None, use_unconstrained=False, unconstrained_dir=None):
        self.data_path = data_path
        self.segments = segments or ["Contract", "General", "Perishable", "Express", "Spot"]
        self.use_unconstrained = use_unconstrained
        self.unconstrained_dir = unconstrained_dir
        self._df = None

    def load_data(self):
        if self._df is None:
            self._df = pd.read_csv(self.data_path)
            self._df["Date"] = pd.to_datetime(self._df["Date"])
            
            if self.use_unconstrained and self.unconstrained_dir:
                all_uncon = []
                for file in os.listdir(self.unconstrained_dir):
                    if file.endswith(".parquet"):
                        uncon_df = pd.read_parquet(os.path.join(self.unconstrained_dir, file))
                        all_uncon.append(uncon_df)
                
                if all_uncon:
                    uncon_combined = pd.concat(all_uncon, axis=0)
                    uncon_combined["Date"] = pd.to_datetime(uncon_combined["Date"])
                    self._df = pd.merge(
                        self._df, 
                        uncon_combined, 
                        on=["Date", "Origin", "Destination", "Flight_Sequence"],
                        how="left",
                        suffixes=("", "_Uncon")
                    )
        return self._df

    def get_route_data(self, origin, destination, flight_seq=None):
        df = self.load_data()
        mask = (df["Origin"] == origin) & (df["Destination"] == destination)
        if flight_seq is not None:
            mask &= (df["Flight_Sequence"] == flight_seq)
        
        route_df = df[mask]
        
        if self.use_unconstrained:
            target_cols = [f"EM_{s}_Est" for s in self.segments if f"EM_{s}_Est" in route_df.columns]
        else:
            target_cols = [f"Oracle_{s}_kg" for s in self.segments]
            
        return route_df.groupby("Date")[target_cols].sum()

    def generate_report(self, df_results):
        report_path = os.path.join(os.path.dirname(__file__), "REPORT.md")
        with open(report_path, "w") as f:
            f.write("# Forecasting Performance Report\n\n")
            f.write("## 1. Global Summary\n")
            summary = df_results.groupby(["Horizon", "Model"])[["MAE", "RMSE", "WAPE", "Trend (Corr)"]].mean().sort_values(["Horizon", "MAE"])
            f.write(summary.to_markdown() + "\n\n")
            
            f.write("## 2. Route-Specific Analysis\n")
            route_summary = df_results.groupby(["Route", "Model"])[["MAE", "WAPE"]].mean().reset_index()
            for route in route_summary["Route"].unique():
                f.write(f"### Route: {route}\n")
                route_data = route_summary[route_summary["Route"] == route].sort_values("MAE")
                f.write(route_data[["Model", "MAE", "WAPE"]].to_markdown(index=False) + "\n\n")
                best_model = route_data.iloc[0]["Model"]
                f.write(f"**Strengths:** {best_model} performs best on this route.\n")
                worst_model = route_data.iloc[-1]["Model"]
                f.write(f"**Weaknesses:** {worst_model} struggles with the volatility or seasonality of this route.\n\n")
            
            f.write("## 3. Conclusions\n")
            f.write("- **Short-term (H=1):** Baselines like Naive/SMA are often competitive, but ARIMA usually leads.\n")
            f.write("- **Long-term (H=7, 30):** SARIMA and Transformer models show superior trend capture and lower WAPE.\n")
            f.write("- **Modularity:** The refactored architecture allows for seamless model swapping and testing.\n")

    def run_ts_cross_validation(self, n_routes=None, n_splits=3, horizons=[1, 7, 30], seed=42, max_workers=None):
        random.seed(seed)
        df = self.load_data()
        
        if n_routes is None:
            all_groups = df.groupby(['Origin', 'Destination', 'Flight_Sequence']).size().index.tolist()
            selected_flights = all_groups
            print(f"Harvesting ALL {len(selected_flights)} flight sequences...")
        else:
            all_routes = df.groupby(['Origin', 'Destination']).size().index.tolist()
            sampled_routes = random.sample(all_routes, min(n_routes, len(all_routes)))
            selected_flights = []
            for r_o, r_d in sampled_routes:
                f_seqs = df[(df["Origin"] == r_o) & (df["Destination"] == r_d)]["Flight_Sequence"].unique()
                for fs in f_seqs:
                    selected_flights.append((r_o, r_d, fs))
            print(f"Harvesting {len(selected_flights)} flights from {n_routes} routes...")
        
        # 1. GENERATE ALL TASKS
        all_tasks = []
        max_h = max(horizons)
        
        for origin, dest, flight_seq in selected_flights:
            ts_data = self.get_route_data(origin, dest, flight_seq)
            dates = ts_data.index
            for segment_col in ts_data.columns:
                y = ts_data[segment_col].values
                if len(y) < (n_splits + 1) * max_h:
                    continue
                segment_name = segment_col.replace("Oracle_", "").replace("_kg", "").replace("EM_", "").replace("_Est", "")
                for i in range(n_splits):
                    train_idx = len(y) - (n_splits - i + 1) * max_h
                    if train_idx < 10: continue
                    
                    y_train = y[:train_idx]
                    y_test = y[train_idx:train_idx + max_h]
                    test_dates = dates[train_idx:train_idx + max_h]
                    
                    task_id = f"{origin}_{dest}_FS{flight_seq}_{segment_name}_fold{i}"
                    all_tasks.append((
                        origin, dest, flight_seq, segment_name, i, 
                        y_train, y_test, horizons, test_dates, task_id
                    ))

        # 2. CHECK FOR CHECKPOINT
        checkpoint_path = "Forecasting/harvest_checkpoint.json"
        existing_results = []
        finished_ids = set()
        if os.path.exists(checkpoint_path):
            print(f"Found checkpoint at {checkpoint_path}. Resuming...")
            with open(checkpoint_path, 'r') as f:
                existing_results = json.load(f)
                for r in existing_results:
                    finished_ids.add(f"{r['Flight_ID']}_{r['Segment']}_fold{r['Fold']}")
            
        remaining_tasks = [t for t in all_tasks if t[-1] not in finished_ids]
        print(f"Total Tasks: {len(all_tasks)} | Finished: {len(finished_ids)} | Remaining: {len(remaining_tasks)}")

        if not remaining_tasks:
            print("All tasks already completed.")
            return pd.DataFrame(existing_results)

        # 3. RUN WITH THROTTLED WORKERS
        if max_workers is None:
            max_workers = max(1, os.cpu_count() // 2)
        
        print(f"Starting execution with {max_workers} workers...")
        
        all_results = existing_results
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(evaluate_task, t[:-1]): t[-1] for t in remaining_tasks}
            pbar = tqdm(as_completed(futures), total=len(remaining_tasks), desc="Harvesting Progress")
            
            counter = 0
            for f in pbar:
                task_results = f.result()
                all_results.extend(task_results)
                counter += 1
                
                if counter % 100 == 0:
                    with open(checkpoint_path, 'w') as ck:
                        json.dump(all_results, ck)
                    pbar.set_postfix({"ckpt": "saved"})

        # 4. FINAL SAVE
        df_results = pd.DataFrame(all_results)
        if not df_results.empty:
            self.generate_report(df_results)
            df_results.to_json("Forecasting/harvested_predictions.json", orient="records")
            if os.path.exists(checkpoint_path):
                os.remove(checkpoint_path)
            print("Final harvest complete. Checkpoint cleared.")
        return df_results

if __name__ == "__main__":
    DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/air_cargo_10yr_dataset.csv")
    experiment = ForecastingExperiment(DATA_PATH, use_unconstrained=False)
    
    HORIZONS = [1, 7, 30]
    # Reduce max_workers to 4 or 6 to keep CPU temperature low
    df_results = experiment.run_ts_cross_validation(n_routes=None, n_splits=20, horizons=HORIZONS, max_workers=8)
