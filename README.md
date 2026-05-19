# Air Cargo Synthesized Dataset & Demand Unconstraining Pipeline

This repository contains a comprehensive pipeline for generating, unconstraining, and forecasting synthetic air cargo booking data. This project is designed to simulate realistic air cargo networks, model capacity constraints, and evaluate advanced statistical and machine learning methods for recovering latent demand (unconstraining) and forecasting future demand.

## Project Structure

The project is divided into three primary modules, each handling a distinct phase of the air cargo demand modeling lifecycle:

### 1. Synthesizing (`/Synthesizing`)
This module generates realistic, multi-year synthetic air cargo booking data across a network of Origin-Destination (OD) pairs. It models complex dynamics such as:
*   **Temporal Seasonality:** Weekly and annual seasonality.
*   **Booking Curves:** Segment-specific booking build-up curves (e.g., Express vs. General cargo).
*   **Pricing Dynamics:** Price elasticity and temporal price variations.
*   **Network Effects:** Simulates capacity constraints and spill-over effects.

*Key Files:*
*   `modules/generator.py`, `modules/simulation.py`, `modules/pricing.py`, `modules/booking_curves.py`: Core logic for data generation.
*   `dataset_visualizer.ipynb`: Notebook for visualizing the generated booking curves and seasonality.

### 2. Unconstraining (`/Unconstraining`)
Air cargo historical data is often censored because bookings stop when physical capacity is reached. This module implements several advanced unconstraining algorithms to estimate the *true*, unconstrained demand from observed bookings.
*   **Naive Baseline:** Ignores capacity constraints.
*   **Expectation-Maximization (EM):** Standard and Price-dependent Truncated Normal EM models.
*   **Projection-Detruncation (PD):** A highly efficient alternative to EM, with both standard and price-dependent variants.

*Key Files:*
*   `models.py`: Numba-accelerated mathematical implementations of the unconstraining algorithms.
*   `batch_unconstrain.py`: High-performance parallelized script to run unconstraining across all OD pairs using a rolling time window to prevent data leakage.
*   `batch_results_new.ipynb`: Notebook for evaluating unconstraining performance (RMSE, MAE).

### 3. Forecasting (`/Forecasting`)
The final phase involves forecasting future cargo demand using the unconstrained data. This module evaluates different forecasting methodologies and compares the impact of using different unconstraining techniques (e.g., EM vs. Oracle true demand).

*Key Files:*
*   `batch_forecast.py`: Script for batch forecasting across the network.
*   Multiple Jupyter notebooks (`forecast_EMXPrice.ipynb`, `forecast_ORACLE.ipynb`, etc.) for analyzing the performance of different forecasting models and the impact of shocks.

## Data Storage
*   `/data`: Stores the raw generated CSV files (e.g., `air_cargo_5yr_dataset.csv`).
*   `/Unconstraining/unconstrained_results`: Stores the `.parquet` outputs of the unconstraining process, separated by OD pair.

## Getting Started

### Prerequisites
*   Python 3.8+
*   Required packages: `numpy`, `pandas`, `scipy`, `numba`, `scikit-learn`, `matplotlib`, `seaborn`, `tqdm`, `jupyter`.

### Workflow
1.  **Generate Data:** Run the synthesizing scripts (or notebooks) to create the base dataset in the `/data` folder.
2.  **Unconstrain Demand:** 
    ```bash
    cd Unconstraining
    python batch_unconstrain.py
    ```
    This will process the dataset and save the unconstrained estimates as Parquet files.
3.  **Analyze & Forecast:** Use the notebooks in `/Unconstraining` to evaluate the unconstraining accuracy, and the scripts/notebooks in `/Forecasting` to run demand predictions.

## Performance Notes
*   **Numba Acceleration:** The core Expectation-Maximization (EM) and Projection-Detruncation (PD) algorithms in `models.py` are heavily optimized using JIT compilation (`@njit(fastmath=True)`) to achieve C-like execution speeds.
*   **Parallel Processing:** The `batch_unconstrain.py` script leverages `ProcessPoolExecutor` to process multiple OD pairs concurrently, significantly reducing execution time on multi-core systems. Strict sliding window logic is implemented to ensure zero lookahead bias (data leakage).
