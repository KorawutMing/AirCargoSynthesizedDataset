import torch
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import sys
import os

# Robust path handling for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from data_manager import ResidualDataManager
from model import GlobalResidualPredictor
from sklearn.preprocessing import StandardScaler

def visualize_flight(model_name, horizon, flight_id):
    # Path is relative to project root
    harvested_path = os.path.join("Forecasting", "results", "harvested_predictions.json")
    dm = ResidualDataManager(harvested_path)
    X_raw, Y_raw, M_raw, E_raw, dates = dm.get_matrices(model_name, horizon)
    
    Resid_raw = Y_raw - X_raw
    split_idx = int(len(X_raw) * 0.8)
    
    tr_X, te_X = X_raw[:split_idx], X_raw[split_idx:]
    tr_R, te_R = Resid_raw[:split_idx], Resid_raw[split_idx:]
    tr_E, te_E = E_raw[:split_idx], E_raw[split_idx:]
    tr_M, te_M = M_raw[:split_idx], M_raw[split_idx:]
    te_Y_raw = Y_raw[split_idx:]
    te_dates = dates[split_idx:]

    sc_X, sc_R, sc_E = StandardScaler(), StandardScaler(), StandardScaler()
    sc_X.fit(tr_X)
    sc_R.fit(tr_R)
    sc_E.fit(tr_E)
    
    te_X_sc = sc_X.transform(te_X)
    te_E_sc = sc_E.transform(te_E)
    
    te_X_img = dm.build_image_tensors(te_X_sc, te_M)
    
    # Load model
    weights_path = os.path.join(current_dir, "results", "weights", f"{model_name}_H{horizon}.pt")
    model = GlobalResidualPredictor(in_channels=dm.total_channels_per_od*2, out_channels=dm.total_channels_per_od, extra_dim=te_E_sc.shape[1], hidden_dim=32)
    model.load_state_dict(torch.load(weights_path, weights_only=True))
    model.eval()
    
    with torch.no_grad():
        ref_R_img = model(torch.FloatTensor(te_X_img), None, torch.FloatTensor(te_E_sc)).numpy()
        ref_R = sc_R.inverse_transform(dm.flatten_prediction(ref_R_img))
        ref_Y = (te_X + ref_R) * te_M
        act_Y = te_Y_raw * te_M
        orig_X = te_X * te_M

    # Find index for flight_id
    if flight_id not in dm.all_sequences:
        print(f"Flight ID {flight_id} not found.")
        return
    
    seq_idx = dm.all_sequences.index(flight_id)
    
    # Extract timeseries for test set
    oracle = act_Y[:, seq_idx]
    forecast = orig_X[:, seq_idx]
    recovered = ref_Y[:, seq_idx]
    mask = te_M[:, seq_idx]
    
    # Filter by mask (where data exists)
    valid_indices = np.where(mask > 0)[0]
    oracle = oracle[valid_indices]
    forecast = forecast[valid_indices]
    recovered = recovered[valid_indices]
    plot_dates = [te_dates[i] for i in valid_indices]
    
    # Metrics
    def get_metrics(p, t):
        rmse = np.sqrt(np.mean((p-t)**2))
        mae = np.mean(np.abs(p-t))
        return rmse, mae

    r_o, m_o = get_metrics(forecast, oracle)
    r_r, m_r = get_metrics(recovered, oracle)
    
    print(f"Metrics for {flight_id} (Model: {model_name}, H={horizon}):")
    print(f"Original Forecast - RMSE: {r_o:.2f}, MAE: {m_o:.2f}")
    print(f"ResidualNet Recovered - RMSE: {r_r:.2f}, MAE: {m_r:.2f}")
    print(f"Improvement - RMSE: {((r_o-r_r)/r_o*100):.2f}%, MAE: {((m_o-m_r)/m_o*100):.2f}%")

    # Plot
    plt.figure(figsize=(15, 6))
    plt.plot(plot_dates, oracle, label='Oracle Demand', color='black', alpha=0.6, linestyle='--')
    plt.plot(plot_dates, forecast, label=f'Forecasted ({model_name})', color='red', alpha=0.7)
    plt.plot(plot_dates, recovered, label='ResidualNet Recovered', color='blue', alpha=0.8)
    plt.title(f"Demand Comparison for {flight_id} (Test Set, {model_name} H{horizon})")
    plt.xlabel("Date")
    plt.ylabel("Demand (kg)")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    save_dir = os.path.join(current_dir, "results", "timeseries")
    os.makedirs(save_dir, exist_ok=True)
    plt.savefig(os.path.join(save_dir, f"TS_{flight_id}_{model_name}_H{horizon}.png"))
    plt.close()

if __name__ == "__main__":
    # If run from project root: python ResidualNet/visualize_timeseries.py
    models = ["Naive", "SARIMA", "Transformer"]
    horizons = [1, 7, 30]
    segments = ["Spot", "General", "Contract"]
    for m in models:
        for h in horizons:
            for s in segments:
                visualize_flight(m, h, f"PEK_LAX_FS1_{s}")
