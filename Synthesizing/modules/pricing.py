# pricing.py
from config import PRICING_DYNAMICS

def calculate_dynamic_prices(base_price, noise_index, segments_config, max_dp=15):
    """
    Calculates prices using: Final Base * Segment Premium * (Growth Constant ^ Days Elapsed)
    """
    prices = {}
    flight_daily_base = base_price * noise_index
    
    for segment in segments_config.keys():
        base_mult = PRICING_DYNAMICS[segment]["base_multiplier"]
        growth_rate = PRICING_DYNAMICS[segment]["daily_growth"]
        
        segment_prices = {}
        for dp in range(max_dp, 0, -1):
            # Days elapsed since the booking window opened (0 at DP=15, 14 at DP=1)
            days_elapsed = max_dp - dp 
            
            # Apply the growing constant
            current_price = flight_daily_base * base_mult * (growth_rate ** days_elapsed)
            segment_prices[dp] = round(current_price, 2)
            
        prices[segment] = segment_prices
        
    return prices