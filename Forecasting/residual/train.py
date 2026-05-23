import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
from Forecasting.residual.data_manager import ResidualDataManager
from Forecasting.residual.model import GlobalResidualPredictor
import json

def train_refiner(model_name, horizon, harvested_path="Forecasting/harvested_predictions.json"):
    dm = ResidualDataManager(harvested_path)
    X_raw, Y_raw, M_raw, E_raw, dates = dm.get_matrices(model_name, horizon)
    
    if len(X_raw) < 10:
        return None

    # Calculate raw residuals for training the U-Net
    Resid_raw = Y_raw - X_raw

    # Split
    split_idx = int(len(X_raw) * 0.8)
    tr_X_raw, te_X_raw = X_raw[:split_idx], X_raw[split_idx:]
    tr_Res_raw, te_Res_raw = Resid_raw[:split_idx], Resid_raw[split_idx:]
    tr_E_raw, te_E_raw = E_raw[:split_idx], E_raw[split_idx:]
    tr_M_raw, te_M_raw = M_raw[:split_idx], M_raw[split_idx:]
    te_Y_raw = Y_raw[split_idx:]

    # --- NO DATA LEAK SCALING ---
    sc_X, sc_R, sc_E = StandardScaler(), StandardScaler(), StandardScaler()
    tr_X_scaled = sc_X.fit_transform(tr_X_raw)
    te_X_scaled = sc_X.transform(te_X_raw)
    tr_Res_scaled = sc_R.fit_transform(tr_Res_raw)
    tr_E_scaled = sc_E.fit_transform(tr_E_raw)
    te_E_scaled = sc_E.transform(te_E_raw)

    # --- CONVERT TO 2D IMAGES ---
    tr_X_img = dm.build_image_tensors(tr_X_scaled, tr_M_raw)
    te_X_img = dm.build_image_tensors(te_X_scaled, te_M_raw)
    # Residual Target also becomes an 'Image' but with only Max_FS channels
    tr_Res_img = dm.build_image_tensors(tr_Res_scaled, tr_M_raw)[:, :dm.max_fs, :, :]

    # Convert to Tensors
    train_ds = TensorDataset(torch.FloatTensor(tr_X_img), torch.FloatTensor(tr_Res_img), 
                             torch.FloatTensor(tr_E_scaled))
    loader = DataLoader(train_ds, batch_size=32, shuffle=True)

    # U-Net Model Setup
    model = GlobalResidualPredictor(
        in_channels=dm.max_fs * 2, 
        out_channels=dm.max_fs,
        extra_dim=tr_E_scaled.shape[1]
    )
    
    optimizer = optim.Adam(model.parameters(), lr=0.0001, weight_decay=1e-3)
    criterion = nn.SmoothL1Loss()

    model.train()
    for epoch in tqdm(range(200), desc=f"Training U-Net {model_name} H={horizon}"):
        for bx_img, br_img, be in loader:
            optimizer.zero_grad()
            # U-Net takes: x_img, mask (not used separately in forward), and extras
            pred_r_img = model(bx_img, None, be)
            loss = criterion(pred_r_img, br_img)
            
            l1_lambda = 1e-4
            l1_norm = sum(p.abs().sum() for p in model.parameters())
            (loss + l1_lambda * l1_norm).backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        ref_R_img = model(torch.FloatTensor(te_X_img), None, torch.FloatTensor(te_E_scaled)).numpy()
        # Flatten image back to 180 vector
        ref_R_scaled = dm.flatten_image_prediction(ref_R_img)
        # Inverse Scale
        ref_R = sc_R.inverse_transform(ref_R_scaled)
        
        # Apply Refinement
        ref_Y = (te_X_raw + ref_R) * te_M_raw
        act_Y = te_Y_raw * te_M_raw
        orig_X = te_X_raw * te_M_raw

    def get_metrics(p, t, m):
        p, t = p[m > 0], t[m > 0]
        return np.mean(np.abs(p-t)), np.sqrt(np.mean((p-t)**2)), np.sum(np.abs(t-p))/(np.sum(np.abs(t))+1e-9)

    m_o, r_o, w_o = get_metrics(orig_X, act_Y, te_M_raw)
    m_r, r_r, w_r = get_metrics(ref_Y, act_Y, te_M_raw)
    
    return {
        "MAE": (float(m_o), float(m_r), float((m_o - m_r)/m_o*100)),
        "RMSE": (float(r_o), float(r_r), float((r_o - r_r)/r_o*100)),
        "WAPE": (float(w_o), float(w_r), float((w_o - w_r)/w_o*100))
    }

if __name__ == "__main__":
    with open("Forecasting/harvested_predictions.json", 'r') as f:
        data = json.load(f)
    models = sorted(list(set(r["Model"] for r in data)))
    horizons = [1, 7, 30]
    
    print(f"Starting Comprehensive U-Net Refinement for models: {models}")
    
    results = {}
    for m in models:
        results[m] = {}
        for h in horizons:
            print(f"Processing {m} (H={h})...")
            res = train_refiner(m, h)
            if res:
                results[m][str(h)] = res

    print("\n\n" + "="*80)
    print(f"{'Model':<15} | {'H':<3} | {'Metric':<6} | {'Original':<10} | {'Refined':<10} | {'Improvement':<12}")
    print("-" * 80)
    
    for m in models:
        for h in horizons:
            h_str = str(h)
            if h_str in results[m]:
                res = results[m][h_str]
                for metric in ["MAE", "WAPE"]:
                    orig, ref, imp = res[metric]
                    print(f"{m:<15} | {h:<3} | {metric:<6} | {orig:<10.2f} | {ref:<10.2f} | {imp:>10.2f}%")
        print("-" * 80)
        
    with open("Forecasting/spatial_refinement_results.json", "w") as f:
        json.dump(results, f, indent=4)
    print("\nResults saved to Forecasting/spatial_refinement_results.json")
