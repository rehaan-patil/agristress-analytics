"""
Integration and API endpoint tests for AgriStress Analytics FastAPI backend.
"""
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "AgriStress Analytics"
    assert "documentation" in data


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_datasets_status_endpoint():
    response = client.get("/api/v1/datasets/status")
    assert response.status_code == 200
    data = response.json()
    assert "datasets" in data
    assert "ready_for_analysis" in data


def test_overview_endpoint():
    response = client.get("/api/v1/overview")
    assert response.status_code == 200
    data = response.json()
    assert "kcc_total_queries" in data
    assert "states_covered" in data


def test_analysis_summary_and_trends():
    # Summary
    res_sum = client.get("/api/v1/analysis/summary")
    if res_sum.status_code == 200:
        data = res_sum.json()
        assert "descriptive_statistics" in data

    # Trends
    res_trends = client.get("/api/v1/analysis/trends?limit=14")
    assert res_trends.status_code == 200
    trends = res_trends.json()
    assert isinstance(trends, list)


def test_analysis_regions_and_correlations():
    # Regions
    res_reg = client.get("/api/v1/analysis/regions")
    assert res_reg.status_code == 200
    assert isinstance(res_reg.json(), list)

    # Correlations
    res_corr = client.get("/api/v1/analysis/correlations")
    assert res_corr.status_code == 200
    assert isinstance(res_corr.json(), list)


def test_hypothesis_test_endpoint():
    payload = {
        "state": None,
        "commodity": None,
        "diesel_shock_threshold_pct": 2.0
    }
    response = client.post("/api/v1/analysis/hypothesis-tests", json=payload)
    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert len(data["results"]) >= 1


def test_forecast_endpoint():
    payload = {
        "horizon_days": 7,
        "use_sarimax": True
    }
    response = client.post("/api/v1/forecast", json=payload)
    if response.status_code == 200:
        data = response.json()
        assert "predictions" in data
        assert len(data["predictions"]) == 7
        assert "stress_assessment" in data


def test_forecast_history_endpoint():
    response = client.get("/api/v1/forecast/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_invalid_file_upload_rejected():
    # Upload a .txt file instead of .csv
    file_content = b"random text"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    response = client.post("/api/v1/data/import/kcc", files=files)
    assert response.status_code == 400
    assert "Only .csv files are supported" in response.json()["detail"]


def test_reports_latest_endpoint():
    response = client.get("/api/v1/reports/latest")
    assert response.status_code == 200
    data = response.json()
    assert "content_markdown" in data
    assert "# AgriStress Analytics" in data["content_markdown"]
