# Synthesis/unconstrainers.py
import numpy as np
from scipy.stats import norm
from abc import ABC, abstractmethod


class BaseUnconstrainer(ABC):
    def __init__(self):
        self.history = []

    @abstractmethod
    def fit(self, observed_bookings, is_censored, capacity, **kwargs):
        pass

    def evaluate(self, true_demand, estimated_demand):
        rmse = np.sqrt(np.mean((true_demand - estimated_demand) ** 2))
        mae = np.mean(np.abs(true_demand - estimated_demand))
        return {"RMSE": round(rmse, 2), "MAE": round(mae, 2)}


class NaiveUnconstrainer(BaseUnconstrainer):
    """
    Baseline Model: Ignores the capacity constraint.
    Assumes observed bookings perfectly represent latent demand.
    """
    def fit(self, observed_bookings, is_censored, capacity=None, price_per_kg=None, max_iter=None, tol=None):
        # We simply return the observations. No "lift" is applied.
        y = observed_bookings.copy().astype(float)
        return y


class EMUnconstrainer(BaseUnconstrainer):
    """
    Expectation-Maximization Algorithm for Truncated Normal Distribution.
    Assumes demand is stationary (or has been pre-detrended/deseasonalized).
    """
    def __init__(self):
        super().__init__()
        self.mu = None
        self.sigma = None

    def fit(self, observed_bookings, is_censored, capacity, price_per_kg=None, max_iter=100, tol=1e-5):
        self.history.clear()

        y = observed_bookings.copy().astype(float)
        cens = np.asarray(is_censored, dtype=bool)
        
        # Format capacity as an array to handle discrete/fuzzy truncation
        if np.isscalar(capacity):
            cap_array = np.full_like(y, capacity)
        else:
            cap_array = np.asarray(capacity)

        # Initial guesses based on uncensored data (fallback to all data if heavily censored)
        if np.sum(~cens) > 0:
            self.mu = np.mean(y[~cens])
            self.sigma = max(np.std(y[~cens]), 1.0)
        else:
            self.mu = np.mean(y)
            self.sigma = max(np.std(y), 1.0)
        
        for i in range(max_iter):
            prev_mu = self.mu
            prev_sigma = self.sigma
            
            # --- E-STEP: Estimate latent demand for censored flights ---
            # Using the property of the Truncated Normal distribution
            a = (cap_array[cens] - self.mu) / self.sigma
            a = np.clip(a, -5.0, 5.0) # Numerical stability
            
            tail = np.clip(1 - norm.cdf(a), 1e-12, 1.0)
            lam = norm.pdf(a) / tail
            
            # Fill in the "hidden" data
            y[cens] = self.mu + self.sigma * lam
            
            # --- M-STEP: Maximize Likelihood (Update parameters) ---
            self.mu = np.mean(y)
            self.sigma = max(np.std(y), 1.0)
            
            self.history.append({'iter': i, 'mu': self.mu, 'sigma': self.sigma})
            
            diff = abs(self.mu - prev_mu) + abs(self.sigma - prev_sigma)
            if diff < tol:
                break
                
        return y

class EMPriceUnconstrainer(BaseUnconstrainer):
    """
    Truncated Normal EM with price-dependent mean.
    """
    def __init__(self):
        super().__init__()
        self.beta0 = None
        self.beta1 = None
        self.sigma = None

    def fit(self, observed_bookings, is_censored, capacity, price_per_kg, max_iter=100, tol=1e-5):
        self.history.clear()

        y = np.asarray(observed_bookings, dtype=float).copy()
        cens = np.asarray(is_censored, dtype=bool)
        p = np.asarray(price_per_kg, dtype=float)

        # Robustness: If all bookings are zero, return zeros
        if np.all(y == 0) and not np.any(cens):
            return y

        if np.isscalar(capacity):
            cap = np.full(len(y), capacity, dtype=float)
        else:
            cap = np.asarray(capacity, dtype=float)

        # ---------- Initial OLS using uncensored ----------
        mask = ~cens
        # Robustness: Ensure we have enough data and variance for OLS
        if np.sum(mask) < 2 or np.std(p[mask]) < 1e-6:
            # Fallback to mean if OLS is not possible
            self.beta0 = np.mean(y)
            self.beta1 = 0.0
        else:
            X = np.column_stack([np.ones(np.sum(mask)), p[mask]])
            beta = np.linalg.lstsq(X, y[mask], rcond=None)[0]
            self.beta0 = beta[0]
            self.beta1 = beta[1]

        self.sigma = max(np.std(y[mask]) if np.sum(mask) > 1 else 1.0, 1.0)

        for i in range(max_iter):
            prev_b0 = self.beta0
            prev_b1 = self.beta1
            prev_sigma = self.sigma

            mu = self.beta0 + self.beta1 * p

            # ---------- E STEP ----------
            idx = np.where(cens)[0]

            if len(idx) > 0:
                # Ensure sigma is not zero to avoid division by zero
                current_sigma = max(self.sigma, 1e-6)
                a = (cap[idx] - mu[idx]) / current_sigma
                a = np.clip(a, -5, 5)

                tail = np.clip(1 - norm.cdf(a), 1e-12, 1.0)
                lam = norm.pdf(a) / tail

                # Calculate imputation
                imputed_values = mu[idx] + current_sigma * lam

                # The circuit breaker is DELETED. 
                # Just assign the lifted values directly!
                y[idx] = imputed_values

            # ---------- M STEP ----------
            # Use the COMPLETE dataset (uncensored + imputed) to update parameters
            if len(y) > 2 and np.std(p) > 1e-6:
                X_all = np.column_stack([np.ones(len(y)), p])
                beta = np.linalg.lstsq(X_all, y, rcond=None)[0]
                self.beta0 = beta[0]
                self.beta1 = beta[1]
            else:
                self.beta0 = np.mean(y)
                self.beta1 = 0.0

            # The variance (sigma) can still be calculated on the whole dataset
            resid = y - (self.beta0 + self.beta1 * p)
            self.sigma = max(np.std(resid), 1.0)

            self.history.append({
                "iter": i + 1,
                "beta0": self.beta0,
                "beta1": self.beta1,
                "sigma": self.sigma
            })

            diff = abs(self.beta0 - prev_b0) + abs(self.beta1 - prev_b1) + abs(self.sigma - prev_sigma)
            if diff < tol:
                break

        return y
    
# ==========================================================
# PROJECTION-DETRUNCATION (PD) UNCONSTRAINERS
# ==========================================================

class PDUnconstrainer(BaseUnconstrainer):
    """
    Projection-Detruncation (PD) Algorithm for Truncated Normal Distribution.
    Replaces censored observations with a fixed fractile (controlled by tau)
    of the conditional tail distribution, rather than the expected value.
    """
    def __init__(self):
        super().__init__()
        self.mu = None
        self.sigma = None

    def fit(self, observed_bookings, is_censored, capacity, price_per_kg=None, tau=0.5, max_iter=100, tol=1e-5):
        self.history.clear()

        y = np.asarray(observed_bookings, dtype=float).copy()
        cens = np.asarray(is_censored, dtype=bool)

        if np.isscalar(capacity):
            cap = np.full(len(y), capacity, dtype=float)
        else:
            cap = np.asarray(capacity, dtype=float)

        # Step 0: Initialization using uncensored data
        mask = ~cens
        if np.sum(mask) > 0:
            self.mu = np.mean(y[mask])
            self.sigma = max(np.std(y[mask]), 1.0)
        else:
            self.mu = np.mean(y)
            self.sigma = max(np.std(y), 1.0)

        for i in range(max_iter):
            prev_mu = self.mu
            prev_sigma = self.sigma

            # --- Step 1: E-STEP (Projection) ---
            idx = np.where(cens)[0]
            if len(idx) > 0:
                current_sigma = max(self.sigma, 1e-6)
                
                # Standardize the booking limit
                a = (cap[idx] - self.mu) / current_sigma
                a = np.clip(a, -5.0, 5.0) 
                
                # Calculate P(Z > b_i)
                tail_prob = np.clip(1.0 - norm.cdf(a), 1e-12, 1.0)
                
                # Target probability for the substituted value: tau * P(Z > b_i)
                # Translated to CDF space: 1 - (tau * P(Z > b_i))
                target_cdf = np.clip(1.0 - (tau * tail_prob), 0.0, 1.0 - 1e-12)
                
                # Find the standardized Z value at this fractile using inverse CDF (ppf)
                z_hat_std = norm.ppf(target_cdf)
                
                # Unstandardize back to the booking scale and substitute
                y[idx] = self.mu + current_sigma * z_hat_std

            # --- Step 2: M-STEP (Detruncation) ---
            # Recalculate parameters using the combined (substituted + unconstrained) dataset
            self.mu = np.mean(y)
            self.sigma = max(np.std(y), 1.0)

            self.history.append({'iter': i + 1, 'mu': self.mu, 'sigma': self.sigma})

            # --- Step 3: Convergence Test ---
            diff = abs(self.mu - prev_mu) + abs(self.sigma - prev_sigma)
            if diff < tol:
                break

        return y


class PDPriceUnconstrainer(BaseUnconstrainer):
    """
    Projection-Detruncation (PD) method with price-dependent mean.
    """
    def __init__(self):
        super().__init__()
        self.beta0 = None
        self.beta1 = None
        self.sigma = None

    def fit(self, observed_bookings, is_censored, capacity, price_per_kg, tau=0.5, max_iter=100, tol=1e-5):
        self.history.clear()

        y = np.asarray(observed_bookings, dtype=float).copy()
        cens = np.asarray(is_censored, dtype=bool)
        p = np.asarray(price_per_kg, dtype=float)

        if np.all(y == 0) and not np.any(cens):
            return y

        if np.isscalar(capacity):
            cap = np.full(len(y), capacity, dtype=float)
        else:
            cap = np.asarray(capacity, dtype=float)

        # --- Step 0: Initialization ---
        mask = ~cens
        if np.sum(mask) < 2 or np.std(p[mask]) < 1e-6:
            self.beta0 = np.mean(y)
            self.beta1 = 0.0
        else:
            X = np.column_stack([np.ones(np.sum(mask)), p[mask]])
            beta = np.linalg.lstsq(X, y[mask], rcond=None)[0]
            self.beta0 = beta[0]
            self.beta1 = beta[1]

        self.sigma = max(np.std(y[mask]) if np.sum(mask) > 1 else 1.0, 1.0)

        for i in range(max_iter):
            prev_b0 = self.beta0
            prev_b1 = self.beta1
            prev_sigma = self.sigma

            # Calculate the current conditional mean for all observations
            mu = self.beta0 + self.beta1 * p

            # --- Step 1: E-STEP (Projection) ---
            idx = np.where(cens)[0]
            if len(idx) > 0:
                current_sigma = max(self.sigma, 1e-6)
                
                # Standardize using the conditional mean for each specific observation
                a = (cap[idx] - mu[idx]) / current_sigma
                a = np.clip(a, -5.0, 5.0)

                tail_prob = np.clip(1.0 - norm.cdf(a), 1e-12, 1.0)
                target_cdf = np.clip(1.0 - (tau * tail_prob), 0.0, 1.0 - 1e-12)
                z_hat_std = norm.ppf(target_cdf)

                # Unstandardize using conditional mean and substitute
                y[idx] = mu[idx] + current_sigma * z_hat_std

            # ---------- M STEP ----------
            # Use the COMPLETE dataset (uncensored + imputed) to update parameters
            if len(y) > 2 and np.std(p) > 1e-6:
                X_all = np.column_stack([np.ones(len(y)), p])
                beta = np.linalg.lstsq(X_all, y, rcond=None)[0]
                self.beta0 = beta[0]
                self.beta1 = beta[1]
            else:
                self.beta0 = np.mean(y)
                self.beta1 = 0.0

            # Variance is computed on the entire dataset (including PD substitutions)
            resid = y - (self.beta0 + self.beta1 * p)
            self.sigma = max(np.std(resid), 1.0)

            self.history.append({
                "iter": i + 1,
                "beta0": self.beta0,
                "beta1": self.beta1,
                "sigma": self.sigma
            })

            # --- Step 3: Convergence Test ---
            diff = abs(self.beta0 - prev_b0) + abs(self.beta1 - prev_b1) + abs(self.sigma - prev_sigma)
            if diff < tol:
                break

        return y