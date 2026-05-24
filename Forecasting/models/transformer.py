import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import DataLoader
from sklearn.preprocessing import StandardScaler
from .base import BaseForecaster
from ..utils.data import TimeSeriesDataset

class PositionalEncoding(nn.Module):
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
    def __init__(self, input_dim=1, d_model=64, nhead=4, num_layers=2, dim_feedforward=128, dropout=0.1, horizon=30):
        super(TransformerModel, self).__init__()
        self.embedding = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward, dropout)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)
        self.decoder = nn.Linear(d_model, horizon)
        self.horizon = horizon

    def forward(self, x):
        # x shape: [batch, window, input_dim]
        x = x.transpose(0, 1) # [seq_len, batch, dim]
        x = self.embedding(x)
        x = self.pos_encoder(x)
        output = self.transformer_encoder(x)
        last_state = output[-1]
        return self.decoder(last_state)

class TransformerForecaster(BaseForecaster):
    def __init__(self, window_size=60, horizon=30, d_model=64, nhead=4, 
                 num_layers=2, epochs=100, lr=0.001, batch_size=32, patience=10):
        super().__init__(horizon=horizon)
        self.window_size = window_size
        self.epochs = epochs
        self.lr = lr
        self.batch_size = batch_size
        self.patience = patience
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.model = TransformerModel(
            input_dim=1, d_model=d_model, nhead=nhead, 
            num_layers=num_layers, horizon=horizon
        ).to(self.device)
        self.scaler = StandardScaler()

    def train(self, y, **kwargs):
        y_raw = np.array(y).reshape(-1, 1)
        
        # Split into train/val for early stopping (e.g., 85/15)
        split_idx = int(len(y_raw) * 0.85)
        train_raw = y_raw[:split_idx]
        val_raw = y_raw[split_idx - self.window_size:] # overlap for windowing
        
        # DATA LEAK PREVENTION: Fit scaler ONLY on training data
        train_scaled = self.scaler.fit_transform(train_raw)
        val_scaled = self.scaler.transform(val_raw)
        
        train_dataset = TimeSeriesDataset(train_scaled, self.window_size, self.horizon)
        val_dataset = TimeSeriesDataset(val_scaled, self.window_size, self.horizon)
        
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size)
        
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        criterion = nn.MSELoss()
        
        best_val_loss = float('inf')
        epochs_no_improve = 0
        best_model_state = None

        for epoch in range(self.epochs):
            self.model.train()
            for x, y_batch in train_loader:
                x, y_batch = x.to(self.device), y_batch.to(self.device)
                optimizer.zero_grad()
                output = self.model(x)
                loss = criterion(output, y_batch)
                loss.backward()
                optimizer.step()
            
            self.model.eval()
            val_loss = 0
            with torch.no_grad():
                for x_val, y_val in val_loader:
                    x_val, y_val = x_val.to(self.device), y_val.to(self.device)
                    output_val = self.model(x_val)
                    val_loss += criterion(output_val, y_val).item()
            
            val_loss /= len(val_loader) if len(val_loader) > 0 else 1
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                epochs_no_improve = 0
                best_model_state = self.model.state_dict().copy()
            else:
                epochs_no_improve += 1
            
            if epochs_no_improve >= self.patience:
                break
        
        if best_model_state:
            self.model.load_state_dict(best_model_state)
            
        # For prediction, use the last window of the full training data
        self.last_window = self.scaler.transform(y_raw[-self.window_size:])

    def predict(self, steps=None, last_window=None):
        """
        Supports both single-window and batch-window inference.
        last_window can be [window_size] or [batch, window_size].
        """
        self.model.eval()
        with torch.no_grad():
            if last_window is not None:
                if last_window.ndim == 1:
                    # Single window
                    window_sc = self.scaler.transform(last_window.reshape(-1, 1))
                    x = torch.FloatTensor(window_sc).unsqueeze(0).to(self.device)
                else:
                    # Batch of windows [B, W]
                    # Reshape for scaler, then back
                    B, W = last_window.shape
                    flat_windows = last_window.reshape(-1, 1)
                    sc_flat = self.scaler.transform(flat_windows)
                    window_sc = sc_flat.reshape(B, W, 1)
                    x = torch.FloatTensor(window_sc).to(self.device)
            else:
                x = torch.FloatTensor(self.last_window).unsqueeze(0).to(self.device)
            
            output = self.model(x)
            # output is [B, Horizon]
            pred_scaled = output.cpu().numpy()
            
            # Inverse transform is tricky for batch, simpler to do manually or flat
            if pred_scaled.ndim == 1 or (pred_scaled.shape[0] == 1):
                return self.scaler.inverse_transform(pred_scaled.reshape(-1, 1)).flatten()[:steps]
            else:
                # Batch inverse transform
                B, H = pred_scaled.shape
                flat_pred = pred_scaled.reshape(-1, 1)
                inv_flat = self.scaler.inverse_transform(flat_pred)
                return inv_flat.reshape(B, H) # Returns [B, Horizon]
