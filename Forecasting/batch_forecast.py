import os
import glob
import math
import warnings
import traceback
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import multiprocessing as mp
import concurrent.futures
from tqdm import tqdm

from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.svm import SVR
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tools.sm_exceptions import ConvergenceWarning

# Ignore warnings to keep the console clean during parallel processing
warnings.simplefilter('ignore', ConvergenceWarning)
warnings.simplefilter('ignore', UserWarning)

# ==========================================
# 1. TSFORMER ARCHITECTURE & HELPERS
# ==========================================
class SinusoidalPE(nn.Module):
    def __init__(self, d_model, max_len=200):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        pos = torch.arange(max_len).unsqueeze(1).float()
        div = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, : x.size(1)]

def causal_mask(sz, device):
    return torch.triu(torch.full((sz, sz), float("-inf"), device=device), diagonal=1)

def memory_mask(dec_len, enc_len, device):
    mask = torch.full((dec_len, enc_len), float("-inf"), device=device)
    for i in range(dec_len):
        allowed = i + (enc_len - dec_len)
        mask[i, : allowed + 1] = 0.0
    return mask

class Tsformer(nn.Module):
    def __init__(self, n_features, d_model, n_heads, n_enc, n_dec, ffn_dim, dropout, forecast_len):
        super().__init__()
        self.enc_input_fc = nn.Linear(n_features, d_model)
        self.dec_input_fc = nn.Linear(n_features, d_model)
        self.pe = SinusoidalPE(d_model)

        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=ffn_dim, 
            dropout=dropout, activation=F.elu, batch_first=True
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=n_enc)

        dec_layer = nn.TransformerDecoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=ffn_dim, 
            dropout=dropout, activation=F.elu, batch_first=True
        )
        self.decoder = nn.TransformerDecoder(dec_layer, num_layers=n_dec)
        self.fc_out = nn.Linear(d_model, 1)
        self.forecast_len = forecast_len

    def forward(self, src, tgt):
        src = self.pe(self.enc_input_fc(src))
        tgt = self.pe(self.dec_input_fc(tgt))

        B, S, _ = src.shape
        _, T, _ = tgt.shape

        src_mask = causal_mask(S, src.device)
        tgt_mask = causal_mask(T, tgt.device)
        mem_mask = memory_mask(T, S, src.device)

        memory = self.encoder(src, mask=src_mask)
        out = self.decoder(tgt, memory, tgt_mask=tgt_mask, memory_mask=mem_mask)

        pred = self.fc_out(out[:, -self.forecast_len:, :])
        return pred.squeeze(-1)

def build_tsformer_sequences(data, enc_len, dec_len, forecast_len):
    X_enc, X_dec, Y = [], []
    total = enc_len + forecast_len
    for i in range(len(data) - total + 1):
        enc_seq = data[i : i + enc_len]
        dec_known = data[i + enc_len - dec_len : i + enc_len]
        token = dec_known[-1].copy()
        token[0] = 0.0 # Mask demand, keep calendar features
        dec_seq = np.vstack([dec_known, token])
        target = data[i + enc_len : i + enc_len + forecast_len, 0]
        X_enc.append(enc_seq)
        X_dec.append(dec_seq)
        Y.append(target)
    return np.array(X_enc, dtype=np.float32), np.array(X_dec, dtype=np.float32), np.array(Y, dtype=np.float32)

# ==========================================
# 2. MODEL RUNNERS
# ==========================================
def run_arima(train, test):
    history = list(train)
    test_values = list(test)
    forecast_log = []
    
    for t in range(len(test_values)):
        model = ARIMA(history, order=(1, 1, 1))
        model_fit = model.fit()
        yhat = model_fit.forecast(steps=1)[0]
        forecast_log.append(yhat)
        history.append(test_values[t])
        
    forecast = np.exp(forecast_log) - 1
    actual = np.exp(test_values) - 1
    return np.sqrt(mean_squared_error(actual, forecast)), forecast

def run_sarima(train, test):
    history = list(train)
    test_values = list(test)
    forecast_log = []
    
    for t in range(len(test_values)):
        model = SARIMAX(history, order=(1, 1, 1), seasonal_order=(0, 1, 1, 7))
        model_fit = model.fit(disp=False)
        yhat = model_fit.forecast(steps=1)[0]
        forecast_log.append(yhat)
        history.append(test_values[t])
        
    forecast = np.exp(forecast_log) - 1
    actual = np.exp(test_values) - 1
    return np.sqrt(mean_squared_error(actual, forecast)), forecast

def forecast_component_with_exog(component_series, full_df, calendar_cols, start_idx, steps_to_forecast, lag, best_params):
    history = list(component_series.values)
    preds = []
    X_train_init, y_train_init = [], []
    
    for i in range(lag, len(history)):
        lags = history[i-lag:i]
        cal_features = full_df.iloc[i][calendar_cols].values.tolist()
        X_train_init.append(lags + cal_features)
        y_train_init.append(history[i])
        
    X_train_init = np.array(X_train_init)
    y_train_init = np.array(y_train_init)
    
    scaler_X = StandardScaler().fit(X_train_init)
    scaler_y = StandardScaler().fit(y_train_init.reshape(-1, 1))
    
    X_scaled = scaler_X.transform(X_train_init)
    y_scaled = scaler_y.transform(y_train_init.reshape(-1, 1)).ravel()
    
    model = SVR(kernel='rbf', **best_params)
    model.fit(X_scaled, y_scaled)
    
    current_test_idx = start_idx
    for _ in range(steps_to_forecast):
        last_lags = history[-lag:]
        future_cal_features = full_df.iloc[current_test_idx][calendar_cols].values.tolist()
        step_features = np.array(last_lags + future_cal_features).reshape(1, -1)
        
        last_scaled = scaler_X.transform(step_features)
        pred_scaled = model.predict(last_scaled)[0]
        pred = scaler_y.inverse_transform([[pred_scaled]])[0][0]
        
        preds.append(pred)
        history.append(pred)
        current_test_idx += 1
        
    return np.array(preds)

def run_sd_svr(df_raw, train_size):
    df_model = df_raw.copy()
    df_model['Date'] = pd.to_datetime(df_model['Date'])
    df_model['weekday'] = df_model['Date'].dt.weekday
    df_model['month'] = df_model['Date'].dt.month
    df_model['Log_Demand'] = np.log(df_model['Demand'] + 1)
    df_model = pd.get_dummies(df_model, columns=['weekday', 'month'], drop_first=True)
    
    decomp = seasonal_decompose(df_model['Log_Demand'].iloc[:train_size], model='additive', period=7, extrapolate_trend='freq')
    components = {'trend': decomp.trend, 'seasonal': decomp.seasonal, 'resid': decomp.resid}
    
    test_steps = len(df_model) - train_size
    calendar_cols = [c for c in df_model.columns if 'weekday_' in c or 'month_' in c]
    
    lags = {'trend': 14, 'seasonal': 7, 'resid': 3}
    default_svr_params = {'C': 10, 'gamma': 'scale', 'epsilon': 0.01}
    pred_components = {}
    
    for name, series in components.items():
        pred_components[name] = forecast_component_with_exog(
            series.dropna(), df_model, calendar_cols, train_size, test_steps, lags[name], default_svr_params
        )
        
    log_forecast = pred_components['trend'] + pred_components['seasonal'] + pred_components['resid']
    forecast = np.exp(log_forecast) - 1
    actual = df_model['Demand'].iloc[train_size:].values
    
    return np.sqrt(mean_squared_error(actual, forecast)), forecast

def run_tsformer(df_raw, train_size):
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    df = df_raw.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    
    scaler = MinMaxScaler()
    scaler.fit(df["Demand"].values[:train_size].reshape(-1, 1))
    passengers_scaled = scaler.transform(df["Demand"].values.reshape(-1, 1)).flatten()
    
    months_scaled = (df["Date"].dt.month.values - 1) / 11.0
    weekdays_scaled = df["Date"].dt.weekday.values / 6.0
    features = np.stack([passengers_scaled, months_scaled, weekdays_scaled], axis=1)
    
    ENCODER_LEN, DECODER_LEN, FORECAST_LEN = 12, 6, 1
    enc_inputs, dec_inputs, targets = build_tsformer_sequences(features, ENCODER_LEN, DECODER_LEN, FORECAST_LEN)
    
    split = train_size - ENCODER_LEN - FORECAST_LEN + 1
    enc_train, enc_test = enc_inputs[:split], enc_inputs[split:]
    dec_train, dec_test = dec_inputs[:split], dec_inputs[split:]
    y_train, y_test = targets[:split], targets[split:]
    
    enc_train_t = torch.tensor(enc_train).to(DEVICE)
    dec_train_t = torch.tensor(dec_train).to(DEVICE)
    y_train_t   = torch.tensor(y_train).to(DEVICE)
    enc_test_t  = torch.tensor(enc_test).to(DEVICE)
    dec_test_t  = torch.tensor(dec_test).to(DEVICE)
    
    model = Tsformer(
        n_features=3, d_model=16, n_heads=2, n_enc=1, n_dec=1, 
        ffn_dim=32, dropout=0.1, forecast_len=FORECAST_LEN
    ).to(DEVICE)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=3e-3)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=300)
    criterion = nn.MSELoss()
    
    model.train()
    for epoch in range(300):
        optimizer.zero_grad()
        pred = model(enc_train_t, dec_train_t)
        loss = criterion(pred, y_train_t)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        
    model.eval()
    with torch.no_grad():
        pred_scaled = model(enc_test_t, dec_test_t).cpu().numpy()
        
    pred_inv = scaler.inverse_transform(pred_scaled).flatten()
    true_inv = scaler.inverse_transform(y_test).flatten()
    rmse = np.sqrt(mean_squared_error(true_inv, pred_inv))
    
    # Clean up GPU memory so parallel workers don't crash the GPU
    del model, enc_train_t, dec_train_t, y_train_t, enc_test_t, dec_test_t
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        
    return rmse, pred_inv

# ==========================================
# 3. PARALLEL WORKER FUNCTION
# ==========================================
def process_od_pair(args):
    """ Worker function to process a single OD pair across all targets """
    origin, dest, df_raw, target_cols = args
    
    try:
        df = df_raw.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df = df[df['Date'] >= '2023-01-01'].sort_values('Date').reset_index(drop=True)
        
        train_size = int(len(df) * 0.8)
        
        # This will hold the timeseries forecasts for the parquet file
        test_dates = df['Date'].iloc[train_size:].reset_index(drop=True)
        forecast_df = pd.DataFrame({'Date': test_dates})
        
        # This will hold the benchmark RMSE metrics for this OD pair
        od_results = []
        
        # Loop through every unconstraining method + the Oracle
        for target_col in target_cols:
            if target_col not in df.columns:
                continue
                
            # Create isolated target dataframe
            df_target = pd.DataFrame({'Date': df['Date'], 'Demand': df[target_col]})
            
            df_log = np.log(df_target['Demand'] + 1)
            train_log, test_log = df_log.iloc[:train_size], df_log.iloc[train_size:]
            
            # 1. Run Models
            rmse_arima, pred_arima = run_arima(train_log, test_log)
            rmse_sarima, pred_sarima = run_sarima(train_log, test_log)
            rmse_svr, pred_svr = run_sd_svr(df_target, train_size)
            rmse_tsformer, pred_tsformer = run_tsformer(df_target, train_size)
            
            # 2. Append columns to the Parquet DataFrame
            # Format: TargetMethod_Actual and TargetMethod_ForecastingMethod
            forecast_df[f'{target_col}_Actual'] = df_target['Demand'].iloc[train_size:].reset_index(drop=True)
            forecast_df[f'{target_col}_ARIMA'] = pred_arima
            forecast_df[f'{target_col}_SARIMA'] = pred_sarima
            forecast_df[f'{target_col}_SD_SVR'] = pred_svr
            forecast_df[f'{target_col}_Tsformer'] = pred_tsformer
            
            # 3. Save metrics for the benchmark matrix
            od_results.append({
                'Origin': origin,
                'Destination': dest,
                'Target_Data': target_col,
                'ARIMA_RMSE': rmse_arima,
                'SARIMA_RMSE': rmse_sarima,
                'SD_SVR_RMSE': rmse_svr,
                'Tsformer_RMSE': rmse_tsformer,
                'Status': 'Success'
            })
            
        # Save 1 parquet file for the OD pair containing ALL targets and ALL forecasts
        parquet_path = f"forecast_results/{origin}_{dest}_forecasts.parquet"
        forecast_df.to_parquet(parquet_path, index=False)
        
        return od_results
        
    except Exception as e:
        error_msg = str(e) + "\n" + traceback.format_exc()
        return [{
            'Origin': origin,
            'Destination': dest,
            'Target_Data': 'Failed',
            'ARIMA_RMSE': np.nan,
            'SARIMA_RMSE': np.nan,
            'SD_SVR_RMSE': np.nan,
            'Tsformer_RMSE': np.nan,
            'Status': f'Failed: {error_msg}'
        }]

# ==========================================
# 4. MAIN EXECUTION
# ==========================================
if __name__ == '__main__':
    # Strictly required for PyTorch Multiprocessing
    mp.set_start_method('spawn', force=True)
    
    # Create directory for the time series visualizations
    os.makedirs("forecast_results", exist_ok=True)
    
    print("Loading data...")
    files = glob.glob("../Unconstraining/unconstrained_results/*.parquet")
    df_all = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    
    # Define ALL unconstraining columns + Oracle demand column
    # IMPORTANT: Change 'Oracle_Demand_Column_Name' to whatever your true/oracle column is named in the dataset.
    target_cols = [
        'Naive_Est', 'EM_Est', 'MARSS_Est', 'EMXPrice_Est', 'MARSSXPrice_Est', 'Final_True_Demand'
    ]
    
    # Drop rows where all the target estimates are NaN
    df_all = df_all.dropna(subset=[c for c in target_cols if c in df_all.columns], how='all').reset_index(drop=True)
    
    od_pairs = list(df_all[['Origin', 'Destination']].drop_duplicates().itertuples(index=False, name=None))
    
    tasks = []
    # Package the full dataframe and the list of targets to process for each OD pair
    for origin, dest in od_pairs:
        df_od = df_all[(df_all['Origin'] == origin) & (df_all['Destination'] == dest)].reset_index(drop=True)
        tasks.append((origin, dest, df_od, target_cols))
        
    # Set max workers to prevent CUDA out-of-memory errors. 
    # Because you are looping 6 targets per OD pair, the GPU memory clears after each target, 
    # but concurrent workers stack up memory usage.
    n_workers = max(mp.cpu_count(), 4) 
    print(f"Starting parallel evaluation across {len(tasks)} OD pairs using {n_workers} workers...")
    
    all_results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(process_od_pair, task) for task in tasks]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            # extend because process_od_pair now returns a list of dictionaries (1 per target method)
            all_results.extend(future.result()) 
            
    # Compile final matrix
    results_df = pd.DataFrame(all_results)
    
    print("\n================== FINAL BENCHMARK MATRIX ==================")
    print(results_df.drop(columns=['Status']).head(15).to_markdown(index=False))
    
    # Show any failures
    failures = results_df[results_df['Status'] != 'Success']
    if not failures.empty:
        print(f"\n[WARNING] {len(failures)} processing tasks failed. See Status column in the CSV for tracebacks.")
    
    # Save Benchmark Matrix to CSV
    results_df.to_csv("forecasting_benchmark_matrix.csv", index=False)
    print("Saved matrix to forecasting_benchmark_matrix.csv")
    print(f"Saved {len(od_pairs)} individual Parquet files to the 'forecast_results/' folder.")