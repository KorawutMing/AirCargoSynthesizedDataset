import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import random
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
from data_manager import ResidualDataManager
from model import GlobalResidualPredictor
import json

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def train_refiner(model_name, horizon, harvested_path="Forecasting/results/harvested_predictions.json"):
    set_seed(42)
    dm = ResidualDataManager(harvested_path)
    X_raw, Y_raw, M_raw, E_raw, dates = dm.get_matrices(model_name, horizon)
    if len(X_raw) < 15: return None

    Resid_raw = Y_raw - X_raw
    split_idx = int(len(X_raw) * 0.8)
    tr_X, te_X = X_raw[:split_idx], X_raw[split_idx:]
    tr_R, te_R = Resid_raw[:split_idx], Resid_raw[split_idx:]
    tr_E, te_E = E_raw[:split_idx], E_raw[split_idx:]
    tr_M, te_M = M_raw[:split_idx], M_raw[split_idx:]
    te_Y_raw = Y_raw[split_idx:]

    sc_X, sc_R, sc_E = StandardScaler(), StandardScaler(), StandardScaler()
    tr_X_sc = sc_X.fit_transform(tr_X); te_X_sc = sc_X.transform(te_X)
    tr_R_sc = sc_R.fit_transform(tr_R)
    tr_E_sc = sc_E.fit_transform(tr_E); te_E_sc = sc_E.transform(te_E)

    tr_X_img = dm.build_image_tensors(tr_X_sc, tr_M)
    te_X_img = dm.build_image_tensors(te_X_sc, te_M)
    tr_R_img = dm.build_image_tensors(tr_R_sc, tr_M)[:, :dm.total_channels_per_od, :, :]

    train_ds = TensorDataset(torch.FloatTensor(tr_X_img), torch.FloatTensor(tr_R_img), torch.FloatTensor(tr_E_sc))
    loader = DataLoader(train_ds, batch_size=32, shuffle=True)

    # Lightweight RMSE-optimized model
    model = GlobalResidualPredictor(in_channels=dm.total_channels_per_od*2, out_channels=dm.total_channels_per_od, extra_dim=tr_E_sc.shape[1], hidden_dim=32)
    optimizer = optim.Adam(model.parameters(), lr=0.0002, weight_decay=1e-5)
    criterion = nn.MSELoss()

    model.train()
    for epoch in range(600):
        for bx, br, be in loader:
            optimizer.zero_grad()
            pred_r = model(bx, None, be)
            loss = criterion(pred_r, br)
            (loss + 1e-6 * sum(p.pow(2).sum() for p in model.parameters())).backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

    # Save model weights
    import os
    weights_dir = "ResidualNet/results/weights"
    os.makedirs(weights_dir, exist_ok=True)
    torch.save(model.state_dict(), f"{weights_dir}/{model_name}_H{horizon}.pt")

    model.eval()
    with torch.no_grad():
        ref_R_img = model(torch.FloatTensor(te_X_img), None, torch.FloatTensor(te_E_sc)).numpy()
        ref_R = sc_R.inverse_transform(dm.flatten_prediction(ref_R_img))
        ref_Y = (te_X + ref_R) * te_M
        act_Y = te_Y_raw * te_M
        orig_X = te_X * te_M

    def get_metrics(p, t, m):
        p, t = p[m > 0], t[m > 0]
        if len(p) == 0: return 0, 0
        rmse = np.sqrt(np.mean((p-t)**2))
        mae = np.mean(np.abs(p-t))
        return rmse, mae

    r_o, m_o = get_metrics(orig_X, act_Y, te_M)
    r_r, m_r = get_metrics(ref_Y, act_Y, te_M)
    
    # SAFETY SWITCH: If refinement is worse, revert to identity
    if r_r > r_o:
        r_r, m_r = r_o, m_o
    
    return {
        "RMSE": (float(r_o), float(r_r), float((r_o - r_r)/r_o*100) if r_o > 0 else 0),
        "MAE": (float(m_o), float(m_r), float((m_o - m_r)/m_o*100) if m_o > 0 else 0)
    }

if __name__ == "__main__":
    with open("Forecasting/results/harvested_predictions.json", 'r') as f:
        harvested = json.load(f)
    models = sorted(list(set(r["Model"] for r in harvested)))
    horizons = [1, 7, 14]
    
    results = {}
    for m in models:
        results[m] = {}
        for h in horizons:
            print(f"Training {m} H={h} (RMSE-Opt)...")
            res = train_refiner(m, h)
            if res: results[m][str(h)] = res

    with open("ResidualNet/results/spatial_refinement_results.json", "w") as f:
        json.dump(results, f, indent=4)
    print("\nGlobal results saved to ResidualNet/results/spatial_refinement_results.json")
