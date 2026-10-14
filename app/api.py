"""
FastAPI route handlers for AgriStress Analytics.

Written in clean, direct student-level Python.
Route handlers delegate analytical and forecasting computations to
app.data_processing, app.analysis, and app.forecasting.
"""
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import OUTPUTS_DIR
from app.schemas import (
    HealthResponse,
    DatasetStatusResponse,
    OverviewResponse,
    ImportResultResponse,
    AnalysisSummaryResponse,
    TrendPoint,
    RegionalSummary,
    CorrelationPair,
    HypothesisTestRequest,
    HypothesisReportResponse,
    ForecastRequest,
    ForecastResponse,
    ReportGenerateResponse
)
from app.data_processing import (
    import_kcc_csv,
    import_commodity_csv,
    import_fuel_csv,
    get_dataset_status,
    build_analytical_dataset
)
from app.analysis import (
    get_overview_stats,
    get_descriptive_summary,
    get_regional_summary,
    get_correlations,
    run_hypothesis_tests,
    generate_summary_report
)
from app.forecasting import (
    generate_forecast,
    get_forecast_history,
    get_forecast_by_id
)

router = APIRouter()


# =====================================================================
# 1. HEALTH AND STATUS
# =====================================================================

@router.get("/health", response_model=HealthResponse, tags=["Health"])
def check_health(db: Session = Depends(get_db)):
    """Health check endpoint confirming API status and database connectivity."""
    return {
        "status": "healthy",
        "database": "connected",
        "environment": "local_or_render",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/api/v1/datasets/status", response_model=DatasetStatusResponse, tags=["Datasets"])
def get_status(db: Session = Depends(get_db)):
    """Returns database record counts, observation date ranges, and analytical readiness."""
    return get_dataset_status(db)


@router.get("/api/v1/overview", response_model=OverviewResponse, tags=["Overview"])
def get_overview(db: Session = Depends(get_db)):
    """Returns high-level project summary: total queries, records, date bounds, and states."""
    return get_overview_stats(db)


# =====================================================================
# 2. CSV DATA IMPORT
# =====================================================================

def validate_csv_upload(file: UploadFile):
    """Simple check that uploaded file is a CSV and not empty."""
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type for '{file.filename}'. Only .csv files are supported."
        )


@router.post("/api/v1/data/import/kcc", response_model=ImportResultResponse, tags=["Data Ingestion"])
def upload_kcc_data(
    file: UploadFile = File(...),
    is_synthetic: bool = Query(False, description="Flag whether uploaded CSV is synthetic demo data"),
    db: Session = Depends(get_db)
):
    """Uploads and validates a Kisan Call Centre query CSV file into the database."""
    validate_csv_upload(file)
    result = import_kcc_csv(file.file, db, filename=file.filename, is_synthetic=is_synthetic)
    if result["status"] == "FAILED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["errors"])
    return result


@router.post("/api/v1/data/import/commodity", response_model=ImportResultResponse, tags=["Data Ingestion"])
def upload_commodity_data(
    file: UploadFile = File(...),
    is_synthetic: bool = Query(False, description="Flag whether uploaded CSV is synthetic demo data"),
    db: Session = Depends(get_db)
):
    """Uploads and validates an Agricultural Commodity mandi price CSV file into the database."""
    validate_csv_upload(file)
    result = import_commodity_csv(file.file, db, filename=file.filename, is_synthetic=is_synthetic)
    if result["status"] == "FAILED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["errors"])
    return result


@router.post("/api/v1/data/import/fuel", response_model=ImportResultResponse, tags=["Data Ingestion"])
def upload_fuel_data(
    file: UploadFile = File(...),
    is_synthetic: bool = Query(False, description="Flag whether uploaded CSV is synthetic demo data"),
    db: Session = Depends(get_db)
):
    """Uploads and validates a Diesel fuel price CSV file into the database."""
    validate_csv_upload(file)
    result = import_fuel_csv(file.file, db, filename=file.filename, is_synthetic=is_synthetic)
    if result["status"] == "FAILED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["errors"])
    return result


# =====================================================================
# 3. STATISTICAL ANALYSIS AND CORRELATION
# =====================================================================

@router.get("/api/v1/analysis/summary", response_model=AnalysisSummaryResponse, tags=["Analysis"])
def get_analysis_summary(
    state: Optional[str] = Query(None, description="Filter by state name"),
    commodity: Optional[str] = Query(None, description="Filter by commodity"),
    db: Session = Depends(get_db)
):
    """Computes descriptive statistical metrics (mean, median, std dev, range) for analytical variables."""
    df = build_analytical_dataset(db, state=state, commodity=commodity, export_csv=False)
    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analytical data found. Please ensure data has been imported."
        )
    return get_descriptive_summary(df)


@router.get("/api/v1/analysis/trends", response_model=List[TrendPoint], tags=["Analysis"])
def get_recent_trends(
    state: Optional[str] = Query(None, description="Filter by state"),
    commodity: Optional[str] = Query(None, description="Filter by commodity"),
    limit: int = Query(60, ge=7, le=365, description="Number of recent days to return"),
    db: Session = Depends(get_db)
):
    """Returns chronological recent daily observations for charting trends in the frontend."""
    df = build_analytical_dataset(db, state=state, commodity=commodity, export_csv=False)
    if df.empty:
        return []

    recent = df.tail(limit)
    points = []
    for _, row in recent.iterrows():
        points.append({
            "date": row["observation_date"].strftime("%Y-%m-%d"),
            "query_count": float(row["query_count"]) if pd_not_nan(row["query_count"]) else None,
            "wholesale_price": float(row["wholesale_price"]) if pd_not_nan(row["wholesale_price"]) else None,
            "diesel_price": float(row["diesel_price"]) if pd_not_nan(row["diesel_price"]) else None,
        })
    return points


def pd_not_nan(val):
    """Helper to check if a value is not NaN or None."""
    import math
    if val is None:
        return False
    try:
        return not math.isnan(float(val))
    except (ValueError, TypeError):
        return True


@router.get("/api/v1/analysis/regions", response_model=List[RegionalSummary], tags=["Analysis"])
def get_regions(db: Session = Depends(get_db)):
    """Returns comparative query totals and daily averages by state."""
    return get_regional_summary(db)


@router.get("/api/v1/analysis/correlations", response_model=List[CorrelationPair], tags=["Analysis"])
def get_correlation_pairs(
    state: Optional[str] = Query(None),
    commodity: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Computes pairwise Pearson and Spearman correlation coefficients."""
    df = build_analytical_dataset(db, state=state, commodity=commodity, export_csv=False)
    return get_correlations(df)


@router.post("/api/v1/analysis/hypothesis-tests", response_model=HypothesisReportResponse, tags=["Analysis"])
def execute_hypothesis_tests(
    params: HypothesisTestRequest,
    db: Session = Depends(get_db)
):
    """
    Executes formal econometric hypothesis tests:
      - HYP-A: Commodity price change association with query demand
      - HYP-B: Diesel price shocks vs query influx
      - HYP-C: Wholesale-to-retail price spread vs query influx
    """
    df = build_analytical_dataset(db, state=params.state, commodity=params.commodity, export_csv=False)
    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data available to conduct hypothesis tests."
        )

    res = run_hypothesis_tests(df, diesel_shock_threshold_pct=params.diesel_shock_threshold_pct)
    return {
        "run_date": res["run_date"],
        "state_filter": params.state,
        "commodity_filter": params.commodity,
        "results": res["results"],
        "disclaimer": res["disclaimer"]
    }


# =====================================================================
# 4. TIME-SERIES FORECASTING & ADVISORY-STRESS
# =====================================================================

@router.post("/api/v1/forecast", response_model=ForecastResponse, tags=["Forecasting"])
def run_forecast_endpoint(
    req: ForecastRequest,
    db: Session = Depends(get_db)
):
    """
    Runs SARIMAX time-series forecasting for KCC advisory demand,
    compares against seasonal naive baseline, and classifies advisory-stress.
    """
    future_exo_dicts = [e.dict() for e in req.future_exogenous] if req.future_exogenous else None

    result = generate_forecast(
        db=db,
        state=req.state,
        commodity=req.commodity,
        horizon_days=req.horizon_days,
        use_sarimax=req.use_sarimax,
        future_exogenous=future_exo_dicts
    )

    if result["model_name"] == "NONE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient data to fit time-series forecasting model (minimum 30 observations required)."
        )

    return result


@router.get("/api/v1/forecast/history", tags=["Forecasting"])
def list_forecast_history(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Returns list of previous forecast runs and logged evaluation metrics."""
    return get_forecast_history(db, limit=limit)


@router.get("/api/v1/forecast/{forecast_id}", tags=["Forecasting"])
def get_single_forecast(
    forecast_id: int,
    db: Session = Depends(get_db)
):
    """Returns full details and point predictions for a specific forecast run ID."""
    record = get_forecast_by_id(db, forecast_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Forecast with ID {forecast_id} not found.")
    return record


# =====================================================================
# 5. RESEARCH REPORTS
# =====================================================================

@router.post("/api/v1/reports/generate", response_model=ReportGenerateResponse, tags=["Reports"])
def generate_report_endpoint(db: Session = Depends(get_db)):
    """Triggers end-to-end report generation and exploratory chart generation."""
    return generate_summary_report(db)


@router.get("/api/v1/reports/latest", tags=["Reports"])
def get_latest_report(db: Session = Depends(get_db)):
    """Reads and returns the content of the latest generated research summary report."""
    report_file = OUTPUTS_DIR / "reports" / "summary_report.md"
    if not report_file.exists():
        # Generate on demand if missing
        generate_summary_report(db)

    with open(report_file, "r", encoding="utf-8") as f:
        content = f.read()

    return {
        "filename": report_file.name,
        "path": str(report_file),
        "content_markdown": content
    }
