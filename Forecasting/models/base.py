import numpy as np
from abc import ABC, abstractmethod

class BaseForecaster(ABC):
    """
    Abstract Base Class for all forecasting models.
    """
    def __init__(self, horizon=1):
        self.horizon = horizon
        self.history = None

    @abstractmethod
    def train(self, y, **kwargs):
        """
        Train the model on the provided time series data 'y'.
        """
        pass

    @abstractmethod
    def predict(self, steps=None):
        """
        Generate forecasts for the specified number of steps.
        """
        pass

    def evaluate(self, y_true, y_pred):
        """
        Basic evaluation helper (RMSE and MAE).
        """
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        min_len = min(len(y_true), len(y_pred))
        y_true, y_pred = y_true[:min_len], y_pred[:min_len]
        rmse = np.sqrt(np.mean((y_true - y_pred)**2))
        mae = np.mean(np.abs(y_true - y_pred))
        return {"RMSE": rmse, "MAE": mae}
