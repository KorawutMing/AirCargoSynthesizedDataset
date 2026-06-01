import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# Add Synthesizing/modules to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), "Synthesizing", "modules"))
try:
    from config import AIRCRAFT_CAPACITY_KG, AIRCRAFT_CAPACITY_CBM
except ImportError:
    AIRCRAFT_CAPACITY_KG = 100000
    AIRCRAFT_CAPACITY_CBM = 600

def analyze_load_factors(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    print(f"Loading dataset: {file_path}...")
    df = pd.read_csv(file_path)

    # Calculate Load Factors
    # Note: We use the final constrained bookings which represent the actual loaded cargo
    df['LF_Weight'] = df['Final_Constrained_Bookings_KG'] / AIRCRAFT_CAPACITY_KG
    df['LF_Volume'] = df['Final_Constrained_Bookings_CBM'] / AIRCRAFT_CAPACITY_CBM

    # Basic Statistics
    stats = df[['LF_Weight', 'LF_Volume']].describe()
    print("\n--- Load Factor Statistics ---")
    print(stats)

    # Visualization
    plt.figure(figsize=(12, 6))

    # 1. Distribution Plot
    plt.subplot(1, 2, 1)
    sns.histplot(df['LF_Weight'], color='blue', label='Weight LF', kde=True, bins=30, alpha=0.5)
    sns.histplot(df['LF_Volume'], color='orange', label='Volume LF', kde=True, bins=30, alpha=0.5)
    plt.axvline(1.0, color='red', linestyle='--', label='Physical Limit')
    plt.title('Load Factor Distribution')
    plt.xlabel('Load Factor (Used / Capacity)')
    plt.ylabel('Frequency')
    plt.legend()

    # 2. Joint Scatter Plot (Weight vs Volume)
    plt.subplot(1, 2, 2)
    plt.scatter(df['LF_Weight'], df['LF_Volume'], alpha=0.1, s=1)
    plt.axvline(1.0, color='red', linestyle='--', alpha=0.5)
    plt.axhline(1.0, color='red', linestyle='--', alpha=0.5)
    plt.title('Weight LF vs Volume LF')
    plt.xlabel('Weight Load Factor')
    plt.ylabel('Volume Load Factor')
    
    # Identify bottleneck types for the title or annotations
    weigh_out = (df['Censored_By'] == 'Weight').sum()
    cube_out = (df['Censored_By'] == 'Volume').sum()
    total = len(df)
    
    plt.tight_layout()
    
    # Save the result
    output_fig = "data/load_factor_distribution.png"
    plt.savefig(output_fig)
    print(f"\nDistribution plot saved to: {output_fig}")
    
    print(f"\nSummary of Bottlenecks:")
    print(f"Total Flights: {total}")
    print(f"Weigh-out Flights: {weigh_out} ({weigh_out/total:.1%})")
    print(f"Cube-out Flights: {cube_out} ({cube_out/total:.1%})")

if __name__ == "__main__":
    # Target the new 5yr volumetric dataset
    target_file = "data/air_cargo_5yr_volumetric_dataset.csv"
    analyze_load_factors(target_file)
