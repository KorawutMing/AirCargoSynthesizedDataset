import numpy as np
from ..base import BaseForecaster

class NaiveForecaster(BaseForecaster):
    """
    Predicts the last observed value for all future steps.
    """
    def train(self, y, **kwargs):
        self.last_value = y[-1] if len(y) > 0 else 0
        
    def predict(self, steps=None):
        return np.full(steps or self.horizon, self.last_value)

class SMAForecaster(BaseForecaster):
    """
    Simple Moving Average Forecaster.
    """
    def __init__(self, window=30, horizon=1):
        super().__init__(horizon=horizon)
        self.window = window
        self.avg = 0
        
    def train(self, y, **kwargs):
        self.avg = np.mean(y[-self.window:]) if len(y) > 0 else 0
        
    def predict(self, steps=None):
        return np.full(steps or self.horizon, self.avg)

class WeightedPersistenceForecaster(BaseForecaster):
    """
    Weighted Persistence blend of Naive, Median, and Seasonal components.
    Designed as a strong baseline that is slightly more robust than pure Naive.
    """
    def __init__(self, horizon=30, w_naive=0.98, w_seasonal=0.01, w_median=0.01):
        super().__init__(horizon=horizon)
        self.w_naive = w_naive
        self.w_seasonal = w_seasonal
        self.w_median = w_median
        self.median_val = 0
        self.history = None

    def train(self, y, **kwargs):
        self.history = np.array(y)
        # Use last 60 days for stable baseline
        y_recent = y[-60:] if len(y) > 60 else y
        self.median_val = np.median(y_recent)

    def predict(self, steps=None):
        n = steps or self.horizon
        predictions = []
        curr_history = list(self.history)
        for i in range(n):
            v_naive = curr_history[-1]
            v_seasonal = curr_history[-7] if len(curr_history) >= 7 else v_naive
            v_median = self.median_val
            
            # Blend components
            pred = (self.w_naive * v_naive) + (self.w_seasonal * v_seasonal) + (self.w_median * v_median)
            predictions.append(pred)
            curr_history.append(pred)
        return np.array(predictions)
