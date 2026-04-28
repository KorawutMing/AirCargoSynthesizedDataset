# generator.py
import pandas as pd
import numpy as np
from config import CITIES, TRADE_LANES, AIRCRAFT_CAPACITY_KG, SCHEDULE_DESIGN_LOAD_FACTOR, SEGMENTS, MAX_SHIPMENT_SIZE_KG
from network import generate_base_network
from temporal import generate_temporal_dynamics
from booking_curves import generate_booking_curves

def map_trade_lane(origin, destination):
    """Helper function to find the right noise column for a city pair."""
    orig_macro = CITIES[origin]['macro_region']
    dest_macro = CITIES[destination]['macro_region']
    
    lane_info = TRADE_LANES.get((orig_macro, dest_macro))
    if lane_info:
        return f"Mult_{lane_info['name']}"
    return "Base_Mult" 

def generate_final_dataset(years=10):
    """
    The Core Engine: Merges network, temporal, and booking curve data.
    Simulates sequential daily arrivals and applies capacity spillage.
    """
    print("1. Generating Base Network...")
    df_routes = generate_base_network()
    
    print(f"2. Generating {years}-Year Temporal Dynamics...")
    df_time = generate_temporal_dynamics(years=years)
    
    print("3. Merging Network and Timeline (Cross Join)...")
    df_full = df_routes.merge(df_time, how='cross')
    
    print("4. Applying Trade Lane Coherence...")
    df_full['Lane_Column'] = df_full.apply(lambda x: map_trade_lane(x['Origin'], x['Destination']), axis=1)
    
    idx, cols = pd.factorize(df_full['Lane_Column'])
    df_full['Final_Multiplier'] = df_full.reindex(cols, axis=1).to_numpy()[np.arange(len(df_full)), idx]
    df_full['Total_Daily_Market_Demand'] = df_full['Base_Daily_Demand_KG'] * df_full['Final_Multiplier']
    
    print("5. Assigning Fixed Flight Schedules...")
    peak_demand = df_full.groupby(['Origin', 'Destination'])['Total_Daily_Market_Demand'].transform('max')
    target_capacity = AIRCRAFT_CAPACITY_KG * SCHEDULE_DESIGN_LOAD_FACTOR
    df_full['Scheduled_Flights'] = np.ceil(peak_demand / target_capacity).astype(int)
    df_full['True_Flight_Demand'] = df_full['Total_Daily_Market_Demand'] / df_full['Scheduled_Flights']
    
    # ---------------------------------------------------------
    # THE MISSING LINK: Integrating the 15-Day Booking Curves
    # ---------------------------------------------------------
    print("6. Simulating 15-Day Booking Arrivals & Truncation...")
    df_curves = generate_booking_curves()
    
    # Calculate a blended daily arrival percentage based on segment weights
    blended_arrivals = np.zeros(len(df_curves))
    for segment, params in SEGMENTS.items():
        blended_arrivals += df_curves[segment].values * params['weight']
        
    # Vectorized Outer Product: (Total Flights x 1) * (1 x 15 Days) = Matrix of daily new requests
    true_daily_arrivals = df_full['True_Flight_Demand'].values.reshape(-1, 1) * blended_arrivals.reshape(1, -1)
    
    # Cumulative sum to simulate Bookings-on-Hand growing over 15 days
    cum_true_demand = np.cumsum(true_daily_arrivals, axis=1)
    
    # ---------------------------------------------------------
    # NEW: Fuzzy Truncation (The Knapsack Effect)
    # ---------------------------------------------------------
    num_flights = len(df_full)
    
    # Generate random wasted space for every single flight
    wasted_space = np.random.randint(0, MAX_SHIPMENT_SIZE_KG, size=num_flights)
    
    # Calculate the exact cutoff limit for each flight (e.g., 99,450 instead of 100,000)
    flight_capacities = AIRCRAFT_CAPACITY_KG - wasted_space
    
    # Truncate at the fuzzy capacity limit. 
    # We use .reshape(-1, 1) to broadcast the flight-specific limits across all 15 days.
    cum_constrained_bookings = np.minimum(cum_true_demand, flight_capacities.reshape(-1, 1))
    
    # Save the final D-0 metrics
    df_full['Final_True_Demand'] = cum_true_demand[:, -1].round(0)
    df_full['Final_Constrained_Bookings'] = cum_constrained_bookings[:, -1].round(0)
    
    # A flight is censored if its true demand exceeded its specific fuzzy capacity
    df_full['Is_Censored'] = df_full['Final_True_Demand'] > flight_capacities
    
    # Append the 15-day constrained booking trajectory to the dataframe
    days_prior = df_curves.index.tolist()
    curve_cols = []
    for i, dp in enumerate(days_prior):
        col_name = f'BOH_DP{dp}' # Bookings-on-Hand at Days Prior (DP)
        df_full[col_name] = cum_constrained_bookings[:, i].round(0)
        curve_cols.append(col_name)
    
    # Clean up and order columns
    base_cols = [
        'Date', 'Origin', 'Destination', 'Scheduled_Flights', 
        'Final_True_Demand', 'Final_Constrained_Bookings', 'Is_Censored'
    ]
    
    df_final = df_full[base_cols + curve_cols].copy()
    
    print("Dataset Generation Complete!")
    return df_final

if __name__ == "__main__":
    df = generate_final_dataset(years=10)
    df.to_csv('./data/air_cargo_10yr_dataset.csv', index=False)
    
    print("\n--- Sample Output (Showing the 15-Day Booking Curve Build-up) ---")
    # Show a flight that was censored to prove the truncation works across the curve
    censored_sample = df[df['Is_Censored'] == True].head(1)
    display_cols = ['Origin', 'Destination', 'Final_True_Demand', 'BOH_DP10', 'BOH_DP5', 'BOH_DP2', 'BOH_DP1']
    print(censored_sample[display_cols].to_string(index=False))