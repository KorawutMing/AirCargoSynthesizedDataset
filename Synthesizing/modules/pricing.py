# pricing.py
import numpy as np
from config import ESCALATION_PARAMS

def calculate_dynamic_prices(base_price, noise_index, segments_config, max_dp=15):
    """
    Generates a price matrix for a specific flight across all Days Prior (DP) and Segments.
    Formula: Price(DP) = BasePrice * (1 + gamma * e^(-theta * DP)) * Noise
    """
    prices = {}
    
    for segment in segments_config.keys():
        gamma = ESCALATION_PARAMS[segment]["gamma"]
        theta = ESCALATION_PARAMS[segment]["theta"]
        
        segment_prices = {}
        for dp in range(max_dp, 0, -1):
            # Calculate the escalation factor for this DP
            escalation = 1 + (gamma * np.exp(-theta * dp))
            
            # Apply base price and daily macroeconomic noise
            final_price = base_price * escalation * noise_index
            segment_prices[dp] = round(final_price, 2)
            
        prices[segment] = segment_prices
        
    return prices