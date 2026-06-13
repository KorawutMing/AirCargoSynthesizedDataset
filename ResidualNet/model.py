import torch
import torch.nn as nn

class GlobalResidualPredictor(nn.Module):
    """
    Lightweight 2D U-Net optimized for small-sample RMSE reduction.
    """
    def __init__(self, in_channels, out_channels, extra_dim, hidden_dim=32):
        super(GlobalResidualPredictor, self).__init__()
        
        # 1. Encoder
        self.enc1 = nn.Sequential(
            nn.Conv2d(in_channels, hidden_dim, kernel_size=3, padding=1),
            nn.ReLU()
        )
        self.pool = nn.MaxPool2d(2) 
        
        # 2. Bottleneck with context
        self.bottleneck = nn.Sequential(
            nn.Conv2d(hidden_dim + extra_dim, hidden_dim * 2, kernel_size=3, padding=1),
            nn.ReLU()
        )
        
        # 3. Decoder
        self.upconv = nn.ConvTranspose2d(hidden_dim * 2, hidden_dim, kernel_size=2, stride=2)
        self.dec1 = nn.Sequential(
            nn.Conv2d(hidden_dim * 2, hidden_dim, kernel_size=3, padding=1), # Skip concat
            nn.ReLU(),
            nn.Conv2d(hidden_dim, out_channels, kernel_size=1)
        )
        
        # Zero-Init: Identity mapping start
        with torch.no_grad():
            self.dec1[-1].weight.fill_(0.0)
            self.dec1[-1].bias.fill_(0.0)

    def forward(self, x, mask, extras):
        # Encoder
        e1 = self.enc1(x)
        p1 = self.pool(e1)
        
        # Tile extras (DOW)
        # Dynamically match the pooled spatial dimensions
        H_p, W_p = p1.shape[2], p1.shape[3]
        e_tiled = extras.view(extras.size(0), extras.size(1), 1, 1).expand(-1, -1, H_p, W_p)
        bn = self.bottleneck(torch.cat([p1, e_tiled], dim=1))
        
        # Decoder
        up = self.upconv(bn)
        d1 = torch.cat([up, e1], dim=1) # Skip connection
        out = self.dec1(d1)
        
        # Masking: Last out_channels are the masks in input x
        active_mask = x[:, (x.size(1)//2):, :, :]
        return out * active_mask
