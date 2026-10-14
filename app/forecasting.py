"""
SARIMAX Time-Series Forecasting and Advisory-Stress Indicator for AgriStress Analytics.

Written in understandable, student-level Python using Statsmodels and Pandas.
Implements chronological train-test splitting, seasonal naive baseline comparison,
SARIMAX fitting, prediction intervals, and explainable advisory-stress classification.
"""
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import json

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from statsmodels.tsa.statespace.sarimax import SARIMAX

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app.config import OUTPUTS_DIR
from app.models import ForecastHistory
from app.data_processing import build_analytical_dataset


# =====================================================================
# 1. EVALUATION METRICS
# =====================================================================

def calculate_metrics(actual: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
    """
    Calculates standard error metrics: MAE, RMSE, and zero-safe MAPE.
    Formula:
      MAE = mean(|actual - predicted|)
      RMSE = sqrt(mean((actual - predicted)^2))
      MAPE = mean(|actual - predicted| / max(actual, 1.0)) * 100
    """
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    errors = actual - predicted
    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(errors ** 2)))

    # Zero-safe MAPE: avoid division by zero when calls are 0 on Sundays
    denominator = np.where(actual == 0, 1.0, actual)
    mape = float(np.mean(np.abs(errors) / denominator) * 100.0)

    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "mape": round(mape, 2)
    }


# =====================================================================
# 2. ADVISORY STRESS CLASSIFICATION
# =====================================================================

def classify_advisory_stress(
    predicted_mean: float,
    predicted_upper: float,
    historical_mean: float,
    historical_std: float
) -> Dict[str, Any]:
    """
    Classifies forecasted query demand into transparent operational stress levels:
      - Normal: Demand < Baseline + 0.75 * StdDev
      - Elevated: Baseline + 0.75 * StdDev <= Demand < Baseline + 1.75 * StdDev
      - High: Demand >= Baseline + 1.75 * StdDev
      
    Also evaluates whether the 95% upper confidence interval crosses thresholds,
    signaling forecasting uncertainty.
    """
    elevated_cutoff = historical_mean + (0.75 * historical_std)
    high_cutoff = historical_mean + (1.75 * historical_std)

    if predicted_mean >= high_cutoff:
        category = "High"
        explanation = (
            f"Forecasted query volume ({predicted_mean:.1f}) exceeds the high-stress threshold "
            f"({high_cutoff:.1f}). Call centers may experience advisory backlogs or extended wait times."
        )
    elif predicted_mean >= elevated_cutoff:
        category = "Elevated"
        explanation = (
            f"Forecasted query volume ({predicted_mean:.1f}) is above the normal range "
            f"({elevated_cutoff:.1f} to {high_cutoff:.1f}). Operational monitoring recommended."
        )
    else:
        category = "Normal"
        explanation = (
            f"Forecasted query volume ({predicted_mean:.1f}) remains within historical normal parameters "
            f"(baseline mean: {historical_mean:.1f})."
        )

    uncertainty_note = ""
    if category != "High" and predicted_upper >= high_cutoff:
        uncertainty_note = " Notice: 95% upper prediction bound reaches the 'High' stress threshold."

    return {
        "category": category,
        "historical_baseline_mean": round(historical_mean, 2),
        "elevated_threshold": round(elevated_cutoff, 2),
        "high_threshold": round(high_cutoff, 2),
        "explanation": explanation + uncertainty_note,
        "disclaimer": (
            "This is a project-defined research indicator reflecting expected inquiry influx. "
            "It is not an official government operational mandate or staffing directive."
        )
    }


# =====================================================================
# 3. CORE FORECASTING PIPELINE
# =====================================================================

def generate_forecast(
    db: Session,
    state: Optional[str] = None,
    commodity: Optional[str] = None,
    horizon_days: int = 14,
    use_sarimax: bool = True,
    future_exogenous: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Full forecasting workflow:
      1. Fetch and chronologically align time-series data.
      2. Check data sufficiency (minimum 30 observations).
      3. Perform chronological train/test split (80% train, 20% test).
      4. Fit a 7-day seasonal naive baseline model.
      5. Fit SARIMAX(1, 1, 1)(1, 1, 0)[7] model.
      6. Compare evaluation metrics (MAE, RMSE, MAPE).
      7. Fit on full sample and forecast out-of-sample for `horizon_days`.
      8. Apply advisory-stress classification.
      9. Save evaluation plot and record to database.
    """
    warnings = []

    # 1. Prepare data
    df = build_analytical_dataset(db, state=state, commodity=commodity, export_csv=False)

    if df.empty or len(df) < 30:
        return {
            "model_name": "NONE",
            "state": state,
            "target": "query_count",
            "train_start": "N/A",
            "train_end": "N/A",
            "horizon_days": horizon_days,
            "predictions": [],
            "stress_assessment": {
                "category": "Normal",
                "historical_baseline_mean": 0.0,
                "elevated_threshold": 0.0,
                "high_threshold": 0.0,
                "explanation": "Insufficient data available for time-series modeling (minimum 30 daily observations required).",
                "disclaimer": "Insufficient data."
            },
            "warnings": ["Need at least 30 observations to fit SARIMAX."]
        }

    series = df.set_index("observation_date")["query_count"].asfreq("D").fillna(0)
    n_total = len(series)

    # 2. Chronological Train-Test Split (80% train, 20% test, max 30 test days)
    test_size = min(30, max(7, int(n_total * 0.2)))
    train_size = n_total - test_size

    train_series = series.iloc[:train_size]
    test_series = series.iloc[train_size:]

    train_start_str = str(train_series.index.min().date())
    train_end_str = str(train_series.index.max().date())
    test_start_str = str(test_series.index.min().date())
    test_end_str = str(test_series.index.max().date())

    # 3. Seasonal Naive Baseline (predict value from 7 days prior)
    # y_hat_t = y_{t-7}
    baseline_preds = []
    for i in range(len(test_series)):
        lookup_idx = train_size + i - 7
        if lookup_idx >= 0:
            val = series.iloc[lookup_idx]
        else:
            val = train_series.mean()
        baseline_preds.append(float(val))

    baseline_metrics = calculate_metrics(test_series.values, np.array(baseline_preds))

    # 4. Fit SARIMAX or Baseline Model
    sarimax_metrics = None
    sarimax_test_preds = None
    model_name = "Seasonal Naive Baseline (7-Day Lag)"

    if use_sarimax:
        try:
            # Documented SARIMAX specification: order=(1, 1, 1), seasonal_order=(1, 1, 0, 7)
            # 7-day seasonality captures the strong weekly call center pattern.
            sarimax_model = SARIMAX(
                train_series,
                order=(1, 1, 1),
                seasonal_order=(1, 1, 0, 7),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            sarimax_fit = sarimax_model.fit(disp=False, maxiter=100)

            # Test predictions
            sarimax_test_preds = sarimax_fit.predict(start=test_series.index[0], end=test_series.index[-1])
            # Prevent negative forecasts for count data
            sarimax_test_preds = np.clip(sarimax_test_preds, 0, None)

            sarimax_metrics = calculate_metrics(test_series.values, sarimax_test_preds.values)
            model_name = "SARIMAX(1,1,1)(1,1,0)[7]"

        except Exception as e:
            warnings.append(f"SARIMAX optimization did not converge ({str(e)}). Fell back to Seasonal Naive baseline.")
            use_sarimax = False

    # Check whether SARIMAX actually outperformed baseline
    if sarimax_metrics:
        if sarimax_metrics["rmse"] > baseline_metrics["rmse"]:
            warnings.append(
                f"Notice: Baseline Seasonal Naive RMSE ({baseline_metrics['rmse']}) was lower than SARIMAX RMSE ({sarimax_metrics['rmse']}) on the test split."
            )

    # 5. Out-of-sample Future Forecast (horizon_days)
    last_date = series.index.max()
    future_dates = [last_date + timedelta(days=i + 1) for i in range(horizon_days)]

    if use_sarimax:
        try:
            # Refit on full series to utilize all historical information
            full_model = SARIMAX(
                series,
                order=(1, 1, 1),
                seasonal_order=(1, 1, 0, 7),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            full_fit = full_model.fit(disp=False, maxiter=100)
            forecast_res = full_fit.get_forecast(steps=horizon_days)

            pred_mean = np.clip(forecast_res.predicted_mean.values, 0, None)
            conf_int = forecast_res.conf_int(alpha=0.05).values
            pred_lower = np.clip(conf_int[:, 0], 0, None)
            pred_upper = np.clip(conf_int[:, 1], 0, None)
        except Exception:
            # Fallback to repeating last week's pattern
            last_week = series.iloc[-7:].values
            pred_mean = np.array([last_week[i % 7] for i in range(horizon_days)])
            pred_lower = np.clip(pred_mean * 0.85, 0, None)
            pred_upper = pred_mean * 1.15
    else:
        last_week = series.iloc[-7:].values
        pred_mean = np.array([last_week[i % 7] for i in range(horizon_days)])
        pred_lower = np.clip(pred_mean * 0.85, 0, None)
        pred_upper = pred_mean * 1.15

    # 6. Advisory-Stress Classification
    hist_mean = float(series.mean())
    hist_std = float(series.std()) if float(series.std()) > 0 else 1.0

    avg_future_demand = float(np.mean(pred_mean))
    avg_future_upper = float(np.mean(pred_upper))

    stress_eval = classify_advisory_stress(
        avg_future_demand,
        avg_future_upper,
        hist_mean,
        hist_std
    )

    # Build point-by-point forecast list
    predictions_list = []
    for d, m, low, high in zip(future_dates, pred_mean, pred_lower, pred_upper):
        point_stress = classify_advisory_stress(float(m), float(high), hist_mean, hist_std)
        predictions_list.append({
            "date": d.strftime("%Y-%m-%d"),
            "predicted_demand": round(float(m), 1),
            "lower_bound": round(float(low), 1),
            "upper_bound": round(float(high), 1),
            "stress_category": point_stress["category"]
        })

    # 7. Generate Forecast vs Actual Plot
    plot_path = OUTPUTS_DIR / "charts" / "forecast_evaluation.png"
    plt.figure(figsize=(12, 5))
    
    # Plot recent historical actuals (last 90 days for clarity)
    recent_actual = series.iloc[-90:]
    plt.plot(recent_actual.index, recent_actual.values, label="Historical Actual Queries", color="#1976D2", linewidth=1.5)

    # Plot future forecast
    plt.plot(future_dates, pred_mean, label=f"Forecast: {model_name}", color="#E65100", linewidth=2.0)
    plt.fill_between(
        future_dates,
        pred_lower,
        pred_upper,
        color="#FFE0B2",
        alpha=0.6,
        label="95% Confidence Interval"
    )

    # Add historical baseline line
    plt.axhline(hist_mean, color="#757575", linestyle="--", label=f"Historical Baseline Mean ({hist_mean:.1f})")

    plt.title(f"AgriStress Advisory Demand Forecast ({horizon_days}-Day Horizon)", fontsize=12, fontweight="bold")
    plt.xlabel("Date", fontsize=10)
    plt.ylabel("KCC Inquiries", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)
    plt.close()

    # 8. Record to database for history tracking
    chosen_metrics = sarimax_metrics if (use_sarimax and sarimax_metrics) else baseline_metrics
    db_record = ForecastHistory(
        model_name=model_name,
        target_variable="query_count",
        state=state,
        forecast_start_date=future_dates[0].date(),
        forecast_end_date=future_dates[-1].date(),
        horizon_days=horizon_days,
        mae=chosen_metrics.get("mae"),
        rmse=chosen_metrics.get("rmse"),
        mape=chosen_metrics.get("mape"),
        stress_category=stress_eval["category"],
        details_json=json.dumps({
            "predictions": predictions_list,
            "stress": stress_eval,
            "baseline_metrics": baseline_metrics,
            "model_metrics": chosen_metrics
        })
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return {
        "forecast_id": db_record.id,
        "model_name": model_name,
        "state": state,
        "target": "query_count",
        "train_start": train_start_str,
        "train_end": train_end_str,
        "test_start": test_start_str,
        "test_end": test_end_str,
        "horizon_days": horizon_days,
        "mae": chosen_metrics.get("mae"),
        "rmse": chosen_metrics.get("rmse"),
        "mape": chosen_metrics.get("mape"),
        "predictions": predictions_list,
        "stress_assessment": stress_eval,
        "warnings": warnings
    }


def get_forecast_history(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieves previous forecast runs from the database."""
    records = db.query(ForecastHistory).order_by(ForecastHistory.id.desc()).limit(limit).all()
    return [r.to_dict() for r in records]


def get_forecast_by_id(db: Session, forecast_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves full forecast details including prediction points for a specific ID."""
    record = db.query(ForecastHistory).filter(ForecastHistory.id == forecast_id).first()
    if not record:
        return None

    data = record.to_dict()
    if record.details_json:
        try:
            data["details"] = json.loads(record.details_json)
        except Exception:
            data["details"] = {}
    return data
