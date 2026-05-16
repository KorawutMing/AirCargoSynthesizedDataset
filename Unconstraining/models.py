# Synthesis/unconstrainers.py
import numpy as np
from scipy.stats import norm
from abc import ABC, abstractmethod


class BaseUnconstrainer(ABC):
    def __init__(self):
        self.history = []

    @abstractmethod
    def fit(self, observed_bookings, is_censored, capacity):
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
            
            if abs(self.mu - prev_mu) < tol:
                break
                
        return y


class MARSSEMUnconstrainer(BaseUnconstrainer):
    """
    EM for 1D MARSS / Local Level State-Space model with censoring.
    """
    def __init__(self):
        super().__init__()
        self.B = None
        self.Z = None
        self.Q = None
        self.R = None
        self.mu_0 = None
        self.P0 = None

    def fit(self, observed_bookings, is_censored, capacity, price_per_kg=None, max_iter=100, tol=1e-4):
        y = np.asarray(observed_bookings, dtype=float)
        cens = np.asarray(is_censored, dtype=bool)
        T = len(y)

        var_y = max(np.var(y), 1.0)

        self.B = 1.0
        self.Z = 1.0
        self.Q = var_y * 0.10
        self.R = var_y * 0.25
        self.mu_0 = y[0]
        self.P0 = var_y

        loglik_prev = -np.inf

        for iteration in range(max_iter):
            x_pred = np.zeros(T)
            P_pred = np.zeros(T)
            x_filt = np.zeros(T)
            P_filt = np.zeros(T)
            expected_y = np.zeros(T)
            expected_yy = np.zeros(T)
            loglik = 0.0

            # ---------- Forward Kalman Filter ----------
            for t in range(T):
                if t == 0:
                    x_prior = self.B * self.mu_0
                    P_prior = self.B**2 * self.P0 + self.Q
                else:
                    x_prior = self.B * x_filt[t - 1]
                    P_prior = self.B**2 * P_filt[t - 1] + self.Q

                x_pred[t] = x_prior
                P_pred[t] = P_prior

                mu_y = self.Z * x_prior
                S = self.Z**2 * P_prior + self.R
                S = max(S, 1e-8)

                if not cens[t]:
                    obs = y[t]
                    K = P_prior * self.Z / S
                    x_post = x_prior + K * (obs - mu_y)
                    P_post = (1 - K * self.Z) * P_prior
                    expected_y[t] = obs
                    expected_yy[t] = obs**2
                    loglik += norm.logpdf(obs, loc=mu_y, scale=np.sqrt(S))

                else:
                    cap_t = capacity[t] if isinstance(capacity, np.ndarray) else capacity
                    a = (cap_t - mu_y) / np.sqrt(S)
                    a = np.clip(a, -5.0, 5.0) 

                    tail = max(1 - norm.cdf(a), 1e-12)
                    lam = norm.pdf(a) / tail

                    Ey = mu_y + np.sqrt(S) * lam
                    Vy = S * (1 + a * lam - lam**2)

                    K = P_prior * self.Z / S
                    x_post = x_prior + K * (Ey - mu_y)
                    P_post = (1 - K * self.Z) * P_prior

                    expected_y[t] = Ey
                    expected_yy[t] = Vy + Ey**2
                    loglik += np.log(tail)

                x_filt[t] = x_post
                P_filt[t] = max(P_post, 1e-8)

            # ---------- RTS Smoother ----------
            x_smooth = np.zeros(T)
            P_smooth = np.zeros(T)
            P_lag = np.zeros(T)

            x_smooth[-1] = x_filt[-1]
            P_smooth[-1] = P_filt[-1]

            for t in range(T - 2, -1, -1):
                J = P_filt[t] * self.B / max(P_pred[t + 1], 1e-8)
                x_smooth[t] = x_filt[t] + J * (x_smooth[t + 1] - x_pred[t + 1])
                P_smooth[t] = P_filt[t] + J**2 * (P_smooth[t + 1] - P_pred[t + 1])
                P_lag[t + 1] = J * P_smooth[t + 1]

            Ex = x_smooth
            Exx = P_smooth + x_smooth**2
            Exx_lag = np.zeros(T)
            for t in range(1, T):
                Exx_lag[t] = P_lag[t] + x_smooth[t] * x_smooth[t - 1]

            # ---------- M-STEP ----------
            self.B = 1.0

            q_sum = 0.0
            for t in range(1, T):
                q_sum += (Exx[t] - 2 * self.B * Exx_lag[t] + self.B**2 * Exx[t - 1])
            self.Q = max(q_sum / (T - 1), var_y * 0.01)

            r_sum = 0.0
            for t in range(T):
                r_sum += (expected_yy[t] - 2 * self.Z * expected_y[t] * Ex[t] + self.Z**2 * Exx[t])
            self.R = max(r_sum / T, 1e-8)

            self.mu_0 = Ex[0]
            self.P0 = max(P_smooth[0], 1e-8)

            self.history.append({"iter": iteration + 1, "B": self.B, "Q": self.Q, "R": self.R, "loglik": loglik})

            if abs(loglik - loglik_prev) < tol:
                break
            loglik_prev = loglik

        # ---------- FINAL IMPUTATION ----------
        final_imputed = y.copy()
        
        for t in range(T):
            if cens[t]:
                mu_s = self.Z * x_smooth[t]
                S_s = (self.Z**2 * P_smooth[t]) + self.R
                
                # BUG FIX: Extract scalar capacity here as well
                cap_t = capacity[t] if isinstance(capacity, np.ndarray) else capacity
                
                a = (cap_t - mu_s) / np.sqrt(S_s)
                a = np.clip(a, -5.0, 5.0)
                
                tail = max(1 - norm.cdf(a), 1e-12)
                lam = norm.pdf(a) / tail
                
                final_imputed[t] = mu_s + np.sqrt(S_s) * lam

        return final_imputed
    

# ==========================================================
# PRICE-AWARE UNCONSTRAINERS
# Add below your existing classes in unconstrainers.py
# ==========================================================

import numpy as np
from scipy.stats import norm

class MARSSXPriceUnconstrainer(BaseUnconstrainer):
    """
    Practical price-aware dynamic model.
    """
    def __init__(self):
        super().__init__()
        self.beta0 = None
        self.beta1 = None
        self.core_model = MARSSEMUnconstrainer()

    def fit(self, observed_bookings, is_censored, capacity, price_per_kg, max_iter=100, tol=1e-4):
        y = np.asarray(observed_bookings, dtype=float)
        cens = np.asarray(is_censored, dtype=bool)
        p = np.asarray(price_per_kg, dtype=float)

        # Handle scalar capacity
        if np.isscalar(capacity):
            cap_arr = np.full(len(y), capacity, dtype=float)
        else:
            cap_arr = np.asarray(capacity, dtype=float)

        # ---------- Estimate price relationship ----------
        mask = ~cens
        if np.sum(mask) < 3:
            mask = np.ones(len(y), dtype=bool)

        X = np.column_stack([np.ones(np.sum(mask)), p[mask]])
        beta = np.linalg.lstsq(X, y[mask], rcond=None)[0]

        self.beta0 = beta[0]
        self.beta1 = beta[1]

        price_component = self.beta0 + self.beta1 * p

        # Residual demand
        residual = y - price_component
        
        # BUG FIX: Convert capacity to residual space
        residual_capacity = cap_arr - price_component

        # Run MARSS on residual
        residual_est = self.core_model.fit(
            observed_bookings=residual,
            is_censored=cens,
            capacity=residual_capacity,  # <-- Pass the adjusted capacity here
            max_iter=max_iter,
            tol=tol
        )

        final_est = residual_est + price_component

        return final_est


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

                # BUG FIX: Circuit breaker to stop runaway OLS feedback loop.
                # Hard limit the estimation to 2x the flight's capacity
                max_allowed = cap[idx] * 2.0 
                y[idx] = np.minimum(imputed_values, max_allowed)

            # ---------- M STEP ----------
            # Robustness: Check for variance in p before full OLS
            if np.std(p) < 1e-6:
                self.beta0 = np.mean(y)
                self.beta1 = 0.0
            else:
                Xall = np.column_stack([np.ones(len(y)), p])
                beta = np.linalg.lstsq(Xall, y, rcond=None)[0]
                self.beta0 = beta[0]
                self.beta1 = beta[1]

            resid = y - (self.beta0 + self.beta1 * p)
            self.sigma = max(np.std(resid), 1.0)

            self.history.append({
                "iter": i + 1,
                "beta0": self.beta0,
                "beta1": self.beta1,
                "sigma": self.sigma
            })

            diff = abs(self.beta0 - prev_b0) + abs(self.beta1 - prev_b1)

            if diff < tol:
                break

        return y