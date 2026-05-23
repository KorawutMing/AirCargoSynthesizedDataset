# Air Cargo Synthesized Dataset & Demand Unconstraining Pipeline

This repository contains a comprehensive pipeline for generating, unconstraining, and forecasting synthetic air cargo booking data. This project is designed to simulate realistic air cargo networks, model capacity constraints, and evaluate advanced statistical and machine learning methods for recovering latent demand (unconstraining) and forecasting future demand with spatial-temporal refinement.

## Project Structure

The project is divided into four primary modules, each handling a distinct phase of the air cargo demand modeling lifecycle:

### 1. Synthesizing (`/Synthesizing`)
This module generates realistic, multi-year synthetic air cargo booking data across a network of Origin-Destination (OD) pairs. It models complex dynamics such as temporal seasonality, segment-specific booking curves, and pricing dynamics.

### 2. Unconstraining (`/Unconstraining`)
Implements advanced unconstraining algorithms (EM, PD, Price-dependent variants) to estimate true, unconstrained demand from censored historical observations.

### 3. Forecasting (`/Forecasting`)
Trains base forecasting models (ARIMA, SARIMA, Transformer, etc.) and generates out-of-sample predictions. It serves as the baseline for the spatial refinement phase.

### 4. ResidualNet (`/ResidualNet`)
The final phase involves a **Spatial-Temporal Refiner** using a 2D U-Net. It flattens the network into an OD Matrix "Image" and uses convolutional filters to capture regional correlations and systematic residuals, significantly improving baseline forecasting accuracy.

## Data Storage
*   `/data`: Stores the raw generated CSV files (e.g., `air_cargo_10yr_dataset.csv`).
*   `/Unconstraining/unconstrained_results`: Stores the Parquet outputs of the unconstraining process.
*   `/Forecasting/results`: Stores base forecasting reports and JSON predictions.
*   `/ResidualNet/results`: Stores the refined metrics, comparison plots, and trained model weights.

## Getting Started

### Prerequisites
Refer to the `RUN_GUIDE.md` for detailed installation and execution instructions.

### Workflow Overview
1.  **Generate Data:** Run the synthesizing scripts to create the base dataset.
2.  **Unconstrain Demand:** Process the dataset to estimate latent demand.
3.  **Base Forecasting:** Generate out-of-sample forecasts across all models and horizons.
4.  **Spatial Refinement:** Train the ResidualNet U-Net to refine the base forecasts.

## Performance Notes
*   **Numba Acceleration:** Core unconstraining algorithms are JIT-compiled for C-like execution speeds.
*   **Spatial Intelligence:** The ResidualNet module uses the hub-and-spoke topology of the network as a structural prior to reduce forecasting error.
*   **Zero Leakage:** Strict chronological splits and sliding window logic are enforced across all modules to ensure zero lookahead bias.

For detailed execution commands, please see [RUN_GUIDE.md](./RUN_GUIDE.md).
