import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# --- Markdown: Header ---
nb.cells.append(nbf.v4.new_markdown_cell("""# Synthesized Air Cargo Dataset: Exploratory Data Analysis
> **Abstract:** This notebook provides a comprehensive visualization and analysis of the synthesized 10-year air cargo dataset. We explore temporal demand patterns, network connectivity, booking curve dynamics, and price elasticity across five cargo segments (Contract, General, Perishable, Express, and Spot)."""))

# --- Code: Setup ---
setup_code = """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import os
import warnings
warnings.filterwarnings('ignore')

# ── Thesis-Quality Style ──────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":         "serif",
    "font.serif":          ["Times New Roman", "DejaVu Serif", "Georgia"],
    "font.size":           10,
    "axes.titlesize":      12,
    "axes.titleweight":    "bold",
    "axes.labelsize":      11,
    "axes.spines.top":     False,
    "axes.spines.right":   False,
    "grid.linestyle":      "--",
    "grid.alpha":          0.5,
    "figure.dpi":          150,
    "savefig.dpi":         300,
    "savefig.bbox":        "tight"
})

# Color Palette
PALETTE = ["#1a1a2e", "#c0392b", "#2e6da4", "#d35400", "#16a085"]
SEGMENTS = ['Contract', 'General', 'Perishable', 'Express', 'Spot']

# Load Dataset (5yr for speed in EDA)
DATA_PATH = os.path.join('..', 'data', 'air_cargo_5yr_dataset.csv')
if not os.path.exists(DATA_PATH): # Fallback for root execution
    DATA_PATH = 'data/air_cargo_5yr_dataset.csv'
df = pd.read_csv(DATA_PATH)
df['Date'] = pd.to_datetime(df['Date'])
print(f"Dataset Loaded: {len(df):,} rows.")"""
nb.cells.append(nbf.v4.new_code_cell(setup_code))

# --- Markdown: 1. Network Connectivity ---
nb.cells.append(nbf.v4.new_markdown_cell("""## 1 · Network Connectivity & Volume Distribution
Analysis of the 90 Origin-Destination pairs and their total cargo throughput."""))

network_code = """# Aggregate by OD
od_stats = df.groupby(['Origin', 'Destination'])['Final_True_Demand'].sum().reset_index()
pivot_od = od_stats.pivot(index='Origin', columns='Destination', values='Final_True_Demand') / 1e6 # in Millions

plt.figure(figsize=(10, 8))
sns.heatmap(pivot_od, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={'label': 'Total Demand (M kg)'})
plt.title("Air Cargo Network: Total Demand Throughput (10-Year Synthesis)")
plt.tight_layout()
plt.savefig("Synthesizing/network_heatmap.pdf")
plt.show()"""
nb.cells.append(nbf.v4.new_code_cell(network_code))

# --- Markdown: 2. Temporal Dynamics ---
nb.cells.append(nbf.v4.new_markdown_cell("""## 2 · Temporal Dynamics & Seasonality
Visualizing the 5-year demand trend with 30-day moving average and day-of-week distribution."""))

temporal_code = """# Global Trend
daily_demand = df.groupby('Date')['Final_True_Demand'].sum() / 1e3 # in Tonnes
ma30 = daily_demand.rolling(30).mean()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1]})

# Trend
ax1.plot(daily_demand.index, daily_demand, color=PALETTE[2], alpha=0.3, label='Daily Demand')
ax1.plot(ma30.index, ma30, color=PALETTE[1], linewidth=1.5, label='30-Day Moving Average')
ax1.set_title("Global Air Cargo Demand Trend")
ax1.set_ylabel("Demand (Tonnes)")
ax1.legend()

# Seasonality (Monthly)
df['Month'] = df['Date'].dt.month
sns.boxplot(data=df, x='Month', y='Final_True_Demand', ax=ax2, palette="vlag")
ax2.set_title("Monthly Demand Distribution (Seasonality)")
ax2.set_ylabel("Demand per Flight (kg)")

plt.tight_layout()
plt.savefig("Synthesizing/temporal_dynamics.pdf")
plt.show()"""
nb.cells.append(nbf.v4.new_code_cell(temporal_code))

# --- Markdown: 3. Booking Curves ---
nb.cells.append(nbf.v4.new_markdown_cell("""## 3 · Booking Curve Dynamics
Evolution of Bookings-on-Hand (BOH) across different lead times (Days Prior -15 to -1)."""))

booking_code = """# Extract BOH columns
boh_cols = [f'BOH_DP-{i}' for i in range(15, 0, -1)]
boh_data = df[boh_cols].mean()
boh_std = df[boh_cols].std()

plt.figure(figsize=(10, 6))
x = np.arange(-15, 0)
plt.plot(x, boh_data.values, marker='o', color=PALETTE[0], linewidth=2, label='Mean BOH')
plt.fill_between(x, boh_data.values - boh_std.values/2, boh_data.values + boh_std.values/2, 
                 color=PALETTE[0], alpha=0.1, label='Std Dev (0.5x)')

plt.title("Aggregate Booking Curve (System-wide)")
plt.xlabel("Days Prior to Departure")
plt.ylabel("Bookings on Hand (kg)")
plt.xticks(x)
plt.grid(True, axis='y')
plt.legend()
plt.tight_layout()
plt.savefig("Synthesizing/booking_curves.pdf")
plt.show()"""
nb.cells.append(nbf.v4.new_code_cell(booking_code))

# --- Markdown: 4. Segment Composition & Censorship ---
nb.cells.append(nbf.v4.new_markdown_cell("""## 4 · Segment Composition & Capacity Constraints
Distribution of demand by cargo type and analysis of censorship (spillage)."""))

segment_code = """# Segment Totals
segment_cols = [f'Oracle_{s}_kg' for s in SEGMENTS]
totals = df[segment_cols].sum()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Pie Chart
ax1.pie(totals, labels=SEGMENTS, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("viridis"))
ax1.set_title("Demand Composition by Segment")

# Censorship
censorship_rate = df['Is_Censored'].mean() * 100
sns.histplot(data=df, x='Final_True_Demand', hue='Is_Censored', bins=50, kde=True, ax=ax2, palette={True: PALETTE[1], False: PALETTE[2]})
ax2.set_title(f"Demand Distribution (Censorship Rate: {censorship_rate:.1f}%)")
ax2.set_xlabel("True Demand (kg)")

plt.tight_layout()
plt.savefig("Synthesizing/segment_censorship.pdf")
plt.show()"""
nb.cells.append(nbf.v4.new_code_cell(segment_code))

# --- Markdown: 5. Price Elasticity ---
nb.cells.append(nbf.v4.new_markdown_cell("""## 5 · Price-Demand Relationship
Analyzing how the Price Index correlates with demand realizations."""))

price_code = """# Sample for scatter to avoid overplotting
sample_df = df.sample(5000)

plt.figure(figsize=(10, 6))
sns.regplot(data=sample_df, x='Price_Index', y='Final_True_Demand', 
            scatter_kws={'alpha':0.1, 'color':PALETTE[2]}, line_kws={'color':PALETTE[1]})
plt.title("Price Elasticity: Price Index vs. True Demand")
plt.xlabel("Price Index (1.0 = Base)")
plt.ylabel("True Demand (kg)")
plt.tight_layout()
plt.savefig("Synthesizing/price_elasticity.pdf")
plt.show()"""
nb.cells.append(nbf.v4.new_code_cell(price_code))

# Save notebook
with open('Synthesizing/dataset_visualizer.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print("Notebook 'Synthesizing/dataset_visualizer.ipynb' updated successfully.")