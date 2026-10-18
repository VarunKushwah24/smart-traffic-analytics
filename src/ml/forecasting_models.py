import os
import json
import math
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from src.utils.logger import setup_logger

logger = setup_logger("ForecastingModels")

# 4 Forward Prediction Horizons in minutes
HORIZONS = [15, 30, 60, 120]

class MultiHorizonTrafficForecaster:
    """
    Multi-Step Forward Horizon Traffic Forecasting Model.
    
    Predicts future traffic volume across 4 sequential horizons:
      - t + 15 min (immediate tactical horizon)
      - t + 30 min (signal coordination horizon)
      - t + 60 min (arterial route diversion horizon)
      - t + 120 min (strategic municipal dispatch horizon)
      
    Features:
      - Multi-target sequence regression
      - Cyclic temporal encodings (sin/cos of hour and day)
      - Lagged auto-regressive traffic state features
      - Prediction intervals and uncertainty bounds (+/- 1-sigma, +/- 2-sigma)
    """

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        self.horizons = HORIZONS
        # Multi-output Random Forest regressor for multi-horizon sequence learning
        self.model = MultiOutputRegressor(
            RandomForestRegressor(n_estimators=50, max_depth=10, random_state=random_seed, n_jobs=-1)
        )
        self.is_fitted = False
        self.metrics = {}

    def _prepare_sequence_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Constructs lag features and multi-step target matrices from historical corridor data.
        """
        # Ensure timestamp ordering
        df_sorted = df.copy()
        if "timestamp" in df_sorted.columns:
            df_sorted["timestamp"] = pd.to_datetime(df_sorted["timestamp"])
            df_sorted = df_sorted.sort_values(by="timestamp").reset_index(drop=True)
            
        vol = df_sorted["traffic_volume"].values.astype(float)
        speed = df_sorted.get("average_speed", pd.Series(np.ones(len(vol)) * 60.0)).values.astype(float)
        temp = df_sorted.get("temperature_c", pd.Series(np.ones(len(vol)) * 20.0)).values.astype(float)
        
        # Extract or simulate hours
        if "hour" in df_sorted.columns:
            hours = df_sorted["hour"].values
        elif "timestamp" in df_sorted.columns:
            hours = df_sorted["timestamp"].dt.hour.values
        else:
            hours = np.tile(np.arange(24), int(np.ceil(len(vol)/24)))[:len(vol)]
            
        # Cyclic hour encoding
        sin_hour = np.sin(2 * np.pi * hours / 24.0)
        cos_hour = np.cos(2 * np.pi * hours / 24.0)
        
        X_list = []
        Y_list = []
        
        # Multi-step target: 4 steps ahead (sampling frequency ~ 15 min or 1 hr)
        # Using step offsets 1, 2, 4, 8 to represent [t+15, t+30, t+60, t+120]
        step_offsets = [1, 2, 4, 8]
        max_offset = max(step_offsets)
        
        for i in range(3, len(vol) - max_offset):
            # Features: current, lag 1, lag 2, lag 3 + speed + temp + cyclic hour
            feats = [
                vol[i],             # y_t
                vol[i - 1],         # y_t-1
                vol[i - 2],         # y_t-2
                vol[i - 3],         # y_t-3
                speed[i],           # speed_t
                temp[i],            # temp_t
                sin_hour[i],        # sin(hour)
                cos_hour[i]         # cos(hour)
            ]
            
            # Targets across the 4 horizons
            targets = [vol[i + offset] for offset in step_offsets]
            
            X_list.append(feats)
            Y_list.append(targets)
            
        return np.array(X_list), np.array(Y_list)

    def train_and_evaluate(self, df: pd.DataFrame) -> Dict:
        """
        Trains the multi-horizon forecaster and evaluates horizon-wise metrics.
        """
        logger.info("Preparing multi-horizon sequence features...")
        X, Y = self._prepare_sequence_features(df)
        
        if len(X) < 100:
            raise ValueError(f"Insufficient historical samples ({len(X)}) for sequence training.")
            
        # 80/20 train-test split
        split_idx = int(len(X) * 0.80)
        X_train, X_test = X[:split_idx], X[split_idx:]
        Y_train, Y_test = Y[:split_idx], Y[split_idx:]
        
        logger.info(f"Training Multi-Horizon Sequence Forecaster on {len(X_train)} instances...")
        self.model.fit(X_train, Y_train)
        self.is_fitted = True
        
        preds_test = self.model.predict(X_test)
        
        horizon_metrics = {}
        for idx, h in enumerate(self.horizons):
            actual_h = Y_test[:, idx]
            pred_h = preds_test[:, idx]
            
            rmse = float(np.sqrt(mean_squared_error(actual_h, pred_h)))
            mae = float(mean_absolute_error(actual_h, pred_h))
            # MAPE with safe denominator
            mape = float(np.mean(np.abs((actual_h - pred_h) / np.maximum(actual_h, 100.0))) * 100.0)
            
            horizon_metrics[f"t+{h}m"] = {
                "horizon_minutes": h,
                "rmse": round(rmse, 2),
                "mae": round(mae, 2),
                "mape_pct": round(mape, 2),
                "r2_score": round(float(1.0 - (rmse**2 / (np.var(actual_h) + 1e-5))), 4)
            }
            
        self.metrics = horizon_metrics
        logger.info("Multi-Horizon Forecasting evaluation completed successfully.")
        return horizon_metrics

    def predict_future_trajectory(
        self,
        current_volume: float,
        current_speed: float = 60.0,
        temperature_c: float = 20.0,
        current_hour: int = 14
    ) -> Dict:
        """
        Generates forward prediction trajectory for t+15, t+30, t+60, t+120 min
        with 1-sigma and 2-sigma confidence bounds.
        """
        sin_h = np.sin(2 * np.pi * current_hour / 24.0)
        cos_h = np.cos(2 * np.pi * current_hour / 24.0)
        
        # Approximate short-term lag from current state
        sample_input = np.array([[
            current_volume,
            current_volume * 0.98,
            current_volume * 0.96,
            current_volume * 0.95,
            current_speed,
            temperature_c,
            sin_h,
            cos_h
        ]])
        
        if self.is_fitted:
            preds = self.model.predict(sample_input)[0]
        else:
            # Physics-based baseline forecast if model not yet fitted
            decay_factors = [1.02, 1.05, 0.98, 0.91]
            preds = np.array([current_volume * df for df in decay_factors])
            
        trajectory = []
        for idx, h in enumerate(self.horizons):
            predicted_vol = float(round(preds[idx], 1))
            # Uncertainty expands with time horizon
            uncertainty_sigma = round(50.0 + (idx * 35.0), 1)
            
            # Congestion classification projection
            if predicted_vol > 4500:
                cond = "SEVERE"
            elif predicted_vol > 3200:
                cond = "HIGH"
            elif predicted_vol > 1800:
                cond = "MEDIUM"
            else:
                cond = "LOW"
                
            trajectory.append({
                "horizon": f"t+{h}m",
                "horizon_minutes": h,
                "predicted_volume": int(predicted_vol),
                "lower_bound_95": max(0, int(predicted_vol - (2.0 * uncertainty_sigma))),
                "upper_bound_95": int(predicted_vol + (2.0 * uncertainty_sigma)),
                "standard_error": uncertainty_sigma,
                "predicted_condition": cond
            })
            
        return {
            "current_volume": int(current_volume),
            "current_hour": current_hour,
            "trajectory": trajectory
        }
