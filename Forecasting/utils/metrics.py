import numpy as np
from scipy.stats import pearsonr

def calculate_metrics(y_true, y_pred):
    """
    Standard suite of forecasting metrics.
    """
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    
    # Pearson correlation for trend capture
    if len(y_true) > 1 and np.std(y_true) > 0 and np.std(y_pred) > 0:
        corr, _ = pearsonr(y_true, y_pred)
    else:
        corr = 0.0
        
    bias = np.mean(y_pred - y_true)
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred)**2))
    wape = np.sum(np.abs(y_true - y_pred)) / np.sum(np.abs(y_true)) if np.sum(np.abs(y_true)) > 0 else 0
    
    return {
        "MAE": mae, 
        "RMSE": rmse, 
        "WAPE": wape,
        "Trend (Corr)": corr, 
        "Bias": bias
    }
