import pandas as pd
import numpy as np
from tqdm import tqdm
from config import CITIES, TRADE_LANES, AIRCRAFT_CAPACITY_KG, SCHEDULE_DESIGN_LOAD_FACTOR, SEGMENTS
from network import generate_base_network
from temporal import generate_temporal_dynamics
from booking_curves import generate_booking_curves
from pricing import calculate_dynamic_prices
from simulation import simulate_flight_booking_window

def map_trade_lane(origin, destination):
    """Helper function to find the right noise column for a city pair."""
    orig_macro = CITIES[origin]['macro_region']
    dest_macro = CITIES[destination]['macro_region']
    
    lane_info = TRADE_LANES.get((orig_macro, dest_macro))
    if lane_info:
        return f"Mult_{lane_info['name']}"
    return "Base_Mult" 

def get_base_price(origin, destination):
    from config import BASE_PRICE_PER_KG
    o = CITIES[origin]['macro_region']
    d = CITIES[destination]['macro_region']
    return BASE_PRICE_PER_KG[(o, d)]

def generate_final_dataset(years=10):
    print("1. Generating Base Network...")
    df_routes = generate_base_network()
    
    # Calculate Static Flight Schedule Once
    target_capacity = AIRCRAFT_CAPACITY_KG * SCHEDULE_DESIGN_LOAD_FACTOR
    df_routes['Scheduled_Flights'] = np.ceil(df_routes['Base_Daily_Demand_KG'] / target_capacity).astype(int)
    
    print(f"2. Generating {years}-Year Temporal Dynamics...")
    df_time = generate_temporal_dynamics(years=years)
    
    print("3. Merging Network and Timeline (Cross Join)...")
    df_full = df_routes.merge(df_time, how='cross')
    
    # Expand DataFrame to represent individual flights
    df_flights = df_full.loc[df_full.index.repeat(df_full['Scheduled_Flights'])].reset_index(drop=True)
    
    # Assign distinct flight numbers (e.g., Flight 1, Flight 2, Flight 3)
    df_flights['Flight_Sequence'] = df_flights.groupby(['Date', 'Origin', 'Destination']).cumcount() + 1
    
    print("4. Calculating Base Economics...")
    # Apply Trade Lane Noise 
    df_flights['Lane_Column'] = df_flights.apply(lambda x: map_trade_lane(x['Origin'], x['Destination']), axis=1)
    idx, cols = pd.factorize(df_flights['Lane_Column'])
    df_flights['Final_Multiplier'] = df_flights.reindex(cols, axis=1).to_numpy()[np.arange(len(df_flights)), idx]
    
    # Apply Base Pricing and Volatility
    df_flights['Base_Price_per_kg'] = df_flights.apply(lambda x: get_base_price(x['Origin'], x['Destination']), axis=1)
    
    from config import PRICE_VOLATILITY
    df_flights['Price_Index'] = np.clip(np.random.normal(1.0, PRICE_VOLATILITY, len(df_flights)), 0.7, 1.5)
    
    # Calculate flight-specific demand 
    df_flights['True_Flight_Demand'] = (df_flights['Base_Daily_Demand_KG'] * df_flights['Final_Multiplier']) / df_flights['Scheduled_Flights']
    
    print("5. Running Discrete Transaction Engine...")
    df_curves = generate_booking_curves()
    simulation_results = []
    
    # Iterate over the explicitly expanded flight dataframe using tqdm for the progress bar
    for row in tqdm(df_flights.itertuples(), total=len(df_flights), desc="Simulating Flights"):
        price_matrix = calculate_dynamic_prices(row.Base_Price_per_kg, row.Price_Index, SEGMENTS)
        
        flight_state, realized_log, latent_log = simulate_flight_booking_window(
            flight_id=f"{row.Origin}-{row.Destination}-{row.Flight_Sequence}-{row.Date.strftime('%Y%m%d')}",
            total_capacity=AIRCRAFT_CAPACITY_KG,
            base_demand=row.True_Flight_Demand,
            temporal_mult=1.0, 
            price_matrix=price_matrix,
            booking_curves=df_curves,
            segments_config=SEGMENTS
        )
        
        # --- Aggregate the Transaction Logs into Flight Summaries ---
        
        # 1. Calculate Realized vs Latent by Segment
        segment_realized = {f"Observed_{seg}_kg": 0 for seg in SEGMENTS.keys()}
        segment_latent = {f"Oracle_{seg}_kg": 0 for seg in SEGMENTS.keys()}
        
        for req in latent_log:
            segment_latent[f"Oracle_{req['segment']}_kg"] += req['weight']
            
        for req in realized_log:
            segment_realized[f"Observed_{req['segment']}_kg"] += req['weight']
            
        # 2. Reconstruct the Bookings-on-Hand (BOH) Trajectory
        boh_trajectory = {}
        cumulative_weight = 0
        sorted_realized = sorted(realized_log, key=lambda x: x['dp'], reverse=True)
        
        request_idx = 0
        total_requests = len(sorted_realized)
        
        for dp in range(15, 0, -1):
            while request_idx < total_requests and sorted_realized[request_idx]['dp'] == dp:
                cumulative_weight += sorted_realized[request_idx]['weight']
                request_idx += 1
            boh_trajectory[f'BOH_DP{dp}'] = round(cumulative_weight, 0)

        price_trajectory = {}
        for seg in SEGMENTS.keys():
            for dp in range(15, 0, -1):
                price_trajectory[f'Price_{seg}_DP{dp}'] = price_matrix[seg][dp]
            
        # 3. Compile the row 
        result_row = {
            'Index': row.Index,
            'Final_True_Demand': round(sum(segment_latent.values()), 0),
            'Final_Constrained_Bookings': round(sum(segment_realized.values()), 0),
            'Is_Censored': flight_state['is_censored'],
            'Days_Prior_Closed': flight_state['d_close']
        }
        
        # Merge dictionaries and append
        result_row.update(segment_realized)
        result_row.update(segment_latent)
        result_row.update(boh_trajectory)
        result_row.update(price_trajectory)
        
        simulation_results.append(result_row)

    print("6. Merging and Formatting Final Dataset...")
    df_sim_results = pd.DataFrame(simulation_results)
    
    # Expose the index of df_flights as a column so we can merge on it
    df_flights['Index'] = df_flights.index
    
    # Merge the simulation aggregates back with df_flights
    df_final = df_flights.merge(df_sim_results, on='Index', how='left')
    
    # Define exact output schema
    base_cols = [
        'Date', 'Origin', 'Destination', 'Flight_Sequence', 'Scheduled_Flights',
        'Base_Price_per_kg', 'Price_Index', 
        'Final_True_Demand', 'Final_Constrained_Bookings',
        'Is_Censored', 'Days_Prior_Closed'
    ]
    
    # Safely generate the dynamic columns directly from the config keys
    seg_cols = [f"Observed_{seg}_kg" for seg in SEGMENTS.keys()] + \
               [f"Oracle_{seg}_kg" for seg in SEGMENTS.keys()]
    curve_cols = [f'BOH_DP{dp}' for dp in range(15, 0, -1)]
    price_cols = [f'Price_{seg}_DP{dp}' for seg in SEGMENTS.keys() for dp in range(15, 0, -1)]
    
    df_final = df_final[base_cols + seg_cols + curve_cols + price_cols].copy()
    
    print("Dataset Generation Complete!")
    return df_final

if __name__ == "__main__":
    df = generate_final_dataset(years=10) 
    df.to_csv('./data/air_cargo_10yr_dataset.csv', index=False)
    
    print("\n--- Summary of Generated Dataset ---")
    print(f"Total Flights Simulated: {len(df):,}")
    print(f"Censored Flights (Capacity Hit): {df['Is_Censored'].sum():,}")