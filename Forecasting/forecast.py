import pandas as pd
import numpy as np
import os
import random
import json
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from .models.baseline import NaiveForecaster, SMAForecaster, WeightedPersistenceForecaster
from .models.statistical import ARIMAForecaster, SARIMAForecaster
from .models.transformer import TransformerForecaster
from .utils.metrics import calculate_metrics

def evaluate_task_rolling_single_model(args):
    """
    Highly granular worker: Trains and predicts for ONE model.
    """
    origin, dest, flight_seq, segment_name, model_name, y_all, dates, test_start_idx, horizons = args
    results = []
    
    y_train = y_all[:test_start_idx]
    y_test_full = y_all[test_start_idx:]
    test_dates_full = dates[test_start_idx:]
    
    max_h = max(horizons)
    flight_id = f"{origin}_{dest}_FS{flight_seq}"
    
    # Define model based on name
    if model_name == "Naive": model = NaiveForecaster(horizon=max_h)
    elif model_name == "Persistence+": model = WeightedPersistenceForecaster(horizon=max_h)
    elif model_name == "SMA": model = SMAForecaster(window=30, horizon=max_h)
    elif model_name == "ARIMA": model = ARIMAForecaster(horizon=max_h)
    elif model_name == "SARIMA": model = SARIMAForecaster(horizon=max_h)
    elif model_name == "Transformer": model = TransformerForecaster(horizon=max_h, epochs=30, patience=5)
    else: return []

    try:
        model.train(y_train)
        
        for h in horizons:
            preds = []
            actuals = []
            valid_dates = []
            
            if model_name == "Naive":
                for i in range(len(y_test_full)):
                    val = y_train[-(h-i)] if i < h else y_test_full[i-h]
                    preds.append(float(val)); actuals.append(float(y_test_full[i]))
                    valid_dates.append(test_dates_full[i].strftime("%Y-%m-%d"))
            
            elif model_name == "SMA":
                for i in range(len(y_test_full)):
                    window = (list(y_train) + list(y_test_full[:i-h+1]))[-30:] if i >= h else y_train[-(30+h-i):][:30]
                    preds.append(float(np.mean(window))); actuals.append(float(y_test_full[i]))
                    valid_dates.append(test_dates_full[i].strftime("%Y-%m-%d"))
            
            else:
                y_pred_long = model.predict(steps=len(y_test_full))
                if len(y_pred_long) < len(y_test_full):
                    last_p = y_pred_long[-1] if len(y_pred_long) > 0 else 0
                    y_pred_long = np.concatenate([y_pred_long, np.full(len(y_test_full)-len(y_pred_long), last_p)])
                
                preds = [float(p) for p in y_pred_long]
                actuals = [float(a) for a in y_test_full]
                valid_dates = [d.strftime("%Y-%m-%d") for d in test_dates_full]

            metrics = calculate_metrics(np.array(actuals), np.array(preds))
            metrics.update({
                "Route": f"{origin}-{dest}", "Flight_ID": flight_id, "Segment": segment_name,
                "Model": model_name, "Fold": 0, "Horizon": h, "Dates": valid_dates,
                "Predictions": preds, "Actuals": actuals
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
        report_path = os.path.join(os.path.dirname(__file__), "results", "REPORT.md")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w") as f:
            f.write("# Forecasting Performance Report (Rolling Inference Mode)\n\n")
            f.write("## 1. Global Summary\n")
            summary = df_results.groupby(["Horizon", "Model"])[["MAE", "RMSE", "WAPE", "Trend (Corr)"]].mean().sort_values(["Horizon", "MAE"])
            f.write(summary.to_markdown() + "\n\n")
            
            f.write("## 2. Route-Specific Analysis (Sample)\n")
            route_summary = df_results.groupby(["Route", "Model"])[["MAE", "WAPE"]].mean().reset_index()
            for route in route_summary["Route"].unique()[:10]: # Limit report size
                f.write(f"### Route: {route}\n")
                route_data = route_summary[route_summary["Route"] == route].sort_values("MAE")
                f.write(route_data[["Model", "MAE", "WAPE"]].to_markdown(index=False) + "\n\n")

    def run_rolling_harvest(self, test_days=730, horizons=[1, 7, 30], seed=42, max_workers=None):
        random.seed(seed)
        df = self.load_data()
        
        all_groups = df.groupby(['Origin', 'Destination', 'Flight_Sequence']).size().index.tolist()
        model_names = ["Naive", "Persistence+", "SMA", "ARIMA", "SARIMA", "Transformer"]
        
        all_tasks = []
        for origin, dest, flight_seq in all_groups:
            ts_data = self.get_route_data(origin, dest, flight_seq)
            dates = ts_data.index
            test_start_idx = len(ts_data) - test_days
            if test_start_idx < 100: continue
            
            for segment_col in ts_data.columns:
                y = ts_data[segment_col].values
                segment_name = segment_col.replace("Oracle_", "").replace("_kg", "").replace("EM_", "").replace("_Est", "")
                
                for m_name in model_names:
                    all_tasks.append((
                        origin, dest, flight_seq, segment_name, m_name, y, dates, test_start_idx, horizons
                    ))

        if max_workers is None:
            max_workers = max(1, os.cpu_count() // 2)
        
        print(f"Starting Highly Granular Harvest: {len(all_tasks)} tasks...")
        
        all_results = []
        save_path = "Forecasting/results/harvested_predictions.json"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(evaluate_task_rolling_single_model, t): t[4] for t in all_tasks}
            pbar = tqdm(as_completed(futures), total=len(all_tasks), desc="Rolling Forecasts", dynamic_ncols=True)
            
            counter = 0
            for future in pbar:
                task_results = future.result()
                all_results.extend(task_results)
                counter += 1
                
                if counter % 100 == 0:
                    with open(save_path, 'w') as ck:
                        json.dump(all_results, ck)
                    pbar.set_postfix({"ckpt": "saved"})

        df_results = pd.DataFrame(all_results)
        if not df_results.empty:
            self.generate_report(df_results)
            df_results.to_json(save_path, orient="records")
            print(f"Rolling harvest complete. Results saved to {save_path}")
        return df_results

if __name__ == "__main__":
    DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/air_cargo_10yr_dataset.csv")
    experiment = ForecastingExperiment(DATA_PATH)
    experiment.run_rolling_harvest(test_days=730, horizons=[1, 7, 30], max_workers=8)
