# network.py
import math
import pandas as pd
from config import CITIES, GRAVITY_K

def calculate_haversine(lat1, lon1, lat2, lon2):
    """
    Calculates the great-circle distance between two points 
    on the Earth's surface using their latitude and longitude.
    """
    R = 6371.0  # Earth radius in kilometers
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def f(dist_km):
    return 1

def generate_base_network():
    """
    Calculates total market demand purely based on Export/Import power,
    then uses distance to calculate the Air Cargo Mode Share.
    """
    routes = []
    
    # Adjusted scaler since we removed the distance denominator
    # If PVG(100) * LAX(100) * 1.5 = 15,000. 
    # 15,000 * 20 = 300,000 kg (Perfect for our 100,000 kg capacity constraint)
    DEMAND_SCALER = 20 
    
    for orig_code, orig_data in CITIES.items():
        for dest_code, dest_data in CITIES.items():
            if orig_code == dest_code:
                continue
                
            dist_km = calculate_haversine(
                orig_data['lat'], orig_data['lon'],
                dest_data['lat'], dest_data['lon']
            )
            
            X_i = orig_data['X']
            M_j = dest_data['M']
            
            # 1. Pure Market Demand (No distance penalty)
            total_market_demand = GRAVITY_K * (X_i * M_j) * DEMAND_SCALER / f(dist_km)
            
            # 2. Air Cargo Mode Share (Distance as a routing/mode filter)
            if dist_km < 500:
                # e.g., CAN to HKG (Trucking wins completely)
                mode_share = 0.02 
            elif dist_km < 2000:
                # e.g., PEK to PVG (Mix of trucking, rail, and air)
                mode_share = 0.30 
            else:
                # e.g., PVG to LAX (Ocean takes a lot, but this represents the pure Air target market)
                mode_share = 1.0  
                
            final_air_demand_kg = total_market_demand * mode_share
            
            routes.append({
                'Origin': orig_code,
                'Destination': dest_code,
                'Distance_km': round(dist_km, 2),
                'Base_Daily_Demand_KG': round(final_air_demand_kg, 2)
            })
            
    df_routes = pd.DataFrame(routes)
    return df_routes

if __name__ == "__main__":
    # If you run this file directly, it will test the asymmetry
    df = generate_base_network()
    
    print("--- Asymmetry Check ---")
    pvg_lax = df[(df['Origin'] == 'PVG') & (df['Destination'] == 'LAX')]['Base_Daily_Demand_KG'].values[0]
    lax_pvg = df[(df['Origin'] == 'LAX') & (df['Destination'] == 'PVG')]['Base_Daily_Demand_KG'].values[0]
    
    print(f"Shanghai to LAX (Export Heavy): {pvg_lax:,.0f} kg")
    print(f"LAX to Shanghai (Backhaul):     {lax_pvg:,.0f} kg")

    print(df)