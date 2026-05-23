# Comprehensive Technical Report: Air Cargo Spatial-Temporal Demand Forecasting

## 1. Executive Summary
This project presents a multi-stage architecture designed to solve the problem of demand forecasting in constrained global logistics networks. By integrating **synthetic data simulation**, **advanced statistical unconstraining**, **walk-forward temporal forecasting**, and **2D convolutional spatial refinement**, we demonstrate a significant reduction in Root Mean Squared Error (RMSE) across a 180-route air cargo network.

The central thesis of this work is that **Spatial-Temporal Refinement** (ResidualNet) can correct for systemic biases in traditional time-series models by capturing regional demand correlations that standalone models ignore.

---

## 2. System Architecture & Methodology

### 2.1 Phase 1: Data Synthesis (`Synthesizing`)
To evaluate our models under known "Ground Truth," we implemented a high-fidelity transaction engine.
-   **Network Topology:** A 10-hub network with 180 unique Origin-Destination-FlightSequence routes.
-   **Temporal Dynamics:**
    -   Annual growth of 3%.
    -   Monthly seasonality (Q4 peak reaching 1.45x baseline).
    -   Weekly patterns (Tue-Wed peaks, weekend troughs).
-   **Transaction Engine:** 
    -   Simulates a 15-day booking window for every individual flight.
    -   Uses **Beta-distribution booking curves** for 5 customer segments (Contract, General, Perishable, Express, Spot).
    -   Implements **Log-Normal shipment sizes** and **Price Elasticity** (e.g., Spot elasticity of 1.45).
    -   Physical capacity constraints are strictly enforced, resulting in realistic "censored" data where demand exceeds aircraft limits.

### 2.2 Phase 2: Demand Unconstraining (`Unconstraining`)
Because air cargo historical data only records "bookings" (constrained) and not "demand" (latent), we implemented a recovery layer.
-   **Expectation-Maximization (EM):** Uses a truncated normal distribution to impute missing demand on days when the aircraft was full.
-   **Projection-Detruncation (PD):** A high-speed alternative using Acklam’s rational approximation for the inverse normal CDF.
-   **Price-Dependent Variants:** Models the mean demand as a function of daily spot price.
-   **Optimization:** Core loops are accelerated with **Numba (JIT compilation)**, achieving C-like performance and enabling parallel processing of 180 time-series in seconds.

### 2.3 Phase 3: Base Temporal Forecasting (`Forecasting`)
We established a diverse baseline using traditional and modern time-series models.
-   **Model Library:** Naive, SMA, Weighted Persistence, ARIMA, SARIMA (weekly seasonality), and a PyTorch-based Transformer.
-   **Validation Protocol:** A rigorous **20-fold walk-forward cross-validation** (`TimeSeriesSplit`).
-   **Execution:** Each model is trained on historical data and predicts horizons of 1, 7, and 30 days. The out-of-sample predictions are "harvested" to form the training set for the next phase.

### 2.4 Phase 4: Spatial-Temporal Refinement (`ResidualNet`)
The core innovation of the project is the **2D U-Net Residual Refiner**.
-   **Input Mapping:** 180 routes are mapped into a **10x10 matrix (Image)** representing the hub-and-spoke connectivity.
-   **Residual Learning:** Instead of predicting demand directly, the model learns the *residual* (Error = Actual - Forecast) of the base models.
-   **Local Maximum Guard:** A safety mechanism that clips forecast spikes to 2x the historical peak for each route, preventing catastrophic SARIMA/Transformer failures from polluting the network image.
-   **Zero-Initialization:** The final layer of the U-Net is initialized to zero, ensuring the model starts as an identity mapping and only adds corrections where they improve the loss.

---

## 3. Data Leakage Prevention Audit
Strict boundaries were maintained between "Past" and "Future" to ensure the validity of the results.

| Phase | Methodology | Leakage Prevention |
| :--- | :--- | :--- |
| **Unconstraining** | Rolling Window | Used `.shift(1)` to ensure share calculations used only prior data. |
| **Forecasting** | TimeSeriesSplit | Explicitly separated training and testing indices chronologically. |
| **Refinement** | Global Split | StandardScalers were fitted *only* on the training 80% portion. |
| **Guards** | Training Peaks | The Local Maximum Guard only "knows" peaks from the training set. |

---

## 4. Performance Results & Discussion

The implementation of the **Spatial-Temporal Refiner** achieved positive improvements across **all tested models** at the H=30 horizon.

### 4.1 Global Metrics (RMSE) - 30-Day Horizon
| Base Model | Original RMSE | Refined RMSE | Improvement (%) |
| :--- | :---: | :---: | :---: |
| **SARIMA** | 3957.58 | **3768.64** | **+4.77%** |
| **ARIMA** | 4393.83 | **3888.16** | **+11.51%** |
| **Transformer** | 4170.14 | **4124.31** | **+1.10%** |
| **Naive** | 5569.95 | **4344.60** | **+21.99%** |

### 4.2 Analysis of the "SARIMA + U-Net" SOTA
The study's most significant finding is that **SARIMA combined with U-Net refinement** (RMSE 3768) outperformed all other architectures, including the standalone Transformer. This suggests that for hierarchical logistics networks, a "Classical Temporal + Convolutional Spatial" hybrid is the optimal design choice.

### 4.3 The Role of the Local Maximum Guard
Before implementing the Guard, SARIMA and Transformer models often saw *negative* improvement due to occasional massive forecasting spikes. The Guard "rescued" these models by enforcing physical limits, allowing the U-Net to focus on learning subtle regional correlations rather than over-correcting for massive temporal errors.

---

## 5. Conclusions & Future Work
This project proves that the air cargo network's hub-and-spoke structure is a powerful feature that can be exploited using image-processing techniques (CNNs/U-Nets).

**Key Takeaways:**
1.  **Spatial Context Matters:** Errors in cargo forecasting are not random; they are spatially correlated across shared origins and destinations.
2.  **Hybridization is Key:** Deep learning is most effective when used as a "refinement layer" on top of established statistical baselines.
3.  **Stability over Sophistication:** Simple guards against extreme values are more critical to system-wide performance than complex model tuning.

**Future Research:**
-   **Dynamic Graph Kernels:** Moving from a static 10x10 grid to a dynamic Graph Neural Network (GNN) to handle flight cancellations and irregular schedules.
-   **Multimodal Refinement:** Integrating price signals directly into the U-Net as a secondary input channel to capture price-driven demand shifts.
-   **Auto-Tuning Clipping:** Making the Local Maximum Guard adaptive using attention mechanisms.
