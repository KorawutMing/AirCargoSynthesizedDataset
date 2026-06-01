import pandas as pd
import numpy as np
from tqdm import tqdm
from config import CITIES, TRADE_LANES, AIRCRAFT_CAPACITY_KG, AIRCRAFT_CAPACITY_CBM, SCHEDULE_DESIGN_LOAD_FACTOR, SEGMENTS, BOOKING_WINDOW_DAYS
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

def generate_final_dataset(years=10, target_load_factor=None, verbose=True):
    if target_load_factor is None:
        from config import SCHEDULE_DESIGN_LOAD_FACTOR
        target_load_factor = SCHEDULE_DESIGN_LOAD_FACTOR
        
    if verbose: print("1. Generating Base Network...")
    df_routes = generate_base_network()
    
    # Calculate Static Flight Schedule Once
    # target_load_factor controls how many flights we schedule for the base demand.
    # Higher factor -> fewer flights -> higher realized load factor.
    target_capacity = AIRCRAFT_CAPACITY_KG * target_load_factor
    df_routes['Scheduled_Flights'] = np.ceil(df_routes['Base_Daily_Demand_KG'] / target_capacity).astype(int)
    
    if verbose: print(f"2. Generating {years}-Year Temporal Dynamics...")
    df_time = generate_temporal_dynamics(years=years)
    
    if verbose: print("3. Merging Network and Timeline (Cross Join)...")
    df_full = df_routes.merge(df_time, how='cross')
    
    # Expand DataFrame to represent individual flights
    df_flights = df_full.loc[df_full.index.repeat(df_full['Scheduled_Flights'])].reset_index(drop=True)
    
    # Assign distinct flight numbers (e.g., Flight 1, Flight 2, Flight 3)
    df_flights['Flight_Sequence'] = df_flights.groupby(['Date', 'Origin', 'Destination']).cumcount() + 1
    
    if verbose: print("4. Calculating Base Economics...")
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
    
    if verbose: print("5. Running Discrete Transaction Engine...")
    df_curves = generate_booking_curves()
    simulation_results = []
    
    # Disable tqdm if not verbose
    iter_obj = df_flights.itertuples()
    if verbose:
        iter_obj = tqdm(iter_obj, total=len(df_flights), desc="Simulating Flights")

    for row in iter_obj:
        price_matrix = calculate_dynamic_prices(row.Base_Price_per_kg, row.Price_Index, SEGMENTS)
        
        flight_state, realized_log, latent_log = simulate_flight_booking_window(
            flight_id=f"{row.Origin}-{row.Destination}-{row.Flight_Sequence}-{row.Date.strftime('%Y%m%d')}",
            total_capacity_kg=AIRCRAFT_CAPACITY_KG,
            total_capacity_cbm=AIRCRAFT_CAPACITY_CBM,
            base_demand=row.True_Flight_Demand,
            temporal_mult=1.0, 
            price_matrix=price_matrix,
            price_index=row.Price_Index,
            booking_curves=df_curves,
            segments_config=SEGMENTS
        )
        
        # --- Aggregate the Transaction Logs into Flight Summaries ---
        
        # 1. Calculate Realized vs Latent by Segment (KG & CBM)
        segment_realized = {f"Observed_{seg}_kg": 0 for seg in SEGMENTS.keys()}
        segment_realized_cbm = {f"Observed_{seg}_cbm": 0 for seg in SEGMENTS.keys()}
        segment_latent = {f"Oracle_{seg}_kg": 0 for seg in SEGMENTS.keys()}
        segment_latent_cbm = {f"Oracle_{seg}_cbm": 0 for seg in SEGMENTS.keys()}
        
        for req in latent_log:
            segment_latent[f"Oracle_{req['segment']}_kg"] += req['weight']
            segment_latent_cbm[f"Oracle_{req['segment']}_cbm"] += req['volume']
            
        for req in realized_log:
            segment_realized[f"Observed_{req['segment']}_kg"] += req['weight']
            segment_realized_cbm[f"Observed_{req['segment']}_cbm"] += req['volume']
            
        # 2. Reconstruct the Bookings-on-Hand (BOH) Trajectory
        boh_trajectory = {}
        cumulative_weight = 0
        cumulative_volume = 0
        sorted_realized = sorted(realized_log, key=lambda x: x['dp'])
        
        request_idx = 0
        total_requests = len(sorted_realized)
        
        for dp in range(-BOOKING_WINDOW_DAYS, 0):
            while request_idx < total_requests and sorted_realized[request_idx]['dp'] == dp:
                cumulative_weight += sorted_realized[request_idx]['weight']
                cumulative_volume += sorted_realized[request_idx]['volume']
                request_idx += 1
            boh_trajectory[f'BOH_KG_DP{dp}'] = round(cumulative_weight, 0)
            boh_trajectory[f'BOH_CBM_DP{dp}'] = round(cumulative_volume, 1)

        price_trajectory = {}
        for seg in SEGMENTS.keys():
            for dp in range(-BOOKING_WINDOW_DAYS, 0):
                price_trajectory[f'Price_{seg}_DP{dp}'] = price_matrix[seg][dp]
            
        # 3. Compile the row 
        result_row = {
            'Index': row.Index,
            'Final_True_Demand_KG': round(sum(segment_latent.values()), 0),
            'Final_True_Demand_CBM': round(sum(segment_latent_cbm.values()), 1),
            'Final_Constrained_Bookings_KG': round(sum(segment_realized.values()), 0),
            'Final_Constrained_Bookings_CBM': round(sum(segment_realized_cbm.values()), 1),
            'Is_Censored': flight_state['is_censored'],
            'Censored_By': flight_state['censored_by'],
            'Days_Prior_Closed': flight_state['d_close']
        }
        
        # Merge dictionaries and append
        result_row.update(segment_realized)
        result_row.update(segment_realized_cbm)
        result_row.update(segment_latent)
        result_row.update(segment_latent_cbm)
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
        'Final_True_Demand_KG', 'Final_True_Demand_CBM',
        'Final_Constrained_Bookings_KG', 'Final_Constrained_Bookings_CBM',
        'Is_Censored', 'Censored_By', 'Days_Prior_Closed'
    ]
    
    # Safely generate the dynamic columns directly from the config keys
    seg_cols = [f"Observed_{seg}_kg" for seg in SEGMENTS.keys()] + \
               [f"Observed_{seg}_cbm" for seg in SEGMENTS.keys()] + \
               [f"Oracle_{seg}_kg" for seg in SEGMENTS.keys()] + \
               [f"Oracle_{seg}_cbm" for seg in SEGMENTS.keys()]
    
    curve_cols = [f'BOH_KG_DP{dp}' for dp in range(-BOOKING_WINDOW_DAYS, 0)] + \
                 [f'BOH_CBM_DP{dp}' for dp in range(-BOOKING_WINDOW_DAYS, 0)]
    
    price_cols = [f'Price_{seg}_DP{dp}' for seg in SEGMENTS.keys() for dp in range(-BOOKING_WINDOW_DAYS, 0)]
    
    df_final = df_final[base_cols + seg_cols + curve_cols + price_cols].copy()
    
    print("Dataset Generation Complete!")
    return df_final

if __name__ == "__main__":
    years = 5
    df = generate_final_dataset(years=years) 
    df.to_csv(f'./data/air_cargo_{years}yr_volumetric_dataset.csv', index=False)
    
    print("\n--- Summary of Generated Dataset ---")
    print(f"Total Flights Simulated: {len(df):,}")
    print(f"Censored Flights (Capacity Hit): {df['Is_Censored'].sum():,}")