import torch
import torch.nn as nn
import torch.nn.functional as F

class UNetResidualPredictor(nn.Module):
    """
    2D U-Net for Spatial Residual Refinement.
    Input: (Batch, 2*Max_FS, H, W) 'Image'
    Extras: (Batch, E) Global context
    Output: (Batch, Max_FS, H, W) Residuals
    """
    def __init__(self, in_channels, out_channels, extra_dim, grid_size=(10, 10), hidden_dim=64):
        super(UNetResidualPredictor, self).__init__()
        self.H, self.W = grid_size
        
        # 1. Encoder
        self.enc1 = nn.Sequential(
            nn.Conv2d(in_channels, hidden_dim, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(hidden_dim)
        )
        self.pool = nn.MaxPool2d(2) # 10x10 -> 5x5
        
        # 2. Bottleneck with Extras
        # We tile extras and concat at the 5x5 level
        self.bottleneck = nn.Sequential(
            nn.Conv2d(hidden_dim + extra_dim, hidden_dim * 2, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(hidden_dim * 2)
        )
        
        # 3. Decoder
        self.upconv = nn.ConvTranspose2d(hidden_dim * 2, hidden_dim, kernel_size=2, stride=2)
        self.dec1 = nn.Sequential(
            nn.Conv2d(hidden_dim * 2, hidden_dim, kernel_size=3, padding=1), # Concat enc1
            nn.ReLU(),
            nn.Conv2d(hidden_dim, out_channels, kernel_size=1)
        )
        
        # --- ZERO INITIALIZATION ---
        with torch.no_grad():
            self.dec1[-1].weight.fill_(0.0)
            self.dec1[-1].bias.fill_(0.0)

    def forward(self, x, mask, extras):
        # x: (B, C, 10, 10)
        # extras: (B, E)
        
        # Encoder
        e1 = self.enc1(x)
        p1 = self.pool(e1) # (B, H, 5, 5)
        
        # Global Context Integration (Tiling)
        # (B, E) -> (B, E, 1, 1) -> (B, E, 5, 5)
        e_tiled = extras.view(extras.size(0), extras.size(1), 1, 1).expand(-1, -1, p1.size(2), p1.size(3))
        b_in = torch.cat([p1, e_tiled], dim=1)
        
        # Bottleneck
        bn = self.bottleneck(b_in)
        
        # Decoder
        up = self.upconv(bn) # (B, H, 10, 10)
        d1 = torch.cat([up, e1], dim=1) # Skip connection
        out = self.dec1(d1)
        
        # Apply mask to ensure only active flights have residuals
        # The mask is in the second half of the input channels
        # x is (B, 2*Max_FS, 10, 10), output is (B, Max_FS, 10, 10)
        active_mask = x[:, (x.size(1)//2):, :, :]
        return out * active_mask

class GlobalResidualPredictor(UNetResidualPredictor):
    # Wrapper to keep train.py imports working if needed
    pass
