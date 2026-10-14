# AgriStress Analytics — REST API Reference for Teammates

This reference details the 16 endpoints provided by the AgriStress Analytics FastAPI backend.

**Base URL (Local):** `http://127.0.0.1:8000`  
**Interactive Swagger UI:** `http://127.0.0.1:8000/docs`  
**ReDoc Documentation:** `http://127.0.0.1:8000/redoc`

---

## 1. System Health & Metadata

### `GET /health`
Verifies database connectivity and server status.
```json
// Response (200 OK)
{
  "status": "healthy",
  "database": "connected",
  "environment": "local_or_render",
  "timestamp": "2026-10-14T02:03:23.830427"
}
```

### `GET /api/v1/datasets/status`
Checks database table row counts, date bounds, and whether sufficient data ($\ge 30$ rows) exists for forecasting.
```json
// Response (200 OK)
{
  "status": "READY",
  "datasets": {
    "kcc": {
      "table_name": "kcc_observations",
      "total_records": 11680,
      "min_date": "2024-01-01",
      "max_date": "2025-12-30",
      "states_count": 4,
      "is_synthetic": true
    },
    "commodity": {
      "table_name": "commodity_observations",
      "total_records": 7512,
      "min_date": "2024-01-01",
      "max_date": "2025-12-30",
      "states_count": 4,
      "is_synthetic": true
    },
    "fuel": {
      "table_name": "fuel_observations",
      "total_records": 2920,
      "min_date": "2024-01-01",
      "max_date": "2025-12-30",
      "states_count": 4,
      "is_synthetic": true
    }
  },
  "ready_for_analysis": true,
  "notes": [
    "Notice: Some or all tables contain synthetic records generated for testing and demonstration."
  ]
}
```

### `GET /api/v1/overview`
High-level overview of total calls, recorded crops, and geographic coverage.
```json
// Response (200 OK)
{
  "kcc_total_queries": 191100,
  "commodity_records": 7512,
  "fuel_records": 2920,
  "date_range": {
    "start": "2024-01-01",
    "end": "2025-12-30"
  },
  "states_covered": ["Madhya Pradesh", "Maharashtra", "Punjab", "Uttar Pradesh"],
  "is_synthetic": true
}
```

---

## 2. CSV Data Ingestion

### `POST /api/v1/data/import/kcc`
Uploads a Kisan Call Centre query CSV file.
- **Form Data:** `file` (Multipart `.csv`), `is_synthetic` (Boolean query param, default `false`)
- **Required Columns:** `observation_date`, `state`

### `POST /api/v1/data/import/commodity`
Uploads an APMC Mandi wholesale commodity price CSV file.
- **Form Data:** `file` (Multipart `.csv`), `is_synthetic` (Boolean query param)
- **Required Columns:** `observation_date`, `state`, `commodity`, `wholesale_price`

### `POST /api/v1/data/import/fuel`
Uploads a retail diesel fuel price CSV file.
- **Form Data:** `file` (Multipart `.csv`), `is_synthetic` (Boolean query param)
- **Required Columns:** `observation_date`, `diesel_price`

**Sample Upload Response:**
```json
{
  "status": "SUCCESS",
  "dataset_type": "kcc",
  "filename": "kcc_queries.csv",
  "total_rows": 500,
  "accepted_rows": 492,
  "rejected_rows": 5,
  "duplicate_rows": 3,
  "errors": []
}
```

---

## 3. Analysis & Econometric Testing

### `GET /api/v1/analysis/summary`
Computes descriptive statistics (count, mean, std, min, median, max) across analytical variables.
- **Query Params:** `state` (optional), `commodity` (optional)

### `GET /api/v1/analysis/trends`
Returns daily time series for plotting in frontend chart components.
- **Query Params:** `state` (optional), `commodity` (optional), `limit` (int, default 60)
```json
// Response excerpt
[
  {
    "date": "2025-12-29",
    "query_count": 240.0,
    "wholesale_price": 1820.5,
    "diesel_price": 93.4
  }
]
```

### `GET /api/v1/analysis/regions`
Returns state-by-state inquiry breakdowns.
```json
[
  {
    "state": "Maharashtra",
    "total_queries": 62500,
    "observation_days": 730,
    "avg_daily_queries": 85.6
  }
]
```

### `GET /api/v1/analysis/correlations`
Computes pairwise Pearson $r$ and Spearman $\rho$ against KCC query demand.

### `POST /api/v1/analysis/hypothesis-tests`
Runs tests for Hypothesis A, B, and C.
```json
// Request Body
{
  "state": "Maharashtra",
  "commodity": "Onion",
  "diesel_shock_threshold_pct": 2.0
}
```
```json
// Response (200 OK excerpt)
{
  "run_date": "2026-10-14 07:25:00",
  "state_filter": "Maharashtra",
  "commodity_filter": "Onion",
  "results": [
    {
      "hypothesis_code": "HYP-A",
      "title": "Commodity Price Movements vs Query Demand",
      "null_hypothesis": "Commodity price changes have no linear association with KCC query demand.",
      "alternative_hypothesis": "Commodity price changes are associated with KCC query demand.",
      "test_used": "Pearson Correlation Test",
      "sample_size": 729,
      "test_statistic": -0.0125,
      "p_value": 0.7354,
      "effect_size": -0.0125,
      "significance_level": 0.05,
      "reject_null": false,
      "verdict_plain_english": "Fail to reject null hypothesis (r=-0.0125, p=0.7354)",
      "limitations": "Correlation does not imply economic causation."
    }
  ],
  "disclaimer": "Tests demonstrate statistical association in this sample, not economic causation."
}
```

---

## 4. Forecasting & Advisory Stress

### `POST /api/v1/forecast`
Fits SARIMAX on historical data and predicts future daily call demand.
```json
// Request Body
{
  "state": null,
  "commodity": null,
  "horizon_days": 14,
  "use_sarimax": true
}
```
```json
// Response Excerpt
{
  "forecast_id": 1,
  "model_name": "SARIMAX(1,1,1)(1,1,0)[7]",
  "state": null,
  "target": "query_count",
  "train_start": "2024-01-01",
  "train_end": "2025-11-30",
  "test_start": "2025-12-01",
  "test_end": "2025-12-30",
  "horizon_days": 14,
  "mae": 30.05,
  "rmse": 35.02,
  "mape": 9.66,
  "predictions": [
    {
      "date": "2025-12-31",
      "predicted_demand": 312.4,
      "lower_bound": 245.1,
      "upper_bound": 379.8,
      "stress_category": "Normal"
    }
  ],
  "stress_assessment": {
    "category": "Normal",
    "historical_baseline_mean": 497.8,
    "elevated_threshold": 645.0,
    "high_threshold": 841.2,
    "explanation": "Forecast (307.8) is within normal parameters (baseline mean: 497.8).",
    "disclaimer": "Project-defined advisory stress indicator for operational research."
  },
  "warnings": []
}
```

### `GET /api/v1/forecast/history`
Returns logged past forecast runs from SQLite.

### `GET /api/v1/forecast/{forecast_id}`
Returns complete prediction points and parameters for a specific forecast ID.

---

## 5. Automated Reports

### `POST /api/v1/reports/generate`
Executes chart generation and writes `outputs/reports/summary_report.md`.

### `GET /api/v1/reports/latest`
Reads and returns the markdown text of the latest generated report.

---

*For architecture and econometric explanations, see [docs/PROJECT_EXPLANATION_FOR_TEAM.md](file:///d:/python-capstone/docs/PROJECT_EXPLANATION_FOR_TEAM.md).*
