import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
import os
from .data_manager import ResidualDataManager
from .model import GlobalResidualPredictor, train_residual_step
from ..utils.metrics import calculate_metrics

def train_and_evaluate_spatial(harvested_json, base_data_path, model_name="Transformer", horizon=30):
    print(f"\n{'='*50}")
    print(f"TRAINING SPATIAL REFINER FOR: {model_name} (H={horizon})")
    print(f"{'='*50}")
    
    # 1. Load and Prepare Data
    dm = ResidualDataManager(
        unconstrained_dir="Unconstraining/unconstrained_results", 
        base_data_path=base_data_path
    )
    
    try:
        X, Y, M, dates = dm.build_network_matrices(harvested_json, model_name, horizon)
    except Exception as e:
        print(f"Skipping {model_name} H={horizon}: Data not sufficient. ({e})")
        return
        
    if len(X) < 10:
        print(f"Skipping {model_name} H={horizon}: Too few samples.")
        return

    # 2. STRICT TEMPORAL SPLIT (No Leakage)
    # Use first 80% of days for training, last 20% for testing
    split_idx = int(len(X) * 0.8)
    
    X_train, Y_train, M_train = X[:split_idx], Y[:split_idx], M[:split_idx]
    X_test, Y_test, M_test = X[split_idx:], Y[split_idx:], M[split_idx:]
    
    print(f"Training on {len(X_train)} days, Testing on {len(X_test)} days.")

    # 3. Initialize Model
    n_flights = X.shape[1]
    model = GlobalResidualPredictor(n_flights=n_flights)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    X_train, Y_train, M_train = X_train.to(device), Y_train.to(device), M_train.to(device)
    X_test, Y_test, M_test = X_test.to(device), Y_test.to(device), M_test.to(device)

    # 4. Training Loop
    best_loss = float('inf')
    patience = 20
    no_improve = 0
    
    for epoch in range(200):
        loss = train_residual_step(model, optimizer, criterion, X_train, M_train, Y_train)
        
        if epoch % 20 == 0:
            print(f"Epoch {epoch}: Loss = {loss:.4f}")
            
        if loss < best_loss:
            best_loss = loss
            no_improve = 0
        else:
            no_improve += 1
            
        if no_improve >= patience:
            print(f"Early stopping at epoch {epoch}")
            break

    # 5. Final Evaluation
    model.eval()
    with torch.no_grad():
        predicted_residuals = model(X_test, M_test)
        refined_forecasts = X_test + predicted_residuals
        
        # Move back to CPU for metric calculation
        y_raw = X_test.cpu().numpy()
        y_refined = refined_forecasts.cpu().numpy()
        y_true = Y_test.cpu().numpy()
        mask = M_test.cpu().numpy()
        
        # Calculate metrics ONLY where mask == 1 (flight exists)
        # Flatten for global comparison
        raw_flat = y_raw[mask == 1]
        refined_flat = y_refined[mask == 1]
        true_flat = y_true[mask == 1]
        
        metrics_raw = calculate_metrics(true_flat, raw_flat)
        metrics_refined = calculate_metrics(true_flat, refined_flat)
        
        print("\n--- PERFORMANCE COMPARISON (Global Network) ---")
        print(f"{'Metric':<15} | {'Original':<15} | {'Spatial-Refined':<15} | {'Improvement':<15}")
        print("-" * 65)
        for m in ["MAE", "RMSE", "WAPE"]:
            orig = metrics_raw[m]
            refi = metrics_refined[m]
            imp = ((orig - refi) / orig) * 100 if orig != 0 else 0
            print(f"{m:<15} | {orig:<15.2f} | {refi:<15.2f} | {imp:>14.2f}%")

if __name__ == "__main__":
    HARVESTED_JSON = "Forecasting/harvested_predictions.json"
    BASE_DATA = "data/air_cargo_10yr_dataset.csv"
    
    if not os.path.exists(HARVESTED_JSON):
        print(f"Error: {HARVESTED_JSON} not found. Run the Data Harvest first.")
    else:
        models = ["Transformer", "SARIMA", "ARIMA", "Persistence+", "Naive"]
        horizons = [1, 7, 30]
        
        for m in models:
            for h in horizons:
                train_and_evaluate_spatial(HARVESTED_JSON, BASE_DATA, m, h)
