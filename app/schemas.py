"""
Pydantic data schemas for API requests and responses.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    database: str
    environment: str
    timestamp: str


class DatasetCountSummary(BaseModel):
    table_name: str
    total_records: int
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    states_count: int
    is_synthetic: bool = False


class DatasetStatusResponse(BaseModel):
    status: str
    datasets: Dict[str, DatasetCountSummary]
    ready_for_analysis: bool
    notes: List[str]


class OverviewResponse(BaseModel):
    kcc_total_queries: int
    commodity_records: int
    fuel_records: int
    date_range: Dict[str, Optional[str]]
    states_covered: List[str]
    is_synthetic: bool


class ImportResultResponse(BaseModel):
    dataset_type: str
    filename: str
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    duplicate_rows: int
    status: str
    errors: List[str] = []


class SummaryStatsItem(BaseModel):
    variable: str
    count: int
    mean: float
    std: float
    min: float
    median: float
    max: float


class AnalysisSummaryResponse(BaseModel):
    sample_period: Dict[str, Optional[str]]
    total_observations: int
    descriptive_statistics: List[SummaryStatsItem]
    insights: List[str]


class TrendPoint(BaseModel):
    date: str
    query_count: Optional[float] = None
    wholesale_price: Optional[float] = None
    diesel_price: Optional[float] = None


class RegionalSummary(BaseModel):
    state: str
    total_queries: int
    avg_daily_queries: float
    observation_days: int


class CorrelationPair(BaseModel):
    variable_x: str
    variable_y: str
    pearson_r: float
    spearman_rho: float
    sample_size: int
    note: str


class HypothesisTestRequest(BaseModel):
    state: Optional[str] = None
    commodity: Optional[str] = None
    diesel_shock_threshold_pct: float = Field(default=2.0)


class SingleHypothesisResult(BaseModel):
    hypothesis_code: str
    title: str
    null_hypothesis: str
    alternative_hypothesis: str
    test_used: str
    sample_size: int
    test_statistic: Optional[float] = None
    p_value: Optional[float] = None
    effect_size: Optional[float] = None
    significance_level: float = 0.05
    reject_null: bool
    verdict_plain_english: str
    limitations: str


class HypothesisReportResponse(BaseModel):
    run_date: str
    state_filter: Optional[str]
    commodity_filter: Optional[str]
    results: List[SingleHypothesisResult]
    disclaimer: str


class ExogenousScenario(BaseModel):
    date: str
    commodity_price: Optional[float] = None
    diesel_price: Optional[float] = None


class ForecastRequest(BaseModel):
    state: Optional[str] = None
    commodity: Optional[str] = None
    horizon_days: int = Field(default=14, ge=1, le=90)
    use_sarimax: bool = True
    future_exogenous: Optional[List[ExogenousScenario]] = None


class ForecastPoint(BaseModel):
    date: str
    predicted_demand: float
    lower_bound: float
    upper_bound: float
    stress_category: str


class StressEvaluation(BaseModel):
    category: str
    historical_baseline_mean: float
    elevated_threshold: float
    high_threshold: float
    explanation: str
    disclaimer: str


class ForecastResponse(BaseModel):
    forecast_id: Optional[int] = None
    model_name: str
    state: Optional[str] = None
    target: str = "query_count"
    train_start: str
    train_end: str
    test_start: Optional[str] = None
    test_end: Optional[str] = None
    horizon_days: int
    mae: Optional[float] = None
    rmse: Optional[float] = None
    mape: Optional[float] = None
    predictions: List[ForecastPoint]
    stress_assessment: StressEvaluation
    warnings: List[str] = []


class ReportGenerateResponse(BaseModel):
    report_filename: str
    report_path: str
    generated_at: str
    chart_paths: List[str]
    status: str
