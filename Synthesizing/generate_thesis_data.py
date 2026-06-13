import os
import sys
import pandas as pd

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))
from generator import generate_final_dataset

DATA_DIR = "data"
YEARS = 3
LF_TARGET = 0.80
DEMAND_MULT = 1.0

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print(f"Generating {YEARS}-year dataset with LF {LF_TARGET}...")
    
    df = generate_final_dataset(years=YEARS, target_load_factor=LF_TARGET, demand_multiplier=DEMAND_MULT, verbose=True)
    
    file_name = f"air_cargo_{YEARS}yr_LF_{int(LF_TARGET*100)}.csv"
    file_path = os.path.join(DATA_DIR, file_name)
    df.to_csv(file_path, index=False)
    
    print(f"\nDataset saved to {file_path}")
    print(f"Total rows: {len(df)}")
