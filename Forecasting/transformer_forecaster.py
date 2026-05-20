import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import DataLoader, Dataset
from sklearn.preprocessing import StandardScaler
from .base_models import BaseForecaster

class TimeSeriesDataset(Dataset):
    """
    Dataset for sliding-window time series forecasting.
    
    Args:
        data (np.ndarray): Scaled time series data.
        window_size (int): Number of historical lags to include.
        horizon (int): Forecasting horizon (lead time).
    """
    def __init__(self, data, window_size=60, horizon=30):
        self.data = torch.FloatTensor(data)
        self.window_size = window_size
        self.horizon = horizon

    def __len__(self):
        return len(self.data) - self.window_size - self.horizon + 1

    def __getitem__(self, idx):
        x = self.data[idx : idx + self.window_size]
        y = self.data[idx + self.window_size : idx + self.window_size + self.horizon]
        return x, y

class PositionalEncoding(nn.Module):
    """
    Implements sinusoidal positional encoding for sequence data.
    """
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:x.size(0), :]

class TransformerModel(nn.Module):
    """
    Transformer Encoder architecture for multi-horizon forecasting.
    
    Includes a learnable scaling layer to adjust signal magnitude.
    """
    def __init__(self, input_dim=1, d_model=64, nhead=4, num_layers=2, dim_feedforward=128, dropout=0.1, horizon=30):
        super(TransformerModel, self).__init__()
        self.embedding = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward, dropout)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)
        self.decoder = nn.Linear(d_model, horizon)
        
        # Learnable parameters for affine magnitude adjustment
        self.scale = nn.Parameter(torch.ones(1))
        self.bias = nn.Parameter(torch.zeros(1))
        
        self.horizon = horizon

    def forward(self, x):
        # x shape: [batch, window, input_dim]
        x = x.transpose(0, 1) # Transformer expects [seq_len, batch, dim]
        x = self.embedding(x)
        x = self.pos_encoder(x)
        output = self.transformer_encoder(x)
        
        # Use the latent representation of the final time step
        last_state = output[-1]
        out = self.decoder(last_state)
        
        # Affine transformation for magnitude scaling
        return out * self.scale + self.bias

class TransformerForecaster(BaseForecaster):
    """
    Academic implementation of a Transformer Forecaster for air cargo demand.
    
    Attributes:
        window_size (int): Lookback window.
        horizon (int): Forecast horizon.
        dampening_factor (float): Multiplicative factor to correct for volatility bias.
    """
    def __init__(self, window_size=60, horizon=30, d_model=64, nhead=4, 
                 num_layers=2, epochs=50, lr=0.001, batch_size=32, dampening_factor=0.75):
        super().__init__(horizon=horizon)
        self.window_size = window_size
        self.epochs = epochs
        self.lr = lr
        self.batch_size = batch_size
        self.dampening_factor = dampening_factor
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.model = TransformerModel(
            input_dim=1, d_model=d_model, nhead=nhead, 
            num_layers=num_layers, horizon=horizon
        ).to(self.device)
        self.scaler = StandardScaler()
        self.bias_correction = 0.0

    def train(self, y, **kwargs):
        """
        Trains the transformer model on univariate time series data.
        """
        y_raw = np.array(y).reshape(-1, 1)
        y_scaled = self.scaler.fit_transform(y_raw)
        
        dataset = TimeSeriesDataset(y_scaled, self.window_size, self.horizon)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        criterion = nn.MSELoss()
        
        self.model.train()
        for epoch in range(self.epochs):
            for x, y_batch in dataloader:
                x = x.to(self.device)
                y_batch = y_batch.to(self.device).squeeze(-1)
                
                optimizer.zero_grad()
                output = self.model(x)
                loss = criterion(output, y_batch)
                loss.backward()
                optimizer.step()
        
        # Empirical bias calculation for residual correction
        self.model.eval()
        with torch.no_grad():
            val_x = torch.FloatTensor(y_scaled[-self.window_size-self.horizon:-self.horizon]).unsqueeze(0).to(self.device)
            val_y_true = y_raw[-self.horizon:].flatten()
            val_pred_scaled = self.model(val_x).cpu().numpy().flatten()
            val_pred = self.scaler.inverse_transform(val_pred_scaled.reshape(-1, 1)).flatten()
            self.bias_correction = np.mean(val_y_true - val_pred)
        
        self.last_window = y_scaled[-self.window_size:]

    def predict(self, steps=None):
        """
        Generates out-of-sample multi-horizon forecasts.
        """
        self.model.eval()
        with torch.no_grad():
            x = torch.FloatTensor(self.last_window).unsqueeze(0).to(self.device)
            output = self.model(x)
            pred_scaled = output.cpu().numpy().flatten()
            pred = self.scaler.inverse_transform(pred_scaled.reshape(-1, 1)).flatten()
            
            # Application of bias correction and dampening factor
            final_pred = (pred + self.bias_correction) * self.dampening_factor
            return final_pred[:steps] if steps else final_pred
