"""
Time-Series Forecasting and Advisory-Stress Classification for AgriStress Analytics.
Uses Seasonal Naive baseline and Statsmodels SARIMAX(1,1,1)(1,1,0)[7].
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
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


def calculate_metrics(actual: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
    """Calculates MAE, RMSE, and zero-safe MAPE error metrics."""
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    errors = actual - predicted

    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(errors ** 2)))
    # Avoid zero division when call volume is 0
    denom = np.where(actual == 0, 1.0, actual)
    mape = float(np.mean(np.abs(errors) / denom) * 100.0)

    return {"mae": round(mae, 2), "rmse": round(rmse, 2), "mape": round(mape, 2)}


def classify_advisory_stress(pred_mean: float, pred_upper: float, hist_mean: float, hist_std: float) -> Dict[str, Any]:
    """Classifies forecasted demand into Normal, Elevated, or High based on standard deviations."""
    elevated_cutoff = hist_mean + (0.75 * hist_std)
    high_cutoff = hist_mean + (1.75 * hist_std)

    if pred_mean >= high_cutoff:
        cat = "High"
        exp = f"Forecast ({pred_mean:.1f}) exceeds high stress threshold ({high_cutoff:.1f})."
    elif pred_mean >= elevated_cutoff:
        cat = "Elevated"
        exp = f"Forecast ({pred_mean:.1f}) is above normal range ({elevated_cutoff:.1f} to {high_cutoff:.1f})."
    else:
        cat = "Normal"
        exp = f"Forecast ({pred_mean:.1f}) is within normal parameters (baseline mean: {hist_mean:.1f})."

    if cat != "High" and pred_upper >= high_cutoff:
        exp += " (Warning: 95% upper prediction bound reaches High threshold)."

    return {
        "category": cat,
        "historical_baseline_mean": round(hist_mean, 2),
        "elevated_threshold": round(elevated_cutoff, 2),
        "high_threshold": round(high_cutoff, 2),
        "explanation": exp,
        "disclaimer": "Project-defined advisory stress indicator for operational research."
    }


def generate_forecast(
    db: Session,
    state: Optional[str] = None,
    commodity: Optional[str] = None,
    horizon_days: int = 14,
    use_sarimax: bool = True,
    future_exogenous: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Runs train-test evaluation and forecasts future query demand using SARIMAX."""
    df = build_analytical_dataset(db, state=state, commodity=commodity, export_csv=False)
    if df.empty or len(df) < 30:
        return {
            "model_name": "NONE", "state": state, "target": "query_count",
            "train_start": "N/A", "train_end": "N/A", "horizon_days": horizon_days,
            "predictions": [],
            "stress_assessment": {"category": "Normal", "historical_baseline_mean": 0.0, "elevated_threshold": 0.0, "high_threshold": 0.0, "explanation": "Insufficient data.", "disclaimer": "Insufficient data."},
            "warnings": ["Need at least 30 observations to fit model."]
        }

    series = df.set_index("observation_date")["query_count"].asfreq("D").fillna(0)
    test_size = min(30, max(7, int(len(series) * 0.2)))
    train, test = series.iloc[:-test_size], series.iloc[-test_size:]

    # 1. Seasonal Naive baseline (value from 7 days prior)
    baseline_preds = [series.iloc[len(train) + i - 7] if (len(train) + i - 7) >= 0 else train.mean() for i in range(len(test))]
    baseline_metrics = calculate_metrics(test.values, np.array(baseline_preds))

    # 2. Fit SARIMAX
    model_name = "Seasonal Naive Baseline (7-Day Lag)"
    chosen_metrics = baseline_metrics
    warnings = []

    if use_sarimax:
        try:
            fit_res = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 1, 0, 7), enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
            test_preds = np.clip(fit_res.predict(start=test.index[0], end=test.index[-1]), 0, None)
            chosen_metrics = calculate_metrics(test.values, test_preds.values)
            model_name = "SARIMAX(1,1,1)(1,1,0)[7]"
        except Exception as e:
            warnings.append(f"SARIMAX optimization error: {e}. Used baseline.")
            use_sarimax = False

    # 3. Forecast future horizon_days
    future_dates = [series.index.max() + timedelta(days=i + 1) for i in range(horizon_days)]
    if use_sarimax:
        try:
            full_fit = SARIMAX(series, order=(1, 1, 1), seasonal_order=(1, 1, 0, 7), enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
            fc = full_fit.get_forecast(steps=horizon_days)
            pred_mean = np.clip(fc.predicted_mean.values, 0, None)
            conf_int = fc.conf_int(alpha=0.05).values
            pred_lower, pred_upper = np.clip(conf_int[:, 0], 0, None), np.clip(conf_int[:, 1], 0, None)
        except Exception:
            last_week = series.iloc[-7:].values
            pred_mean = np.array([last_week[i % 7] for i in range(horizon_days)])
            pred_lower, pred_upper = pred_mean * 0.8, pred_mean * 1.2
    else:
        last_week = series.iloc[-7:].values
        pred_mean = np.array([last_week[i % 7] for i in range(horizon_days)])
        pred_lower, pred_upper = pred_mean * 0.8, pred_mean * 1.2

    # 4. Advisory stress assessment
    hist_mean = float(series.mean())
    hist_std = float(series.std()) if float(series.std()) > 0 else 1.0
    stress = classify_advisory_stress(float(np.mean(pred_mean)), float(np.mean(pred_upper)), hist_mean, hist_std)

    predictions = [
        {
            "date": d.strftime("%Y-%m-%d"),
            "predicted_demand": round(float(m), 1),
            "lower_bound": round(float(low), 1),
            "upper_bound": round(float(high), 1),
            "stress_category": classify_advisory_stress(float(m), float(high), hist_mean, hist_std)["category"]
        }
        for d, m, low, high in zip(future_dates, pred_mean, pred_lower, pred_upper)
    ]

    # 5. Save chart
    plot_path = OUTPUTS_DIR / "charts" / "forecast_evaluation.png"
    plt.figure(figsize=(10, 4))
    recent = series.iloc[-60:]
    plt.plot(recent.index, recent.values, label="Historical Actuals", color="#2563eb")
    plt.plot(future_dates, pred_mean, label=f"Forecast: {model_name}", color="#ea580c")
    plt.fill_between(future_dates, pred_lower, pred_upper, color="#fed7aa", alpha=0.5, label="95% Confidence Interval")
    plt.axhline(hist_mean, color="gray", linestyle="--", label="Historical Mean")
    plt.title(f"Advisory Demand Forecast ({horizon_days} Days)")
    plt.xlabel("Date")
    plt.ylabel("Inquiries")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path, dpi=120)
    plt.close()

    # 6. Save run in database
    rec = ForecastHistory(
        model_name=model_name,
        target_variable="query_count",
        state=state,
        forecast_start_date=future_dates[0].date(),
        forecast_end_date=future_dates[-1].date(),
        horizon_days=horizon_days,
        mae=chosen_metrics.get("mae"),
        rmse=chosen_metrics.get("rmse"),
        mape=chosen_metrics.get("mape"),
        stress_category=stress["category"],
        details_json=json.dumps({"predictions": predictions, "stress": stress})
    )
    db.add(rec)
    db.commit()

    return {
        "forecast_id": rec.id,
        "model_name": model_name,
        "state": state,
        "target": "query_count",
        "train_start": str(train.index.min().date()),
        "train_end": str(train.index.max().date()),
        "test_start": str(test.index.min().date()),
        "test_end": str(test.index.max().date()),
        "horizon_days": horizon_days,
        "mae": chosen_metrics.get("mae"),
        "rmse": chosen_metrics.get("rmse"),
        "mape": chosen_metrics.get("mape"),
        "predictions": predictions,
        "stress_assessment": stress,
        "warnings": warnings
    }


def get_forecast_history(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """Gets list of previous forecast logs."""
    return [r.to_dict() for r in db.query(ForecastHistory).order_by(ForecastHistory.id.desc()).limit(limit).all()]


def get_forecast_by_id(db: Session, forecast_id: int) -> Optional[Dict[str, Any]]:
    """Gets details for a single forecast run."""
    r = db.query(ForecastHistory).filter(ForecastHistory.id == forecast_id).first()
    if not r:
        return None
    data = r.to_dict()
    data["details"] = json.loads(r.details_json) if r.details_json else {}
    return data
