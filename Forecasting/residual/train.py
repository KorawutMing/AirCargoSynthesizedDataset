import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
from Forecasting.residual.data_manager import ResidualDataManager
from Forecasting.residual.model import GlobalResidualPredictor

def train_refiner(model_name, horizon, harvested_path="Forecasting/harvested_predictions.json"):
    print("="*50)
    print(f"TRAINING SPATIAL REFINER FOR: {model_name} (H={horizon})")
    print("="*50)
    
    dm = ResidualDataManager(harvested_path)
    X_raw, Y_raw, M, dates = dm.get_matrices(model_name, horizon)
    
    if len(X_raw) < 10:
        print(f"Insufficient data for {model_name} H={horizon}. Skipping.")
        return

    split_idx = int(len(X_raw) * 0.8)
    
    train_X_raw, test_X_raw = X_raw[:split_idx], X_raw[split_idx:]
    train_Y_raw, test_Y_raw = Y_raw[:split_idx], Y_raw[split_idx:]
    train_M, test_M = M[:split_idx], M[split_idx:]

    # --- NO DATA LEAK SCALING ---
    scaler_X = StandardScaler()
    scaler_Y = StandardScaler()
    
    train_X = scaler_X.fit_transform(train_X_raw)
    test_X = scaler_X.transform(test_X_raw) 
    
    train_Y = scaler_Y.fit_transform(train_Y_raw)
    test_Y = scaler_Y.transform(test_Y_raw)

    train_X_t = torch.FloatTensor(train_X)
    train_Y_t = torch.FloatTensor(train_Y)
    train_M_t = torch.FloatTensor(train_M)
    
    test_X_t = torch.FloatTensor(test_X)
    test_Y_t = torch.FloatTensor(test_Y)
    test_M_t = torch.FloatTensor(test_M)

    dataset = TensorDataset(train_X_t, train_Y_t, train_M_t)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    input_dim = X_raw.shape[1]
    model = GlobalResidualPredictor(n_flights=input_dim)
    
    criterion = nn.SmoothL1Loss() 
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    model.train()
    epochs = 200
    pbar = tqdm(range(epochs), desc=f"Training {model_name} H={horizon}")
    for epoch in pbar:
        epoch_loss = 0
        for batch_x, batch_y, batch_m in loader:
            optimizer.zero_grad()
            preds = model(batch_x, batch_m)
            loss = criterion(preds * batch_m, batch_y * batch_m)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        pbar.set_postfix(loss=f"{epoch_loss/len(loader):.6f}")

    model.eval()
    with torch.no_grad():
        refined_Y_scaled = model(test_X_t, test_M_t).numpy()
        refined_Y = scaler_Y.inverse_transform(refined_Y_scaled)
        refined_Y = refined_Y * test_M 
        
        actual_Y = test_Y_raw * test_M
        orig_X = test_X_raw * test_M

    def get_metrics(pred, true, mask):
        p = pred[mask > 0]
        t = true[mask > 0]
        mae = np.mean(np.abs(p - t))
        rmse = np.sqrt(np.mean((p - t)**2))
        wape = np.sum(np.abs(t - p)) / (np.sum(np.abs(t)) + 1e-9)
        return mae, rmse, wape

    mae_orig, rmse_orig, wape_orig = get_metrics(orig_X, actual_Y, test_M)
    mae_ref, rmse_ref, wape_ref = get_metrics(refined_Y, actual_Y, test_M)

    print(f"\n--- PERFORMANCE COMPARISON (Global Network) ---")
    print(f"{'Metric':<15} | {'Original':<15} | {'Spatial-Refined':<15} | {'Improvement':<15}")
    print("-" * 65)
    
    def print_row(label, orig, ref):
        imp = (orig - ref) / (orig + 1e-9) * 100
        print(f"{label:<15} | {orig:<15.2f} | {ref:<15.2f} | {imp:>15.2f}%")

    print_row("MAE", mae_orig, mae_ref)
    print_row("RMSE", rmse_orig, rmse_ref)
    print_row("WAPE", wape_orig, wape_ref)
    print("\n")

if __name__ == "__main__":
    for h in [1, 7, 30]:
        train_refiner("Transformer", h)
    for h in [1, 7, 30]:
        train_refiner("SARIMA", h)
