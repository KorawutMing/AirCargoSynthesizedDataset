import torch
import torch.nn as nn

class GlobalResidualPredictor(nn.Module):
    """
    Global Network Residual Predictor.
    Inputs:
        - temporal_forecasts: (Batch, N_flights)
        - presence_mask: (Batch, N_flights) - 1 if flight exists, 0 otherwise
    Outputs:
        - predicted_residuals: (Batch, N_flights)
    """
    def __init__(self, n_flights, hidden_dim=512):
        super(GlobalResidualPredictor, self).__init__()
        
        # We concatenate forecasts and mask as inputs (Total dim = 2 * n_flights)
        self.encoder = nn.Sequential(
            nn.Linear(n_flights * 2, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, hidden_dim),
            nn.ReLU()
        )
        
        self.decoder = nn.Linear(hidden_dim, n_flights)
        
    def forward(self, forecasts, mask):
        # Flattened input
        x = torch.cat([forecasts, mask], dim=1)
        latent = self.encoder(x)
        residuals = self.decoder(latent)
        
        # Zero out residuals for non-existent flights via the mask
        return residuals * mask

def train_residual_step(model, optimizer, criterion, forecasts, masks, true_demand):
    """
    Single training step for the residual predictor.
    Goal: minimize |(forecasts + predicted_residuals) - true_demand|
    """
    model.train()
    optimizer.zero_grad()
    
    predicted_residuals = model(forecasts, masks)
    refined_forecasts = forecasts + predicted_residuals
    
    # We only calculate loss where flights actually exist (masks == 1)
    loss = criterion(refined_forecasts * masks, true_demand * masks)
    
    loss.backward()
    optimizer.step()
    
    return loss.item()
