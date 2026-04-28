# config.py

# ==========================================
# 1. NETWORK NODES (Cities)
# ==========================================
# Added 'macro_region' to easily group routes into Trade Lanes.

CITIES = {
    # China (Macro: Asia)
    "PVG": {"name": "Shanghai", "region": "East_China", "macro_region": "Asia", "lat": 31.1443, "lon": 121.8083, "X": 100, "M": 60},
    "PEK": {"name": "Beijing", "region": "North_China", "macro_region": "Asia", "lat": 40.0801, "lon": 116.5846, "X": 50, "M": 80},
    "CAN": {"name": "Guangzhou", "region": "South_China", "macro_region": "Asia", "lat": 23.3924, "lon": 113.2988, "X": 90, "M": 50},
    "CGO": {"name": "Zhengzhou", "region": "Central_China", "macro_region": "Asia", "lat": 34.5197, "lon": 113.8408, "X": 85, "M": 20},
    
    # USA (Macro: US)
    "LAX": {"name": "Los Angeles", "region": "US_West", "macro_region": "US", "lat": 33.9416, "lon": -118.4085, "X": 30, "M": 100},
    "ORD": {"name": "Chicago", "region": "US_Midwest", "macro_region": "US", "lat": 41.9742, "lon": -87.9073, "X": 60, "M": 80},
    "JFK": {"name": "New York", "region": "US_East", "macro_region": "US", "lat": 40.6413, "lon": -73.7781, "X": 35, "M": 90},
    
    # Regional Hubs (Macro: Asia)
    "HKG": {"name": "Hong Kong", "region": "South_China", "macro_region": "Asia", "lat": 22.3080, "lon": 113.9185, "X": 95, "M": 95},
    "NRT": {"name": "Tokyo", "region": "East_Asia", "macro_region": "Asia", "lat": 35.7647, "lon": 140.3863, "X": 75, "M": 75},
    "SIN": {"name": "Singapore", "region": "SEA", "macro_region": "Asia", "lat": 1.3521, "lon": 103.8198, "X": 70, "M": 70}
}

# Gravity Model Parameters (Distance used only for mode share, not raw demand)
GRAVITY_K = 1.5      


# ==========================================
# 2. TRADE LANES (For Coherent Time-Series Noise)
# ==========================================
# Maps (Origin Macro, Destination Macro) to a Trade Lane.
# 'volatility' is the standard deviation for the shared daily macroeconomic noise.

TRADE_LANES = {
    ("Asia", "US"):   {"name": "Transpacific_Headhaul", "volatility": 0.15}, # High variance, e-commerce driven
    ("US", "Asia"):   {"name": "Transpacific_Backhaul", "volatility": 0.08}, # Steadier, industrial/agricultural driven
    ("Asia", "Asia"): {"name": "Intra_Asia",            "volatility": 0.10}, # Moderate variance, manufacturing supply chains
    ("US", "US"):     {"name": "US_Domestic",           "volatility": 0.05}  # Low variance baseline
}


# ==========================================
# 3. DEMAND SEGMENTS (Booking Curves)
# ==========================================
SEGMENTS = {
    # Shifts from very early (5.0, 1.5) to a more balanced S-curve
    "Contract":   {"alpha": 2.0, "beta": 1.5, "weight": 0.35}, 
    
    # Shifts from centered (3.0, 3.0) to late-leaning (resembles your Agent A)
    "General":    {"alpha": 1.5, "beta": 2.5, "weight": 0.30}, 
    
    # Keeps demand active in the final week
    "Perishable": {"alpha": 1.0, "beta": 3.0, "weight": 0.10}, 
    
    # Extreme late spike (resembles your Agent B / "hockey stick")
    "Express":    {"alpha": 0.5, "beta": 8.0, "weight": 0.15}, 
    
    # Keeps a baseline arrival rate until Day 0
    "Spot":       {"alpha": 1.0, "beta": 1.0, "weight": 0.10}  
}

BOOKING_WINDOW_DAYS = 15


# ==========================================
# 4. TEMPORAL DYNAMICS
# ==========================================
YOY_GROWTH_RATE = 1.03

MOY_MULTIPLIERS = {
    1: 0.90,  2: 0.75,  3: 0.95,  4: 1.00, 
    5: 1.00,  6: 1.05,  7: 1.00,  8: 1.05, 
    9: 1.15, 10: 1.30, 11: 1.45, 12: 1.25
}

DOW_MULTIPLIERS = {
    0: 1.10, # Mon
    1: 1.15, # Tue
    2: 1.20, # Wed 
    3: 1.15, # Thu
    4: 1.10, # Fri
    5: 0.70, # Sat 
    6: 0.60  # Sun 
}


# ==========================================
# 5. FLIGHT SCHEDULING & CAPACITY
# ==========================================
AIRCRAFT_CAPACITY_KG = 100000
SCHEDULE_DESIGN_LOAD_FACTOR = 1.7
MAX_SHIPMENT_SIZE_KG = 800