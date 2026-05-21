import torch
import numpy as np
from torch.utils.data import Dataset

class TimeSeriesDataset(Dataset):
    """
    PyTorch Dataset for sliding-window time series forecasting.
    
    Args:
        data (np.ndarray): Scaled time series data (shape: [N, 1] or [N]).
        window_size (int): Number of historical lags to include.
        horizon (int): Forecasting horizon (lead time).
    """
    def __init__(self, data, window_size=60, horizon=30):
        if len(data.shape) == 1:
            data = data.reshape(-1, 1)
        self.data = torch.FloatTensor(data)
        self.window_size = window_size
        self.horizon = horizon

    def __len__(self):
        return len(self.data) - self.window_size - self.horizon + 1

    def __getitem__(self, idx):
        x = self.data[idx : idx + self.window_size]
        y = self.data[idx + self.window_size : idx + self.window_size + self.horizon]
        return x, y.squeeze(-1)
