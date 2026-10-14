# AgriStress Analytics

> **Econometric and Spatial-Temporal Analysis of Farmer Information Demand:**
> Modeling Kisan Call Centre (KCC) Query Influx Against Commodity Price Spreads and Fuel Inflation Shocks to Forecast Agricultural Advisory Stress.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Statsmodels](https://img.shields.io/badge/Statsmodels-SARIMAX-orange.svg)](https://www.statsmodels.org/)
[![Tests](https://img.shields.io/badge/Tests-26%20Passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-Academic-lightgrey.svg)]()

---

## 1. Problem Statement & Research Context

Public agricultural advisory services in India—predominantly delivered through the **Kisan Call Centre (KCC)** toll-free helpline (1800-180-1551)—serve as the front line for smallholder and commercial farmers seeking guidance on weather contingencies, pest attacks, cultivation practices, and market prices.

While query volumes follow natural agro-climatic rhythms (such as monsoon onset and sowing periods), farmers are also subject to severe economic distress shocks:
- **Commodity Price Volatility:** Sudden crashes in APMC Mandi wholesale modal prices.
- **Wholesale-to-Retail Price Spreads:** Expanding margins between farm-gate realization and consumer retail prices.
- **Fuel Price Shocks:** Rapid increases in High Speed Diesel (HSD) prices, which drive up diesel-pumped irrigation and tractor transport costs.

**AgriStress Analytics** is a Python-only research backend that harmonizes multi-source government agricultural data, conducts formal econometric hypothesis testing, forecasts future query influx using SARIMAX, and classifies operational advisory-service stress into transparent levels (`Normal`, `Elevated`, `High`).

---

## 2. Key Features

- **Multi-Source Data Ingestion & Validation:**
  - Robust CSV readers for KCC call records, Agmarknet wholesale commodity prices, and PPAC retail diesel prices.
  - Automatic column standardization, date format parsing, and duplicate row detection.
- **Temporal Alignment & Feature Engineering:**
  - Harmonizes mismatched reporting frequencies onto a continuous daily grid.
  - Engineers 7-day rolling commodity price volatility, wholesale-to-retail margin spreads, and diesel price momentum.
- **Defensible Econometric Hypothesis Testing:**
  - **Hypothesis A:** Pearson correlation test assessing linear association between commodity price percentage returns and query demand.
  - **Hypothesis B:** Non-parametric Mann-Whitney U test evaluating query influx differences during diesel price shock periods ($|\%\Delta D_t| \ge 2\%$).
  - **Hypothesis C:** Spearman rank-order correlation examining wholesale-to-retail price spreads against advisory demand.
- **SARIMAX Time-Series Forecasting:**
  - Enforces strict chronological train-test splitting (80% train, 20% test) to prevent future lookahead bias.
  - Fits seasonal $\text{SARIMAX}(1,1,1)(1,1,0)[7]$ capturing the 7-day weekly call center cycle.
  - Directly benchmarks against a 7-day Seasonal Naive baseline using MAE, RMSE, and zero-safe MAPE.
  - Computes 95% confidence intervals and clips negative predictions.
- **Transparent Advisory-Stress Classification:**
  - Maps forecasted demand against historical baseline mean and standard deviation:
    - `Normal`: Demand $< \mu + 0.75\sigma$
    - `Elevated`: $\mu + 0.75\sigma \le \text{Demand} < \mu + 1.75\sigma$
    - `High`: $\text{Demand} \ge \mu + 1.75\sigma$
  - Discloses forecast uncertainty when confidence bounds cross into higher operational categories.
- **FastAPI REST API:**
  - 16 interactive endpoints for health, ingestion, statistical summaries, hypothesis testing, forecasting, and reporting.
  - Local Swagger documentation at `/docs`.
- **Automated Reporting & Visualization:**
  - Exports 9 publication-grade charts to `outputs/charts/` and a comprehensive markdown report to `outputs/reports/summary_report.md`.

---

## 3. Technology Stack

| Category | Technology | Role |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core application logic |
| **Data Processing** | Pandas, NumPy | Data cleaning, reshaping, and feature engineering |
| **Econometrics & Stats** | SciPy, Statsmodels | Pearson/Spearman tests, Mann-Whitney U, SARIMAX |
| **Visualizations** | Matplotlib, Seaborn | Exploratory time-series plots and heatmaps |
| **API Framework** | FastAPI, Uvicorn | High-performance asynchronous REST API |
| **Request Validation** | Pydantic v2 | Schema validation and serialization |
| **Database ORM** | SQLAlchemy 2.0 | Multi-engine persistence (SQLite / PostgreSQL) |
| **Local Storage** | SQLite 3 | Default zero-configuration local database |
| **Testing** | Pytest | Unit and integration test suite |
| **Containerization** | Docker | Production container image |
| **Deployment** | Render | Cloud PaaS deployment specification |

---

## 4. Repository Structure

```
agristress-analytics/
├── app/
│   ├── __init__.py           # Package indicator
│   ├── main.py               # FastAPI application entrypoint & static mount
│   ├── config.py             # Environment variables and path resolution
│   ├── database.py           # SQLAlchemy engine & session dependency
│   ├── models.py             # SQLAlchemy ORM models (KCC, Commodity, Fuel, History)
│   ├── schemas.py            # Pydantic request and response models
│   ├── data_processing.py    # CSV ingestion, validation, and feature engineering
│   ├── analysis.py           # Descriptive stats, hypothesis tests, and chart generation
│   ├── forecasting.py        # Baseline naive, SARIMAX, and advisory stress evaluation
│   └── api.py                # FastAPI route handlers
├── scripts/
│   ├── init_db.py            # Database table creation script
│   ├── generate_demo_data.py # Deterministic synthetic dataset generator (seed=42)
│   ├── import_data.py        # CLI dataset importer
│   └── run_analysis.py       # End-to-end analytical pipeline runner
├── tests/
│   ├── __init__.py
│   ├── test_data_processing.py # CSV validation & alignment tests
│   ├── test_analysis.py        # Descriptive stats & hypothesis testing tests
│   ├── test_forecasting.py     # Metrics, SARIMAX & stress indicator tests
│   └── test_api.py             # REST API endpoint integration tests
├── data/
│   ├── raw/                  # Ingested raw source CSV files
│   ├── processed/            # Harmonized analytical dataset
│   └── synthetic/            # Synthetic demonstration files
├── outputs/
│   ├── charts/               # Generated PNG visualization plots
│   └── reports/              # Generated markdown research reports
├── docs/
│   ├── DATA_SOURCES.md       # Target government schemas and portal documentation
│   ├── METHODOLOGY.md        # Mathematical definitions, SARIMAX, and hypothesis tests
│   └── LIMITATIONS.md        # Scientific boundaries and correlation vs causation
├── .env.example              # Sample environment configuration
├── .gitignore                # Git exclusion rules
├── requirements.txt          # Python dependencies
├── Dockerfile                # Production container specification
├── render.yaml               # Render Cloud deployment blueprint
└── README.md                 # Project guide
```

---

## 5. Getting Started Locally

### Step 1: Clone the Repository & Setup Environment
```bash
git clone https://github.com/rehaan-patil/agristress-analytics.git
cd agristress-analytics

# Create and activate a virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
```bash
# Copy example configuration (defaults to local SQLite database)
copy .env.example .env    # On Windows
# or: cp .env.example .env # On Linux/macOS
```

### Step 4: Initialize the Database
```bash
python scripts/init_db.py
```

---

## 6. Demonstration Workflow

The entire analytical pipeline can be demonstrated offline using deterministic demo data:

### 1. Generate Synthetic Datasets
```bash
python scripts/generate_demo_data.py
```
*Generates 730 days of synthetic records for KCC queries, mandi prices, and diesel fuel prices in `data/synthetic/`.*

### 2. Ingest Data into SQLite
```bash
# Ingest all demo datasets
python scripts/import_data.py --all

# Inspect ingestion status
python scripts/import_data.py --status
```

### 3. Run the End-to-End Analysis Pipeline
```bash
python scripts/run_analysis.py
```
This script executes:
1. Harmonization into `data/processed/analytical_dataset.csv`.
2. Descriptive statistical summaries across variables.
3. Generation of 8 exploratory charts in `outputs/charts/`.
4. Econometric tests for Hypothesis A, B, and C.
5. Chronological SARIMAX model training, evaluation, and 14-day advisory stress forecasting.
6. Compilation of the full research report in `outputs/reports/summary_report.md`.

---

## 7. Starting the FastAPI Server

Start the REST API server using Uvicorn:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open your browser and navigate to:
- **Interactive Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc UI:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 8. REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check verifying database connectivity |
| `GET` | `/api/v1/datasets/status` | Current table counts, date bounds, and readiness |
| `GET` | `/api/v1/overview` | Total inquiries, recorded commodity/fuel observations |
| `POST` | `/api/v1/data/import/kcc` | Upload and validate KCC query CSV |
| `POST` | `/api/v1/data/import/commodity` | Upload and validate Mandi commodity price CSV |
| `POST` | `/api/v1/data/import/fuel` | Upload and validate Diesel fuel price CSV |
| `GET` | `/api/v1/analysis/summary` | Descriptive statistics (mean, std, median, min, max) |
| `GET` | `/api/v1/analysis/trends` | Chronological daily observations for frontend charting |
| `GET` | `/api/v1/analysis/regions` | Regional query breakdown across states |
| `GET` | `/api/v1/analysis/correlations` | Pairwise Pearson & Spearman correlation matrix |
| `POST` | `/api/v1/analysis/hypothesis-tests` | Run Hypothesis A, B, and C statistical tests |
| `POST` | `/api/v1/forecast` | Execute SARIMAX forecast & advisory stress rating |
| `GET` | `/api/v1/forecast/history` | List previous forecast runs and evaluation metrics |
| `GET` | `/api/v1/forecast/{forecast_id}` | Detailed forecast predictions and confidence intervals |
| `POST` | `/api/v1/reports/generate` | Trigger report and chart generation pipeline |
| `GET` | `/api/v1/reports/latest` | Read markdown text of latest research summary |

---

## 9. Running Tests

The test suite covers CSV validation, date parsing, query aggregation, data alignment, hypothesis testing on known examples, chronological splitting, SARIMAX fitting, and REST API endpoints.

Execute all tests with Pytest:
```bash
python -m pytest -v
```

All 26 tests run in under 10 seconds.

---

## 10. Deployment

### Option A: Render Cloud Deployment
1. Connect your GitHub repository to [Render](https://render.com/).
2. Create a new **Web Service** selecting the repository.
3. Render automatically detects `render.yaml`:
   - **Runtime:** Python 3.10
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt && python scripts/init_db.py && python scripts/generate_demo_data.py && python scripts/import_data.py --all`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. The service will deploy with `/health` and `/docs` accessible on your public `.onrender.com` URL.

### Option B: Docker Container Deployment
```bash
# Build the Docker image
docker build -t agristress-analytics .

# Run the container
docker run -p 8000:8000 agristress-analytics
```

---

## 11. Scientific Responsibility & Viva Notes

When defending this project during an academic viva:
1. **Explain the variables:** $Q_t$ (daily queries), $P_t^W$ (wholesale mandi price), $D_t$ (diesel price), $S_t = P_t^R - P_t^W$ (price spread).
2. **Explain why correlation $\neq$ causation:** External factors like monsoon arrival simultaneously affect farm operations and market arrivals.
3. **Defend chronological train/test splitting:** Explain that standard random K-fold shuffling causes lookahead bias in time series.
4. **Explain SARIMAX parameters:** $(1,1,1)(1,1,0)[7]$ differences non-seasonal trend ($d=1$) and weekly 7-day cyclicality ($D=1, s=7$).
5. **Explain the stress classification:** It is a transparent operational heuristic ($\mu + 0.75\sigma, \mu + 1.75\sigma$), not an official staffing mandate.
6. **Synthetic vs. Real Data:** Be transparent that demo runs use reproducible synthetic data (`seed=42`) until real-world data feeds are plugged in.

Consult the documentation in `docs/`:
- [DATA_SOURCES.md](docs/DATA_SOURCES.md)
- [METHODOLOGY.md](docs/METHODOLOGY.md)
- [LIMITATIONS.md](docs/LIMITATIONS.md)

---

## 12. Author & License

- **Author:** Rehaan Patil
- **GitHub:** [rehaan-patil](https://github.com/rehaan-patil)
- **Course:** First-Year Engineering / Semester Project
- **License:** Academic Use Only
