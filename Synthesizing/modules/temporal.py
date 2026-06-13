# temporal.py
import pandas as pd
import numpy as np
from config import MOY_MULTIPLIERS, DOW_MULTIPLIERS, YOY_GROWTH_RATE, TRADE_LANES

def generate_temporal_dynamics(years=10, start_date='2016-01-01'):
    """
    Generates a continuous daily time-series dataframe with calendar multipliers
    and Trade Lane specific noise vectors.
    """
    # 1. Generate the continuous date index
    end_date = pd.to_datetime(start_date) + pd.DateOffset(years=years) - pd.Timedelta(days=1)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    df_time = pd.DataFrame({'Date': dates})
    
    # 2. Map Calendar Multipliers
    df_time['DOW'] = df_time['Date'].dt.dayofweek
    df_time['MOY'] = df_time['Date'].dt.month
    
    base_dow = df_time['DOW'].map(DOW_MULTIPLIERS)
    base_moy = df_time['MOY'].map(MOY_MULTIPLIERS)
    
    # ---------------------------------------------------------
    # NEW: Stochastic Seasonality
    # ---------------------------------------------------------
    # DOW variance: +/- 5% on average (weekdays fluctuate slightly)
    dow_noise = np.random.normal(loc=1.0, scale=0.05, size=len(df_time))
    
    # MOY variance: +/- 8% on average (macro monthly trends have higher variance)
    moy_noise = np.random.normal(loc=1.0, scale=0.08, size=len(df_time))
    
    # Apply the noise to the base multipliers, clipping to prevent extreme outliers
    df_time['DOW_Mult'] = np.clip(base_dow * dow_noise, 0.5, 1.5)
    df_time['MOY_Mult'] = np.clip(base_moy * moy_noise, 0.5, 2.0)
    
    # 3. Calculate Year-over-Year (YoY) Compound Growth
    days_elapsed = (df_time['Date'] - df_time['Date'].min()).dt.days
    df_time['YoY_Mult'] = YOY_GROWTH_RATE ** (days_elapsed / 365.25)
    
    # Base multiplier now contains stochastic day-to-day and month-to-month jitter
    df_time['Base_Mult'] = df_time['DOW_Mult'] * df_time['MOY_Mult'] * df_time['YoY_Mult']
    
    # 4. Generate Trade Lane Coherence Vectors
    # Set a seed so your dataset is perfectly reproducible when you write your report
    np.random.seed(42) 
    
    for lane_tuple, lane_data in TRADE_LANES.items():
        lane_name = lane_data['name']
        volatility = lane_data['volatility']
        
        # Draw random noise using an AR(1) process to introduce autocorrelation
        # This allows Kalman filters to track the 'state' of demand better than static models.
        # x_t = phi * x_{t-1} + (1-phi) * mu + epsilon
        phi = 0.85 # Persistence factor (Increased for stronger regional trends)
        mu = 1.0
        
        lane_noise = np.zeros(len(df_time))
        lane_noise[0] = mu
        
        # Standard deviation of the innovation needed to maintain target volatility
        # sigma_eps = sigma_target * sqrt(1 - phi^2)
        innovation_std = volatility * np.sqrt(1 - phi**2)
        
        for t in range(1, len(df_time)):
            epsilon = np.random.normal(0, innovation_std)
            lane_noise[t] = phi * lane_noise[t-1] + (1 - phi) * mu + epsilon
            
        lane_noise = np.clip(lane_noise, 0.4, 2.5) 
        
        # The final multiplier for any flight in this lane on this specific day
        df_time[f'Mult_{lane_name}'] = df_time['Base_Mult'] * lane_noise

    # 5. Inject Localized Spatial Shocks
    df_time = inject_spatial_shocks(df_time)

    return df_time

def inject_spatial_shocks(df_time):
    """
    Introduces temporary demand surges or crashes for specific city clusters.
    These are invisible to univariate models but create clear spatial patterns.
    """
    regions = {
        'Asia_Export': ['PVG', 'CAN', 'HKG', 'CGO'],
        'US_West_Coast': ['LAX', 'ORD'],
        'US_East_Coast': ['JFK']
    }
    
    # Initialize shock columns
    for region in regions:
        df_time[f'Shock_{region}'] = 1.0
        
    num_days = len(df_time)
    # Roughly 4-5 shocks per year
    num_shocks = max(1, (num_days // 365) * 4)
    
    for _ in range(num_shocks):
        reg_name = np.random.choice(list(regions.keys()))
        duration = np.random.randint(7, 15)
        start_idx = np.random.randint(0, num_days - duration)
        
        # 70% chance of surge, 30% chance of crash
        is_surge = np.random.random() > 0.3
        intensity = np.random.uniform(1.5, 2.0) if is_surge else np.random.uniform(0.4, 0.6)
        
        df_time.loc[start_idx:start_idx+duration, f'Shock_{reg_name}'] = intensity
        
    return df_time

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    # Run the generator
    df_t = generate_temporal_dynamics(years=10)
    
    # Plot a 1-year slice (Year 9) to verify seasonality and noise visually
    year_slice = df_t[(df_t['Date'] >= '2024-01-01') & (df_t['Date'] <= '2024-12-31')]
    
    plt.figure(figsize=(14, 6))
    plt.plot(year_slice['Date'], year_slice['Mult_Transpacific_Headhaul'], label='Transpacific Headhaul (High Volatility)', alpha=0.8)
    plt.plot(year_slice['Date'], year_slice['Mult_US_Domestic'], label='US Domestic (Low Volatility)', alpha=0.8)
    
    # Overlay the smooth base multiplier to see the underlying MOY/DOW gravity
    plt.plot(year_slice['Date'], year_slice['Base_Mult'], label='Underlying Calendar Base', color='black', linewidth=2, linestyle='--')
    
    plt.title('Daily Demand Multipliers (1-Year Slice)', fontsize=16)
    plt.ylabel('Multiplier Value', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()