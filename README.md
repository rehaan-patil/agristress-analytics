# AgriStress Analytics

> **Econometric and Spatial-Temporal Analysis of Farmer Information Demand:**  
> Modeling Kisan Call Centre (KCC) Query Influx Against Commodity Price Spreads and Fuel Inflation Shocks to Forecast Agricultural Advisory Stress.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Statsmodels](https://img.shields.io/badge/Statsmodels-SARIMAX-orange.svg)](https://www.statsmodels.org/)
[![Tests](https://img.shields.io/badge/Tests-19%20Passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-Academic-lightgrey.svg)]()

---

## 1. Problem Statement & Research Context

Public agricultural advisory services in India—predominantly delivered through the **Kisan Call Centre (KCC)** toll-free helpline (1800-180-1551)—serve as the front line for smallholder and commercial farmers seeking guidance on weather contingencies, pest attacks, cultivation practices, and market prices.

While query volumes follow natural agro-climatic rhythms (such as monsoon onset and sowing periods), farmers are also subject to severe economic distress shocks:
- **Commodity Price Volatility:** Sudden crashes in APMC Mandi wholesale modal prices.
- **Wholesale-to-Retail Price Spreads:** Expanding margins between farm-gate realization and consumer retail prices.
- **Fuel Price Shocks:** Rapid increases in High Speed Diesel (HSD) prices, which drive up diesel-pumped irrigation and tractor transport costs.

**AgriStress Analytics** is a 100% pure Python analytical research application designed to run locally. It contains **no web frontend or API overhead**. It harmonizes multi-source government agricultural data, conducts formal econometric hypothesis testing, forecasts future query influx using SARIMAX, benchmarks against a Seasonal Naive baseline on an out-of-sample holdout test period, and classifies operational advisory-service stress into transparent proxy levels (`Normal`, `Elevated`, `High`).

---

## 2. Key Features & Deliverables

- **Pure Local Python Execution:** Clean, intermediate-level Python scripts using Pandas, NumPy, SciPy, Statsmodels, Matplotlib, and Seaborn.
- **One-Command Reproducible Workflow:** Run the complete analytical pipeline via `python main.py` or `python run_pipeline.py`.
- **Data Ingestion & Quality Audit:**
  - Robust CSV readers for KCC call records, Agmarknet wholesale commodity prices, and PPAC retail diesel prices.
  - Automatic column standardization, date format parsing, duplicate detection, and missingness quality reporting.
- **Temporal Alignment & Feature Engineering:**
  - Harmonizes mismatched reporting frequencies (Daily, Weekly, Monthly) onto a continuous timeline without duplicate inflation.
  - Engineers 7-day rolling commodity price volatility, wholesale-to-retail margin spreads, and diesel price momentum.
- **Econometric Hypothesis Testing:**
  - **Hypothesis A:** Pearson correlation test assessing linear association between commodity price percentage returns and query demand.
  - **Hypothesis B:** Non-parametric Mann-Whitney U test evaluating query influx differences during diesel price shock periods.
  - **Hypothesis C:** Spearman rank-order correlation examining wholesale-to-retail price spreads against advisory demand.
- **SARIMAX Time-Series Forecasting & Holdout Validation:**
  - Enforces strict chronological train-test splitting (avoiding future data leakage).
  - Fits seasonal $\text{SARIMAX}(1,1,1)(1,1,0)[7]$ capturing the 7-day weekly call center cycle.
  - Directly benchmarks against a 7-day Seasonal Naive baseline using MAE, RMSE, and zero-safe MAPE.
  - Produces out-of-sample holdout validation plots and 14-day future forecasts with 95% confidence intervals.
- **Transparent Advisory-Stress Classification:**
  - Maps forecasted demand against historical baseline mean and standard deviation:
    - `Normal`: Demand $< \mu + 0.75\sigma$
    - `Elevated`: $\mu + 0.75\sigma \le \text{Demand} < \mu + 1.75\sigma$
    - `High`: $\text{Demand} \ge \mu + 1.75\sigma$
- **Comprehensive Generated Outputs:**
  - `outputs/tables/`: CSV result tables (descriptive stats, correlations, hypothesis test outcomes, regional summaries).
  - `outputs/forecasts/`: CSV tables of 14-day forecast predictions and out-of-sample model evaluation metrics.
  - `outputs/charts/`: 10 publication-quality PNG charts including holdout validation and correlation heatmaps.
  - `outputs/reports/summary_report.md`: Detailed markdown research summary report.

---

## 3. Technology Stack

| Category | Technology | Role |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core application logic |
| **Data Processing** | Pandas, NumPy | Data cleaning, reshaping, and feature engineering |
| **Econometrics & Stats** | SciPy, Statsmodels | Pearson/Spearman tests, Mann-Whitney U, SARIMAX |
| **Visualizations** | Matplotlib, Seaborn | Exploratory time-series plots, heatmaps, and validation figures |
| **Database ORM** | SQLAlchemy 2.0 | Lightweight local persistence via SQLite 3 |
| **Testing** | Pytest | Unit and integration test suite (19 passing tests) |

---

## 4. Repository Structure

```
agristress-analytics/
├── main.py                   # Primary root execution entrypoint
├── run_pipeline.py           # Full research pipeline runner script
├── app/
│   ├── __init__.py           # Package indicator
│   ├── config.py             # Environment variables and path resolution
│   ├── database.py           # SQLAlchemy SQLite engine & session setup
│   ├── models.py             # SQLAlchemy ORM models (KCC, Commodity, Fuel, History)
│   ├── data_processing.py    # CSV ingestion, validation, and feature engineering
│   ├── analysis.py           # Descriptive stats, hypothesis tests, and chart generation
│   └── forecasting.py        # Baseline naive, SARIMAX, and advisory stress evaluation
├── scripts/
│   ├── init_db.py            # Database table creation & reset script
│   ├── generate_demo_data.py # Deterministic synthetic dataset generator (seed=42)
│   ├── import_data.py        # CLI dataset importer
│   └── run_analysis.py       # Analysis execution script
├── tests/
│   ├── test_data_processing.py # CSV validation, alignment, and quality tests
│   ├── test_analysis.py        # Descriptive stats & hypothesis testing tests
│   └── test_forecasting.py     # Metrics, SARIMAX & stress indicator tests
├── data/
│   ├── raw/                  # Directory for raw source CSV files (data.gov.in, Agmarknet, PPAC)
│   ├── processed/            # Harmonized analytical dataset (analytical_dataset.csv)
│   └── synthetic/            # Synthetic demonstration files (clearly identified)
├── outputs/
│   ├── charts/               # Generated PNG visualization plots (10 charts)
│   ├── tables/               # Generated CSV result tables
│   ├── forecasts/            # Generated forecast CSV tables and evaluation metrics
│   └── reports/              # Comprehensive markdown research summary report
├── docs/
│   ├── DATA_SOURCES.md       # Target government schemas and portal documentation
│   ├── METHODOLOGY.md        # Mathematical definitions, SARIMAX, and hypothesis tests
│   └── LIMITATIONS.md        # Scientific boundaries and correlation vs causation
├── requirements.txt          # Pure Python dependencies
└── README.md                 # Complete documentation
```

---

## 5. Quick Start & Execution

### Step 1: Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Run the Complete Research Pipeline
Execute the complete data pipeline, run all statistical tests, generate forecasts, export all CSV tables, and create all charts and the final summary report in one step:
```bash
python main.py
```
*(or `python run_pipeline.py`)*

### Optional Arguments:
```bash
# Force regenerate synthetic demo data and re-import into a clean database:
python main.py --generate-data

# Filter by a specific state or commodity:
python main.py --state Maharashtra --commodity Onion --horizon 21

# Adjust the fuel shock percentage threshold (default: 1.0%):
python main.py --shock-threshold 1.5
```

### Step 3: Inspect Generated Outputs
All outputs are organized in the `outputs/` folder:
- **Research Summary Report:** `outputs/reports/summary_report.md`
- **Charts:** `outputs/charts/*.png`
- **Result Tables:** `outputs/tables/*.csv`
- **Forecast Predictions & Metrics:** `outputs/forecasts/*.csv`

---

## 6. Running Tests

Execute the complete test suite with Pytest:
```bash
python -m pytest
```

All 19 tests run locally in ~5 seconds with zero warnings.

---

## 7. Scientific Responsibility & Viva Notes

When defending this project during an academic viva:
1. **Explain the variables:** $Q_t$ (daily queries), $P_t^W$ (wholesale mandi price), $D_t$ (diesel price), $S_t = P_t^R - P_t^W$ (price spread).
2. **Explain why correlation $\neq$ causation:** External factors like monsoon arrival simultaneously affect farm operations and market arrivals. Correlation demonstrates association in this sample, not economic causation.
3. **Defend chronological train/test splitting:** Explain that standard random K-fold shuffling causes lookahead bias in time series. We use a chronological split (first 700 days train, last 30 days test).
4. **Explain SARIMAX parameters:** $(1,1,1)(1,1,0)[7]$ differences non-seasonal trend ($d=1$) and weekly 7-day cyclicality ($D=1, s=7$).
5. **Explain the stress classification:** It is a transparent operational heuristic derived from historical standard deviations ($\mu + 0.75\sigma, \mu + 1.75\sigma$), not an official staffing mandate.
6. **Synthetic vs. Real Data:** Be transparent that demo runs use reproducible synthetic data (`seed=42`) until real-world data feeds from data.gov.in, Agmarknet, and PPAC are imported.

Consult the documentation in `docs/`:
- [DATA_SOURCES.md](docs/DATA_SOURCES.md)
- [METHODOLOGY.md](docs/METHODOLOGY.md)
- [LIMITATIONS.md](docs/LIMITATIONS.md)

---

## 8. Author & License

- **Author:** Rehaan Patil
- **GitHub:** [rehaan-patil](https://github.com/rehaan-patil)
- **Course:** First-Year Engineering / Semester Project
- **License:** Academic Use Only
