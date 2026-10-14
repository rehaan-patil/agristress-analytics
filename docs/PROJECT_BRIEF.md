# AgriStress Analytics — Complete Project Brief

> **All-in-One Executive Summary & Quick Reference**  
> Everything you need to know about the AgriStress Analytics backend in one concise, readable document.

---

## 1. Project at a Glance

| Item | Details |
| :--- | :--- |
| **Project Name** | **AgriStress Analytics** |
| **Domain** | Agriculture, Agri-FinTech, Econometrics, Public Advisory Services |
| **Problem Statement** | Modeling Kisan Call Centre (KCC) Query Influx against Agricultural Commodity Price Spreads and Fuel Inflation Shocks to Forecast Agricultural Advisory Stress. |
| **Core Objective** | Investigate whether economic distress shocks (price crashes, retail markups, diesel hikes) associate with farmer advisory demand, and forecast future call volume to manage call-centre operational stress. |
| **Target Audience** | Call centre administrators, agricultural policy planners, researchers, and agronomists. |
| **Current Status** | Backend 100% complete, verified with 26 automated tests, running on Python 3.10 + SQLite + FastAPI. |

---

## 2. The Real-World Problem in Plain English

India has over 140 million farming households. When farming conditions are calm, call volume to the national **Kisan Call Centre (1800-180-1551)** follows routine seasonal farming cycles.

However, when sudden economic shocks occur:
1. **Commodity Price Crashes:** Wholesale prices at the local APMC Mandi drop rapidly (e.g., onions falling from ₹25/kg to ₹8/kg).
2. **Wholesale-to-Retail Spreads:** Urban consumers pay high retail prices (₹50/kg) while farmers receive low farm-gate realizations (₹15/kg).
3. **Diesel Fuel Shocks:** Rapid increases in diesel fuel prices (e.g., $\ge 2\%$ hike) immediately increase tractor plowing and diesel-pumped irrigation costs.

When hit by these shocks, farmers experience acute uncertainty and call the Kisan Call Centre for guidance on crop storage, alternate markets, pest management, and government subsidies. 

**Advisory Stress** refers to the resulting operational strain on the call centre (call queues, long wait times, operator overload).

---

## 3. Technology Stack & Why We Chose It

| Layer | Tool | Why We Chose It |
| :--- | :--- | :--- |
| **Language** | Python 3.10 | Standard language for scientific data science and backend APIs. |
| **Data Processing** | Pandas & NumPy | Fast tabular data alignment, date indexing, and vectorized math. |
| **Statistical Tests** | SciPy | Robust, peer-reviewed tests (`pearsonr`, `mannwhitneyu`, `spearmanr`). |
| **Time-Series Forecast** | Statsmodels | Industry-standard `SARIMAX` implementation for seasonal time series. |
| **Web API** | FastAPI & Uvicorn | Lightweight, high performance, automatic interactive Swagger UI (`/docs`). |
| **Database** | SQLite + SQLAlchemy | Zero-configuration local database (`agristress.db`), swappable to PostgreSQL. |
| **Visualizations** | Matplotlib & Seaborn | Headless server-side generation of 9 analytical charts into PNG format. |
| **Testing** | Pytest | Fast automated testing (all 26 tests pass in ~6 seconds). |

---

## 4. Complete Architecture & Data Flow

```
Raw CSV Files (KCC Calls, Mandi Prices, Diesel Rates)
       │
       ▼
app/data_processing.py ──► Validates columns, cleans dates, drops duplicate rows
       │
       ▼
SQLite Database (agristress.db) ──► Stored in 5 SQLAlchemy ORM tables
       │
       ▼
Harmonization & Feature Engineering ──► Continuous daily calendar grid (730 days)
       │                                 Computes: Price returns, volatility, spreads
       ├─────────────────────────────────┬─────────────────────────────────┐
       ▼                                 ▼                                 ▼
app/analysis.py                  app/forecasting.py                 app/api.py
- Descriptive stats              - 80/20 Chronological Split        - 16 REST endpoints
- 3 Hypothesis Tests             - 7-Day Seasonal Naive             - Swagger Docs (/docs)
- 8 Visual Charts (PNG)          - SARIMAX(1,1,1)(1,1,0)[7]         - Interactive JSON
- summary_report.md              - Advisory Stress Rating
```

---

## 5. File Directory Quick Map

```
d:/python-capstone/
├── app/
│   ├── config.py             # Environment variables and directory paths
│   ├── database.py           # SQLAlchemy database connection and SessionLocal
│   ├── models.py             # 5 Database tables (KCC, Commodity, Fuel, Import, Forecast)
│   ├── schemas.py            # Pydantic request/response validation schemas
│   ├── data_processing.py    # CSV cleaning, deduplication, and continuous grid merge
│   ├── analysis.py           # Statistics, 3 hypothesis tests, and 8 chart generators
│   ├── forecasting.py        # Baseline naive, SARIMAX model, and advisory stress logic
│   ├── api.py                # 16 FastAPI route handlers
│   └── main.py               # Server startup, CORS configuration, and static charts mount
├── scripts/
│   ├── init_db.py            # Creates SQLite database tables
│   ├── generate_demo_data.py # Generates 730 days of deterministic demo data (seed=42)
│   ├── import_data.py        # CLI importer for CSV files
│   └── run_analysis.py       # Full pipeline runner (generates charts, report, and forecast)
├── tests/                    # 26 automated unit and integration tests
├── outputs/charts/           # 9 generated visualization images (.png)
├── outputs/reports/          # Generated summary_report.md
└── docs/                     # Comprehensive handover guides and API references
```

---

## 6. Database Schema in One Table

| Table Name | Primary Purpose | Key Columns |
| :--- | :--- | :--- |
| **`kcc_observations`** | Daily KCC farmer inquiries | `observation_date`, `state`, `district`, `query_type`, `query_count` |
| **`commodity_observations`** | Mandi crop prices & arrivals | `observation_date`, `state`, `commodity`, `wholesale_price`, `retail_price` |
| **`fuel_observations`** | Retail diesel fuel prices | `observation_date`, `state`, `diesel_price` (INR/Litre) |
| **`import_history`** | Ingestion audit trail | `dataset_type`, `filename`, `total_records`, `accepted_records`, `status` |
| **`forecast_history`** | Forecast run archive | `model_name`, `horizon_days`, `mae`, `rmse`, `stress_category`, `details_json` |

---

## 7. Mathematical Formulas & Features

1. **Price Percentage Return:**
   $$\% \Delta P_t = \left(\frac{P_t - P_{t-1}}{P_{t-1}}\right) \times 100$$
2. **7-Day Price Volatility:**
   $$\sigma_{7,t} = \sqrt{\frac{1}{6} \sum_{i=0}^6 (P_{t-i} - \bar{P}_{7,t})^2}$$
3. **Wholesale-to-Retail Spread:**
   $$S_t = P_t^{\text{retail}} - P_t^{\text{wholesale}}$$
4. **Diesel Price Shock Definition:**
   $$\text{Shock} = 1 \quad \text{if } |\% \Delta \text{Diesel}_t| \ge 2.0\%$$

---

## 8. The Three Hypothesis Tests

| Code | Hypothesis Tested | Statistical Test | Purpose |
| :--- | :--- | :--- | :--- |
| **HYP-A** | Commodity price movements vs. KCC call influx | **Pearson Correlation ($r$)** | Tests if price percentage returns linearly correlate with call volume. |
| **HYP-B** | Diesel price shocks vs. normal price periods | **Mann-Whitney U Test** | Non-parametric test comparing query distributions on shock days vs. normal days. |
| **HYP-C** | Wholesale-to-retail margin spread vs. call influx | **Spearman Rank ($\rho_s$)** | Tests if wider middleman markups associate with increased farmer inquiries. |

*Significance rule:* Reject null hypothesis ($H_0$) if $p < 0.05$.  
*Scientific boundary:* Statistical correlation proves an association; it **does not prove causation**.

---

## 9. SARIMAX Forecasting & Advisory Stress

### Model Configuration
$$\text{SARIMAX}(p=1, d=1, q=1) \times (P=1, D=1, Q=0)_{s=7}$$
- **$s=7$ (Weekly Seasonality):** Captures the strong 7-day cyclicality of call centres (high volume Monday–Friday, low volume Sunday).
- **Chronological Split:** First 80% of days for training, final 20% for testing (strictly no random shuffling to prevent future lookahead bias).
- **Benchmark Baseline:** Compared directly against a **7-Day Seasonal Naive Baseline** ($\hat{y}_t = y_{t-7}$).
- **Evaluation Metrics:** MAE (Mean Absolute Error), RMSE (Root Mean Squared Error), and zero-safe MAPE (%).

### Advisory Stress Thresholds
Forecasted call volume ($\hat{Q}$) is compared to historical baseline mean ($\mu$) and standard deviation ($\sigma$):
- **`Normal`**: $\hat{Q} < \mu + 0.75\sigma$
- **`Elevated`**: $\mu + 0.75\sigma \le \hat{Q} < \mu + 1.75\sigma$
- **`High`**: $\hat{Q} \ge \mu + 1.75\sigma$

---

## 10. How to Run the Project (4 Commands)

Run these directly in the VS Code Terminal:

```bash
# 1. Generate 730 days of synthetic demonstration data (seed=42)
python scripts/generate_demo_data.py

# 2. Ingest the datasets into SQLite database
python scripts/import_data.py --all

# 3. Run the analytical pipeline (generates 9 charts and research report)
python scripts/run_analysis.py

# 4. Start the interactive FastAPI server
python -m uvicorn app.main:app --reload
```

- **Interactive API Documentation (Swagger):** Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Run All Automated Tests:** `python -m pytest -v` (26 passed).

---

## 11. Generated Charts & Outputs

All charts are saved as high-resolution PNGs in `outputs/charts/`:
1. `query_demand_over_time.png` — Daily call volume and 14-day rolling trend.
2. `seasonality_patterns.png` — Call averages broken down by day-of-week and month.
3. `commodity_price_trends.png` — Wholesale mandi prices (INR/Quintal) over time.
4. `diesel_price_trends.png` — Retail diesel prices (INR/Litre) showing price revisions.
5. `price_spreads.png` — Wholesale vs. retail prices with margin spread shaded.
6. `query_vs_economic.png` — Dual-axis chart comparing calls against crop prices.
7. `regional_queries.png` — Comparative bar chart across states.
8. `correlation_heatmap.png` — Heatmap of Pearson correlation coefficients.
9. `forecast_evaluation.png` — Historical actuals vs. SARIMAX forecast with 95% confidence intervals.
10. `outputs/reports/summary_report.md` — Complete analytical research report.

---

## 12. REST API Summary (16 Endpoints)

| Group | Method & Path | What It Does |
| :--- | :--- | :--- |
| **System** | `GET /health` | Health check verifying database connection. |
| | `GET /api/v1/datasets/status` | Table record counts, date ranges, and analytical readiness. |
| | `GET /api/v1/overview` | Total queries, commodity rows, fuel rows, and states. |
| **Ingestion** | `POST /api/v1/data/import/kcc` | Upload & validate KCC query CSV file. |
| | `POST /api/v1/data/import/commodity` | Upload & validate APMC Mandi price CSV file. |
| | `POST /api/v1/data/import/fuel` | Upload & validate Diesel fuel price CSV file. |
| **Analysis** | `GET /api/v1/analysis/summary` | Descriptive statistics (mean, std, median, min, max). |
| | `GET /api/v1/analysis/trends` | Daily chronological points for frontend chart plotting. |
| | `GET /api/v1/analysis/regions` | Total queries and daily averages by state. |
| | `GET /api/v1/analysis/correlations` | Pairwise Pearson $r$ and Spearman $\rho$ values. |
| | `POST /api/v1/analysis/hypothesis-tests`| Runs formal Hypothesis A, B, and C tests. |
| **Forecast** | `POST /api/v1/forecast` | Runs SARIMAX forecast and advisory stress rating. |
| | `GET /api/v1/forecast/history` | Lists previous forecast runs from database. |
| | `GET /api/v1/forecast/{forecast_id}` | Detailed predictions and bounds for a specific forecast run. |
| **Reports** | `POST /api/v1/reports/generate` | Generates summary report and all charts. |
| | `GET /api/v1/reports/latest` | Returns markdown text of latest research report. |

---

## 13. Top 5 Viva Questions & Answers

1. **Q: Why does the project use SARIMAX instead of simple linear regression?**  
   *A:* Linear regression assumes observations are independent. Call volume has strong time autocorrelation (today's calls depend on yesterday's) and recurring 7-day weekly seasonality (Sunday drops). SARIMAX explicitly models both.
2. **Q: Why is train-test splitting done chronologically?**  
   *A:* Random train-test splitting shuffles future data into the past, causing lookahead bias and fake accuracy. In time series, you must only train on the past (80%) and test on the future (20%).
3. **Q: What does the Advisory Stress indicator measure?**  
   *A:* It is a project-defined operational indicator measuring expected strain on call-centre staffing (Normal, Elevated, High), comparing forecast demand against historical $\mu$ and $\sigma$. It is not an official government mandate.
4. **Q: Does a statistically significant correlation prove that price crashes cause calls?**  
   *A:* No. Correlation does not imply causation. External confounding factors (like monsoon delays or pest outbreaks) simultaneously affect harvest prices and farmer inquiry calls.
5. **Q: Are we using real government records or synthetic demo data right now?**  
   *A:* We are using reproducible synthetic demonstration data (`seed=42`, 730 days) that strictly mirrors the schema of data.gov.in and Agmarknet for offline development and testing. All records are tagged `is_synthetic = True`.

---

*For full deep dives, consult:*
- [docs/PROJECT_EXPLANATION_FOR_TEAM.md](file:///d:/python-capstone/docs/PROJECT_EXPLANATION_FOR_TEAM.md) — 24-section comprehensive team handover.
- [docs/QUICK_START_FOR_TEAM.md](file:///d:/python-capstone/docs/QUICK_START_FOR_TEAM.md) — Fast setup guide.
- [docs/API_REFERENCE_FOR_TEAM.md](file:///d:/python-capstone/docs/API_REFERENCE_FOR_TEAM.md) — Complete endpoint payloads.
- [docs/RESEARCH_AND_STATISTICS_GUIDE.md](file:///d:/python-capstone/docs/RESEARCH_AND_STATISTICS_GUIDE.md) — Statistical formulas and models.
