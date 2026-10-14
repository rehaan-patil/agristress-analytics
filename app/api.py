"""
FastAPI route handlers for AgriStress Analytics.
Direct, understandable endpoints that call data_processing, analysis, and forecasting.
"""
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import math

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import OUTPUTS_DIR
from app.schemas import (
    HealthResponse, DatasetStatusResponse, OverviewResponse, ImportResultResponse,
    AnalysisSummaryResponse, TrendPoint, RegionalSummary, CorrelationPair,
    HypothesisTestRequest, HypothesisReportResponse, ForecastRequest, ForecastResponse, ReportGenerateResponse
)
from app.data_processing import (
    import_kcc_csv, import_commodity_csv, import_fuel_csv,
    get_dataset_status, build_analytical_dataset
)
from app.analysis import (
    get_overview_stats, get_descriptive_summary, get_regional_summary,
    get_correlations, run_hypothesis_tests, generate_summary_report
)
from app.forecasting import generate_forecast, get_forecast_history, get_forecast_by_id

router = APIRouter()


# --- Health & Status ---

@router.get("/health", response_model=HealthResponse, tags=["Health"])
def check_health(db: Session = Depends(get_db)):
    return {"status": "healthy", "database": "connected", "environment": "local_or_render", "timestamp": datetime.utcnow().isoformat()}


@router.get("/api/v1/datasets/status", response_model=DatasetStatusResponse, tags=["Datasets"])
def get_status(db: Session = Depends(get_db)):
    return get_dataset_status(db)


@router.get("/api/v1/overview", response_model=OverviewResponse, tags=["Overview"])
def get_overview(db: Session = Depends(get_db)):
    return get_overview_stats(db)


# --- Data Import ---

def check_csv_extension(file: UploadFile):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail=f"Invalid file type for '{file.filename}'. Only .csv files are supported.")


@router.post("/api/v1/data/import/kcc", response_model=ImportResultResponse, tags=["Data Ingestion"])
def upload_kcc_data(file: UploadFile = File(...), is_synthetic: bool = Query(False), db: Session = Depends(get_db)):
    check_csv_extension(file)
    res = import_kcc_csv(file.file, db, filename=file.filename, is_synthetic=is_synthetic)
    if res["status"] == "FAILED":
        raise HTTPException(status_code=400, detail=res["errors"])
    return res


@router.post("/api/v1/data/import/commodity", response_model=ImportResultResponse, tags=["Data Ingestion"])
def upload_commodity_data(file: UploadFile = File(...), is_synthetic: bool = Query(False), db: Session = Depends(get_db)):
    check_csv_extension(file)
    res = import_commodity_csv(file.file, db, filename=file.filename, is_synthetic=is_synthetic)
    if res["status"] == "FAILED":
        raise HTTPException(status_code=400, detail=res["errors"])
    return res


@router.post("/api/v1/data/import/fuel", response_model=ImportResultResponse, tags=["Data Ingestion"])
def upload_fuel_data(file: UploadFile = File(...), is_synthetic: bool = Query(False), db: Session = Depends(get_db)):
    check_csv_extension(file)
    res = import_fuel_csv(file.file, db, filename=file.filename, is_synthetic=is_synthetic)
    if res["status"] == "FAILED":
        raise HTTPException(status_code=400, detail=res["errors"])
    return res


# --- Analysis ---

@router.get("/api/v1/analysis/summary", response_model=AnalysisSummaryResponse, tags=["Analysis"])
def get_summary(state: Optional[str] = None, commodity: Optional[str] = None, db: Session = Depends(get_db)):
    df = build_analytical_dataset(db, state=state, commodity=commodity, export_csv=False)
    if df.empty:
        raise HTTPException(status_code=404, detail="No analytical data found. Import data first.")
    return get_descriptive_summary(df)


@router.get("/api/v1/analysis/trends", response_model=List[TrendPoint], tags=["Analysis"])
def get_trends(state: Optional[str] = None, commodity: Optional[str] = None, limit: int = 60, db: Session = Depends(get_db)):
    df = build_analytical_dataset(db, state=state, commodity=commodity, export_csv=False)
    if df.empty:
        return []
    pts = []
    for _, r in df.tail(limit).iterrows():
        pts.append({
            "date": r["observation_date"].strftime("%Y-%m-%d"),
            "query_count": float(r["query_count"]) if pd_valid(r["query_count"]) else None,
            "wholesale_price": float(r["wholesale_price"]) if pd_valid(r["wholesale_price"]) else None,
            "diesel_price": float(r["diesel_price"]) if pd_valid(r["diesel_price"]) else None,
        })
    return pts


def pd_valid(v):
    return v is not None and not (isinstance(v, float) and math.isnan(v))


@router.get("/api/v1/analysis/regions", response_model=List[RegionalSummary], tags=["Analysis"])
def get_regions(db: Session = Depends(get_db)):
    return get_regional_summary(db)


@router.get("/api/v1/analysis/correlations", response_model=List[CorrelationPair], tags=["Analysis"])
def get_correlations_route(state: Optional[str] = None, commodity: Optional[str] = None, db: Session = Depends(get_db)):
    df = build_analytical_dataset(db, state=state, commodity=commodity, export_csv=False)
    return get_correlations(df)


@router.post("/api/v1/analysis/hypothesis-tests", response_model=HypothesisReportResponse, tags=["Analysis"])
def execute_hypothesis_tests(params: HypothesisTestRequest, db: Session = Depends(get_db)):
    df = build_analytical_dataset(db, state=params.state, commodity=params.commodity, export_csv=False)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data available for hypothesis tests.")
    res = run_hypothesis_tests(df, diesel_shock_threshold_pct=params.diesel_shock_threshold_pct)
    return {"run_date": res["run_date"], "state_filter": params.state, "commodity_filter": params.commodity, "results": res["results"], "disclaimer": res["disclaimer"]}


# --- Forecasting ---

@router.post("/api/v1/forecast", response_model=ForecastResponse, tags=["Forecasting"])
def run_forecast(req: ForecastRequest, db: Session = Depends(get_db)):
    exo = [e.dict() for e in req.future_exogenous] if req.future_exogenous else None
    res = generate_forecast(db, state=req.state, commodity=req.commodity, horizon_days=req.horizon_days, use_sarimax=req.use_sarimax, future_exogenous=exo)
    if res["model_name"] == "NONE":
        raise HTTPException(status_code=400, detail="Insufficient data to forecast (minimum 30 rows required).")
    return res


@router.get("/api/v1/forecast/history", tags=["Forecasting"])
def list_history(limit: int = 10, db: Session = Depends(get_db)):
    return get_forecast_history(db, limit=limit)


@router.get("/api/v1/forecast/{forecast_id}", tags=["Forecasting"])
def get_forecast(forecast_id: int, db: Session = Depends(get_db)):
    res = get_forecast_by_id(db, forecast_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Forecast {forecast_id} not found.")
    return res


# --- Reports ---

@router.post("/api/v1/reports/generate", response_model=ReportGenerateResponse, tags=["Reports"])
def generate_report(db: Session = Depends(get_db)):
    return generate_summary_report(db)


@router.get("/api/v1/reports/latest", tags=["Reports"])
def get_latest_report(db: Session = Depends(get_db)):
    rep_file = OUTPUTS_DIR / "reports" / "summary_report.md"
    if not rep_file.exists():
        generate_summary_report(db)
    return {"filename": rep_file.name, "path": str(rep_file), "content_markdown": rep_file.read_text(encoding="utf-8")}
