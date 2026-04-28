# booking_curves.py
import numpy as np
import pandas as pd
from scipy.stats import beta
from config import SEGMENTS, BOOKING_WINDOW_DAYS

def generate_booking_curves():
    """
    Generates the daily arrival percentages for each demand segment 
    over the 15-day booking window using Beta distributions.
    """
    # Create an array of time points from 0 to 1 representing the 15-day window.
    # We need BOOKING_WINDOW_DAYS + 1 points to create 15 discrete intervals (days).
    time_points = np.linspace(0, 1, BOOKING_WINDOW_DAYS + 1)
    
    curves_dict = {}
    
    for segment, params in SEGMENTS.items():
        a = params['alpha']
        b = params['beta']
        
        # 1. Calculate the Cumulative Distribution Function (CDF)
        cdf_values = beta.cdf(time_points, a, b)
        
        # 2. Calculate the Daily Arrivals (Probability Density)
        # The percentage of cargo arriving on a specific day is the difference 
        # in the CDF from the start of the day to the end of the day.
        daily_arrivals = np.diff(cdf_values)
        
        # Ensure it sums to exactly 1.0 (correcting for microscopic floating point errors)
        daily_arrivals = daily_arrivals / daily_arrivals.sum()
        
        curves_dict[segment] = daily_arrivals
        
    # Build the DataFrame
    df_curves = pd.DataFrame(curves_dict)
    
    # Add a 'Days_Prior' column counting down from 15 to 1
    df_curves['Days_Prior'] = list(range(BOOKING_WINDOW_DAYS, 0, -1))
    
    # Set it as the index for clean merging later
    df_curves = df_curves.set_index('Days_Prior')
    
    return df_curves

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    df_curves = generate_booking_curves()
    
    # 1. Print the table to verify percentages sum to 1.0 down the columns
    print("--- Daily Arrival Percentages ---")
    print(df_curves.round(3))
    print("\nCheck Sums (Should be 1.0):")
    print(df_curves.sum())
    
    # 2. Plot the Cumulative Booking Curves
    df_cumulative = df_curves.iloc[::-1].cumsum().iloc[::-1] # Reverse, cumsum, reverse back
    
    plt.figure(figsize=(12, 7))
    
    # Plot each segment
    for col in df_curves.columns:
        plt.plot(df_cumulative.index, df_cumulative[col], marker='o', linewidth=2, label=col)
        
    plt.title('Cumulative Booking Curves by Segment (15-Day Window)', fontsize=16)
    plt.xlabel('Days Prior to Departure', fontsize=12)
    plt.ylabel('Cumulative % of Segment Booked', fontsize=12)
    plt.xlim(15, 1) # Reverse X-axis to count down to departure
    plt.grid(True, alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.show()