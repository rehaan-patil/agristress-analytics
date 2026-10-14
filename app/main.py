"""
Main FastAPI Application Entrypoint for AgriStress Analytics.

Provides high-performance, asynchronous REST API endpoints for:
  - Database health and dataset status
  - CSV upload and validation (KCC queries, commodity mandi prices, diesel fuel prices)
  - Statistical and econometric analysis (descriptive statistics, regional comparisons, correlations)
  - Formal hypothesis testing (Pearson, Mann-Whitney U, Spearman)
  - SARIMAX time-series forecasting and advisory-stress classification
  - Visualizations and research summary reporting
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import OUTPUTS_DIR
from app.database import Base, engine
from app.api import router as api_router
import app.models  # Register models with SQLAlchemy metadata

# Ensure database tables exist automatically on application startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AgriStress Analytics Backend API",
    description=(
        "Research SaaS Backend for Econometric and Spatial-Temporal Analysis of Farmer Information Demand. "
        "Models Kisan Call Centre (KCC) Query Influx against Agricultural Commodity Price Spreads and "
        "Fuel Inflation Shocks to Forecast Agricultural Advisory Stress."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable Cross-Origin Resource Sharing (CORS) for future web frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount outputs/charts directory to serve static plot images
charts_dir = OUTPUTS_DIR / "charts"
charts_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/charts", StaticFiles(directory=str(charts_dir)), name="charts")

# Include all API route handlers
app.include_router(api_router)


@app.get("/", tags=["Root"])
def root():
    """Welcome endpoint providing navigation links to Swagger documentation and health checks."""
    return {
        "project": "AgriStress Analytics",
        "description": "Python-only Research SaaS Backend for Advisory Stress Forecasting",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health",
        "author_academic_context": "Semester Project — First-Year Engineering Implementation"
    }


if __name__ == "__main__":
    import uvicorn
    from app.config import HOST, PORT
    print(f"Starting AgriStress Analytics API on http://{HOST}:{PORT}")
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
