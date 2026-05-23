# Air Cargo Synthesized Dataset: Execution Guide

This guide explains how to run the different modules of the Air Cargo Synthesized Dataset project in the correct order. **All commands should be executed from the project root directory.**

## Prerequisites
Ensure you have the required Python packages installed:
```bash
pip install pandas numpy torch scikit-learn tqdm matplotlib seaborn numba statsmodels pyarrow
```

Ensure your `PYTHONPATH` includes the current directory:
```bash
# Windows (PowerShell)
$env:PYTHONPATH = "."

# Linux / macOS
export PYTHONPATH=$PYTHONPATH:.
```

---

## 1. Synthesizing
Generates the synthetic 10-year air cargo dataset.
*   **Run:**
    ```bash
    python Synthesizing/modules/generator.py
    ```
*   **Output:** `data/air_cargo_10yr_dataset.csv`

---

## 2. Unconstraining
Implements demand unconstraining algorithms to estimate latent demand from constrained bookings.
*   **Run:**
    ```bash
    python Unconstraining/batch_unconstrain.py
    ```
*   **Output:** Parquet files in `Unconstraining/unconstrained_results/`.

---

## 3. Forecasting
Trains base forecasting models and generates out-of-sample predictions.
*   **Run:**
    ```bash
    python Forecasting/forecast.py
    ```
*   **Output:** 
    *   `Forecasting/results/harvested_predictions.json`
    *   `Forecasting/results/REPORT.md`

---

## 4. ResidualNet (Spatial Refinement)
Trains a 2D U-Net to refine base forecasts by capturing spatial correlations.
*   **Run:**
    ```bash
    python ResidualNet/train.py
    ```
*   **Output:**
    *   `ResidualNet/results/weights/`
    *   `ResidualNet/results/spatial_refinement_results.json`
    *   `ResidualNet/results/REPORT.md`

---

## 5. Visualization
Generates performance comparison plots for the spatial refinement.
*   **Run:**
    ```bash
    python ResidualNet/visualize_results.py
    ```
*   **Output:** `ResidualNet/results/spatial_refinement_comparison.png`
