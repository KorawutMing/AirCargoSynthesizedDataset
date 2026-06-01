import os
import sys
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))
from generator import generate_final_dataset

DATA_DIR = "data/varied_lf_datasets"
YEARS = 5
LF_TARGETS = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]

def run_simulation(target_lf):
    """Worker function for parallel simulation."""
    # Run the generator with the specific target load factor
    df = generate_final_dataset(years=YEARS, target_load_factor=target_lf, verbose=False)
    
    # Save the result
    file_name = f"air_cargo_{YEARS}yr_LF_{int(target_lf*100)}.csv"
    file_path = os.path.join(DATA_DIR, file_name)
    df.to_csv(file_path, index=False)
    
    return f"LF {target_lf} Complete -> {file_name}"

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print(f"Starting batch generation for {len(LF_TARGETS)} load factor targets...")
    print(f"Directory: {DATA_DIR}")
    
    # Use parallel processing to speed up the 5-year simulations
    workers = min(len(LF_TARGETS), os.cpu_count() - 2)
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(run_simulation, lf): lf for lf in LF_TARGETS}
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Batch Generation"):
            try:
                result = future.result()
                print(result)
            except Exception as e:
                lf = futures[future]
                print(f"LF {lf} failed: {e}")

    print("\nBatch Generation Finished!")
