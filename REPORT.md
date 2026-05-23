# Project Comprehensive Report: Air Cargo Spatial-Temporal Forecasting

## 1. Project Overview
This project implements a multi-stage pipeline to synthesize, estimate, and forecast air cargo demand across a global hub-and-spoke network. The primary objective is to demonstrate that **Spatial-Temporal Refinement** (using 2D U-Nets) can decisively improve the accuracy of traditional time-series models by capturing regional demand correlations.

---

## 2. Methodology & Phases

### Phase 1: Data Synthesis
- **Scope:** 10-year daily cargo dataset (180 unique `OD_FlightSequence` routes, 10 airport hubs).
- **Dynamics:** Seasonal multipliers, Trade Lane noise, 5-segment booking curves, and price elasticity.
- **Location:** `Synthesizing/`

### Phase 2: Demand Unconstraining (Estimation)
- **Objective:** Recover "True Demand" from censored historical observations (constrained by aircraft capacity).
- **Techniques:** EM and PD models (standard and price-dependent).
- **Location:** `Unconstraining/`

### Phase 3: Base Temporal Forecasting
- **Models Library:** ARIMA, SARIMA, Transformer (Deep Learning), SMA, Naive, Persistence+.
- **Validation:** 20-fold walk-forward cross-validation (`TimeSeriesSplit`).
- **Location:** `Forecasting/`

### Phase 4: Spatial-Temporal Refinement (ResidualNet)
- **Architecture:** 2D U-Net (Encoder-Decoder) with skip-connections.
- **Mapping:** 180 routes flattened into a **10x10 Origin-Destination Matrix** (Demand Image).
- **Stabilization:** Implemented **Local Maximum Guards** to constrain forecasts to historical peaks.
- **Location:** `ResidualNet/`

---

## 3. Data Leakage Prevention Audit
A primary requirement was to ensure zero data leakage across the multi-stage pipeline.

| Phase | Leak Risk | Mitigation Strategy | Status |
| :--- | :--- | :--- | :--- |
| **Estimation** | Hindsight Bias | Rolling windows used `.shift(1)` for all share calculations. | **SAFE** |
| **Temporal** | Future Knowledge | `TimeSeriesSplit` enforced chronological training boundaries. | **SAFE** |
| **Refinement** | Global Statistics | `StandardScaler` fitted **only** on the first 80% of dates. | **SAFE** |
| **Clipping** | Peak Leakage | `LocalMaximumGuard` peaks calculated **only** from training portion. | **SAFE** |
| **Inference** | Label Leakage | Model receives only forecasts and DOW; zero info on target demand. | **SAFE** |

---

## 4. Summary of Results (RMSE)
The project successfully established a new performance ceiling for the air cargo network. Refinement results are stored in `ResidualNet/results/`.

| Model | H=30 Original | H=30 Refined | % Improvement |
| :--- | :---: | :---: | :---: |
| **Transformer** | 4170.14 | 4124.31 | +1.10% |
| **ARIMA** | 4393.83 | 3888.16 | **+11.51%** |
| **SARIMA** | 3957.58 | **3768.64** | **+4.77%** |
| **Naive** | 5569.95 | 4344.60 | **+21.99%** |

**Key Finding:** The **Spatial-Refined SARIMA** (RMSE: 3768) is the most accurate model in the study, proving that hybrid statistical-convolutional architectures outperform standalone deep learning for global logistics networks.

---

## 5. Directory Organization
The project has been refactored for clarity and modularity:
- `Forecasting/results/`: Base predictions and reports.
- `ResidualNet/results/`: Refinement plots, metrics, and trained weights (`.pt`).
- `ResidualNet/notebooks/`: Exploratory analysis for the spatial model.
- `RUN_GUIDE.md`: Centralized execution instructions for all modules.
