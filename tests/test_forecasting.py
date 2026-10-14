"""
Unit tests for time-series forecasting, SARIMAX fitting, and advisory-stress classification.
"""
import numpy as np
import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import KCCObservation
from app.forecasting import calculate_metrics, classify_advisory_stress, generate_forecast


@pytest.fixture
def mock_db_with_series():
    """Generates an in-memory SQLite database populated with 100 days of KCC query records."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()

    start_date = pd.to_datetime("2024-01-01")
    objs = []
    for i in range(100):
        d = (start_date + pd.Timedelta(days=i)).date()
        # Weekly cycle: higher on weekdays, lower on Sundays
        day_of_week = i % 7
        calls = 30 if day_of_week == 6 else (100 + (i % 10))
        objs.append(
            KCCObservation(
                observation_date=d,
                state="Maharashtra",
                query_count=calls,
                is_synthetic=True
            )
        )
    session.bulk_save_objects(objs)
    session.commit()

    try:
        yield session
    finally:
        session.close()


def test_calculate_metrics():
    actual = np.array([100.0, 110.0, 120.0, 130.0])
    predicted = np.array([102.0, 108.0, 125.0, 125.0])
    metrics = calculate_metrics(actual, predicted)

    assert "mae" in metrics
    assert "rmse" in metrics
    assert "mape" in metrics
    assert metrics["mae"] == 3.5  # (|2| + |2| + |5| + |5|) / 4 = 14 / 4 = 3.5
    assert metrics["rmse"] > 0
    assert metrics["mape"] > 0


def test_classify_advisory_stress():
    mean = 100.0
    std = 20.0

    # Normal: demand < 100 + 0.75*20 = 115
    res_normal = classify_advisory_stress(110.0, 114.0, mean, std)
    assert res_normal["category"] == "Normal"

    # Elevated: 115 <= demand < 100 + 1.75*20 = 135
    res_elevated = classify_advisory_stress(125.0, 130.0, mean, std)
    assert res_elevated["category"] == "Elevated"

    # High: demand >= 135
    res_high = classify_advisory_stress(145.0, 155.0, mean, std)
    assert res_high["category"] == "High"


def test_generate_forecast_sarimax_pipeline(mock_db_with_series):
    res = generate_forecast(
        db=mock_db_with_series,
        state="Maharashtra",
        horizon_days=14,
        use_sarimax=True
    )

    assert res["model_name"] != "NONE"
    assert len(res["predictions"]) == 14
    assert res["mae"] is not None
    assert res["rmse"] is not None
    assert "stress_assessment" in res
    assert res["stress_assessment"]["category"] in ["Normal", "Elevated", "High"]

    # Verify predictions are non-negative counts
    for p in res["predictions"]:
        assert p["predicted_demand"] >= 0
        assert p["lower_bound"] >= 0
        assert p["upper_bound"] >= p["lower_bound"]


def test_generate_forecast_insufficient_data():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    empty_db = TestingSession()

    res = generate_forecast(db=empty_db, horizon_days=7)
    assert res["model_name"] == "NONE"
    assert len(res["predictions"]) == 0
    assert len(res["warnings"]) > 0
    empty_db.close()
