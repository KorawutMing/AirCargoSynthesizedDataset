import numpy as np
import warnings
from statsmodels.tsa.arima.model import ARIMA
from .base import BaseForecaster

warnings.filterwarnings("ignore")

class ARIMAForecaster(BaseForecaster):
    """
    ARIMA Forecaster using statsmodels.
    Falls back to Naive forecasting if fitting fails.
    """
    def __init__(self, order=(1, 1, 1), horizon=30):
        super().__init__(horizon=horizon)
        self.order = order
        self.model_res = None
        self.last_val = 0

    def train(self, y, **kwargs):
        self.last_val = y[-1] if len(y) > 0 else 0
        try:
            model = ARIMA(y, order=self.order)
            self.model_res = model.fit()
        except Exception:
            self.model_res = None

    def predict(self, steps=None, new_history=None):
        n = steps or self.horizon
        if self.model_res is not None:
            try:
                if new_history is not None:
                    # Slide the model forward to the new origin without refitting
                    # This applies the same AR/MA coefficients to the new data
                    new_res = self.model_res.apply(new_history, refit=False)
                    forecast = new_res.forecast(steps=n)
                else:
                    forecast = self.model_res.forecast(steps=n)
                return np.array(forecast)
            except Exception:
                pass
        return np.full(n, self.last_val)

class SARIMAForecaster(BaseForecaster):
    """
    SARIMA Forecaster for seasonal patterns.
    """
    def __init__(self, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7), horizon=30):
        super().__init__(horizon=horizon)
        self.order = order
        self.seasonal_order = seasonal_order
        self.model_res = None
        self.last_val = 0

    def train(self, y, **kwargs):
        self.last_val = y[-1] if len(y) > 0 else 0
        try:
            # Using simple seasonal order for weekly seasonality (7)
            model = ARIMA(y, order=self.order, seasonal_order=self.seasonal_order)
            self.model_res = model.fit()
        except Exception:
            self.model_res = None

    def predict(self, steps=None, new_history=None):
        n = steps or self.horizon
        if self.model_res is not None:
            try:
                if new_history is not None:
                    # Slide the model forward to the new origin without refitting
                    # This applies the same AR/MA coefficients to the new data
                    new_res = self.model_res.apply(new_history, refit=False)
                    forecast = new_res.forecast(steps=n)
                else:
                    forecast = self.model_res.forecast(steps=n)
                return np.array(forecast)
            except Exception:
                pass
        return np.full(n, self.last_val)
