import torch
import torch.nn as nn

class GlobalResidualPredictor(nn.Module):
    def __init__(self, n_flights, extra_dim, hidden_dim=128): # Reduced hidden dim
        super(GlobalResidualPredictor, self).__init__()
        
        input_dim = (n_flights * 2) + extra_dim
        
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.4), # High dropout
            nn.Linear(hidden_dim, n_flights)
        )
        
        # --- ZERO INITIALIZATION ---
        # We initialize the final layer weights to almost zero.
        # This ensures the model starts by predicting a 0 residual (no change).
        with torch.no_grad():
            self.net[-1].weight.fill_(0.0)
            self.net[-1].bias.fill_(0.0)
        
    def forward(self, forecasts, mask, extras):
        x = torch.cat([forecasts, mask, extras], dim=1)
        delta = self.net(x)
        return delta * mask
