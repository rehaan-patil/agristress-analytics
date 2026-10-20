"""
Unit tests for the Farmer-Friendly Recommendation Engine in app/recommendations.py.
"""
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import pytest

from app.recommendations import (
    analyze_commodity_trend,
    analyze_spread_trend,
    analyze_fuel_trend,
    analyze_advisory_demand,
    generate_farmer_recommendations
)


def create_sample_df(n_days=30, start_date="2024-01-01", price_trend="stable", fuel_shock=False):
    dates = [datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i) for i in range(n_days)]
    base_price = 2000.0
    prices = []
    fuels = []
    retail = []
    
    for i in range(n_days):
        if price_trend == "falling":
            p = base_price - (i * 35.0)  # Steady drop
        elif price_trend == "rising":
            p = base_price + (i * 35.0)  # Steady rise
        else:
            p = base_price + (i % 3) * 10.0  # Stable
        prices.append(max(400.0, p))
        retail.append(p * 1.30)
        
        f = 90.0 + (3.0 if fuel_shock and i >= (n_days - 3) else 0.0)
        fuels.append(f)
        
    df = pd.DataFrame({
        "observation_date": dates,
        "wholesale_price": prices,
        "retail_price": retail,
        "price_spread": [r - p for r, p in zip(retail, prices)],
        "diesel_price": fuels,
        "query_count": [50 + (i % 10) for i in range(n_days)],
        "is_synthetic": [True] * n_days
    })
    return df


def test_analyze_commodity_trend_falling():
    df = create_sample_df(n_days=20, price_trend="falling")
    res = analyze_commodity_trend(df, commodity_name="Tomato")
    assert res["available"] is True
    assert res["direction"] == "FALLING"
    assert "declined" in res["headline"].lower()
    assert any("nearby apmc mandis" in a.lower() for a in res["actions"])
    # Ensure it does NOT tell farmer to sell or hold automatically
    assert not any("you must sell today" in a.lower() for a in res["actions"])


def test_analyze_commodity_trend_rising():
    df = create_sample_df(n_days=20, price_trend="rising")
    res = analyze_commodity_trend(df, commodity_name="Wheat")
    assert res["available"] is True
    assert res["direction"] == "RISING"
    assert "improved" in res["headline"].lower()
    assert any("spot prices" in a.lower() for a in res["actions"])


def test_analyze_commodity_trend_stable():
    df = create_sample_df(n_days=20, price_trend="stable")
    res = analyze_commodity_trend(df, commodity_name="Onion")
    assert res["available"] is True
    assert res["direction"] == "STABLE"
    assert "steady" in res["headline"].lower()


def test_analyze_commodity_trend_missing_data():
    empty_df = pd.DataFrame({"observation_date": ["2024-01-01"]})
    res = analyze_commodity_trend(empty_df, commodity_name="Onion")
    assert res["available"] is False
    assert "unavailable" in res["headline"].lower()


def test_analyze_fuel_trend_shock():
    df = create_sample_df(n_days=20, fuel_shock=True)
    res = analyze_fuel_trend(df, shock_threshold_pct=1.0)
    assert res["available"] is True
    assert res["status"] == "INCREASED"
    assert "increased" in res["headline"].lower()
    assert any("freight quote" in a.lower() or "share" in a.lower() for a in res["actions"])


def test_analyze_fuel_trend_missing():
    df = pd.DataFrame({"observation_date": ["2024-01-01"], "wholesale_price": [2000.0]})
    res = analyze_fuel_trend(df)
    assert res["available"] is False


def test_analyze_advisory_demand_high():
    forecast_mock = {
        "horizon_days": 14,
        "stress_assessment": {
            "category": "High",
            "historical_baseline_mean": 80.0
        },
        "predictions": [{"predicted_demand": 190.0} for _ in range(14)]
    }
    res = analyze_advisory_demand(forecast_mock)
    assert res["available"] is True
    assert res["category"] == "HIGH"
    assert "unusually high" in res["headline"].lower()
    assert any("1800-180-1551" in a for a in res["actions"])


def test_analyze_advisory_demand_normal():
    forecast_mock = {
        "horizon_days": 14,
        "stress_assessment": {
            "category": "Normal",
            "historical_baseline_mean": 80.0
        },
        "predictions": [{"predicted_demand": 75.0} for _ in range(14)]
    }
    res = analyze_advisory_demand(forecast_mock)
    assert res["available"] is True
    assert res["category"] == "NORMAL"
    assert "normal" in res["headline"].lower()


def test_generate_farmer_recommendations_end_to_end(tmp_path):
    df = create_sample_df(n_days=30, price_trend="falling", fuel_shock=True)
    forecast_mock = {
        "horizon_days": 14,
        "stress_assessment": {
            "category": "High",
            "historical_baseline_mean": 60.0
        },
        "predictions": [{"predicted_demand": 160.0} for _ in range(14)]
    }
    quality_mock = {
        "sample_start": "2024-01-01",
        "sample_end": "2024-01-30",
        "is_synthetic": True
    }

    advisory = generate_farmer_recommendations(
        df=df,
        forecast_res=forecast_mock,
        state="Maharashtra",
        commodity="Onion",
        quality=quality_mock,
        output_dir=tmp_path
    )

    assert advisory["status"] == "SUCCESS"
    assert Path(advisory["report_md_path"]).exists()
    assert Path(advisory["report_txt_path"]).exists()

    md_text = Path(advisory["report_md_path"]).read_text(encoding="utf-8")
    assert "Agricultural Information and Market Advisory" in md_text
    assert "Maharashtra" in md_text
    assert "Onion" in md_text
    assert "1800-180-1551" in md_text
    # Verify no statistical jargon
    assert "p-value" not in md_text.lower()
    assert "sarimax" not in md_text.lower()
    assert "standard deviation" not in md_text.lower()

    txt_text = Path(advisory["report_txt_path"]).read_text(encoding="utf-8")
    assert "WHAT IS HAPPENING?" in txt_text
    assert "RECOMMENDED NEXT STEPS" in txt_text
