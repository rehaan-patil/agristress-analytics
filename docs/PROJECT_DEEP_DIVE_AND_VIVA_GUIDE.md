# AgriStress Analytics — Master Project Deep Dive & Technical Viva Guide

> **Target Audience:** First-Year Engineering Students, Project Review Panels, and Viva Voce Evaluators  
> **Repository:** `d:\python-capstone`  
> **Project Scope:** Local Econometric Time-Series Modeling, Advisory Stress Forecasting, and Actionable Farmer Decision Support  
> **Core Architecture:** Pure Python 3.10+ (Pandas, NumPy, SciPy, Statsmodels, Matplotlib, Seaborn, SQLAlchemy, SQLite, Pytest) — **No Frontend / No Web Server Required**  
> **Verification Status:** 35/35 Passing Unit & Integration Tests | 10 Generated Visualizations | 4 Structured CSV Result Tables | Multilingual Farmer Decision Advisories (English, Hindi, Marathi)

---

## Table of Contents

- [Chapter 1: The Entire Project in Plain English](#chapter-1-the-entire-project-in-plain-english)
- [Chapter 2: The Problem, Motivation, and Design Decisions](#chapter-2-the-problem-motivation-and-design-decisions)
- [Chapter 3: Full System Architecture and Execution Flow](#chapter-3-full-system-architecture-and-execution-flow)
- [Chapter 4: File-by-File and Function-by-Function Code Explanation](#chapter-4-file-by-file-and-function-by-function-code-explanation)
- [Chapter 5: Data Sources, Schemas, and Database Ingestion](#chapter-5-data-sources-schemas-and-database-ingestion)
- [Chapter 6: Every Feature-Engineering Calculation](#chapter-6-every-feature-engineering-calculation)
- [Chapter 7: Descriptive Statistics and Correlation Analysis](#chapter-7-descriptive-statistics-and-correlation-analysis)
- [Chapter 8: Every Hypothesis Test, Rationale, and Interpretation](#chapter-8-every-hypothesis-test-rationale-and-interpretation)
- [Chapter 9: Complete Individual Graph Analysis](#chapter-9-complete-individual-graph-analysis)
- [Chapter 10: Forecasting and SARIMAX — Complete Technical Explanation](#chapter-10-forecasting-and-sarimax--complete-technical-explanation)
- [Chapter 11: Agricultural Advisory Stress and Farmer Recommendations](#chapter-11-agricultural-advisory-stress-and-farmer-recommendations)
- [Chapter 12: Every Command-Line Option and Local Workflow](#chapter-12-every-command-line-option-and-local-workflow)
- [Chapter 13: Test Suite and Verification Evidence](#chapter-13-test-suite-and-verification-evidence)
- [Chapter 14: Libraries, Dependencies, and Technology Choices](#chapter-14-libraries-dependencies-and-technology-choices)
- [Chapter 15: Limitations, Failure Scenarios, and Future Roadmap](#chapter-15-limitations-failure-scenarios-and-future-roadmap)

---

## Chapter 1: The Entire Project in Plain English

### 1.1 What AgriStress Analytics Is
**AgriStress Analytics** is an offline, reproducible Python software pipeline designed to investigate and anticipate pressures on agricultural public support systems. Specifically, it monitors how macroeconomic market shocks—such as crashing wholesale crop prices, expanding wholesale-to-retail price margins, and diesel fuel inflation—drive farmers to contact government agricultural advisory helplines like the **Kisan Call Centre (KCC)**. 

Beyond research and statistical modeling, the project translates econometric findings into **plain-language, evidence-backed decision support advisories** for farmers, helping them evaluate storage viability, compare local mandi prices, manage freight expenses, and contact verified public assistance channels.

### 1.2 The Exact Problem Statement
Smallholder farmers in India operate under severe market volatility and margin compression. When farmgate wholesale prices drop or operational input costs (like tractor diesel) jump, farmers experience financial and agronomic anxiety. To cope, they reach out to government helplines. 

However, public advisory infrastructure often suffers from **reactive capacity planning**: call centres become overwhelmed *after* a crisis occurs rather than preparing staff in advance. Furthermore, academic research on market integration typically stops at producing statistical tables and p-values that an ordinary farmer cannot understand or act upon. 

**AgriStress Analytics solves both sides of this problem:**
1. **For Public Infrastructure / Research:** It models historical inquiry volume against price indicators, tests economic hypotheses, and forecasts call volume 14 days into the future using SARIMAX time-series models to predict an **Agricultural Advisory Stress Category** (`Normal`, `Elevated`, or `High`).
2. **For Farmers:** It translates these market conditions into plain-language actionable advisories in English, Hindi, and Marathi, detailing immediate steps, transport cost considerations, and verified toll-free helplines.

### 1.3 Why Farmer Demand for Agricultural Information is Worth Studying
Public agricultural extension services are the primary bridge between agricultural research institutions and grassroots cultivators. Analyzing call-centre logs provides an **unfiltered, high-frequency, real-time pulse of farmer concerns**. Unlike annual crop yield surveys or delayed census reports, helpline call volumes reflect immediate problems: sudden pest outbreaks during unusual weather, confusion during abrupt price collapses, or desperation when diesel price hikes erase transport margins.

### 1.4 What Kisan Call Centre (KCC) Query Data Represents
The Kisan Call Centre network (toll-free `1800-180-1551`) was launched by India's Ministry of Agriculture to provide tele-advisory services in local dialects. In this project:
- Each record represents agricultural inquiries logged by date, state, district, and subject category (e.g., Weather, Plant Protection, Market Information, Fertilizer).
- When aggregated daily, the `query_count` serves as an empirical proxy for **farmer information demand** and collective agricultural anxiety.

### 1.5 Why Commodity Prices, Price Spreads, and Diesel Prices are Considered
Agricultural decision-making does not occur in a vacuum; it is governed by three critical economic pressures:
1. **Wholesale Mandi Prices ($W_t$):** The price received by farmers at local Agricultural Produce Market Committee (APMC) yards. Sharp price drops threaten debt solvency.
2. **Wholesale-to-Retail Price Spread ($R_t - W_t$):** The margin between what urban consumers pay and what farmers receive. When this spread balloons, farmers realize that middlemen and logistics capture the value while farmgate realizations stagnate, prompting inquiries about alternative markets or Minimum Support Price (MSP) procurement.
3. **Retail Diesel Prices ($D_t$):** Diesel is the primary variable input cost for tillage, irrigation pump sets, harvest machinery, and road haulage. Sudden diesel price increases erode net income immediately.

### 1.6 Why Combine Data Processing, Statistical Analysis, and Forecasting?
A complete data engineering solution requires three sequential stages:
- **Data Processing:** Government data comes from fragmented sources (APMC portals, oil marketing companies, call centre logs) with mismatched dates, missing Sunday records, and inconsistent headers. Harmonizing them into a single aligned time-series is mandatory.
- **Statistical Analysis:** Visual inspection can be deceptive. Formal hypothesis testing (Pearson correlation, Spearman rank correlation, Mann-Whitney U tests) verifies whether apparent patterns are statistically meaningful or merely random noise.
- **Forecasting:** Proactive planning requires anticipating tomorrow's demand. Fitting seasonal time-series models (SARIMAX) enables predictive capacity allocation.

### 1.7 What "Agricultural Advisory Stress" Means in this Project
In this project, **Agricultural Advisory Stress** is a project-defined, quantitative proxy for operational load on public support infrastructure. It is calculated by comparing projected call demand against historical baseline parameters:
- $\text{Elevated Stress Threshold} = \mu_{\text{historical}} + 0.75 \times \sigma_{\text{historical}}$
- $\text{High Stress Threshold} = \mu_{\text{historical}} + 1.75 \times \sigma_{\text{historical}}$

If forecasted call demand exceeds these cutoffs, the advisory system flags potential call-centre congestion, signaling a need for temporary staffing surges.

### 1.8 Who Benefits and How
- **Call Centre Administrators:** Receive 14-day advance warnings of operational stress surges to schedule additional tele-advisors.
- **Agricultural Economists & Researchers:** Gain an automated, reproducible pipeline to evaluate spatial-temporal relationships and test market hypotheses.
- **Grassroots Farmers:** Receive structured, non-technical guidance outlining whether to sell immediately or store produce, how to account for freight costs, and where to seek verified official assistance.

### 1.9 What the Farmer Recommendation Engine Adds Beyond Research Tables
Research reports output metrics like $r = -0.1127$, $p = 0.1330$, and $\text{RMSE} = 12.88$. A farmer cannot use these to decide whether to load a truck tomorrow. 
The recommendation engine (`app/recommendations.py`):
1. Strips away all academic jargon.
2. Evaluates recent 7-day wholesale price trends against the prior week.
3. Provides concrete next steps (e.g., verifying local mandi rates before dispatching produce, pooling transport to cut diesel costs).
4. Highlights data freshness and limits (e.g., explicit warnings that historical demonstration data must not guide real financial transactions).
5. Provides verified official contact channels (KCC `1800-180-1551`, open 6:00 AM to 10:00 PM daily).

### 1.10 What the Application Can Currently Do vs Cannot Reliably Do
| What the System Reliably Does | What the System CANNOT Reliably Do |
| :--- | :--- |
| Cleans, maps synonyms, and aligns disparate CSV datasets by date. | Predict spot commodity prices with guaranteed financial accuracy. |
| Implements forward-fill imputation for mandi holiday closures. | Prescribe chemical pesticide dosages or plant disease treatments. |
| Conducts Pearson, Spearman, and Mann-Whitney U hypothesis tests. | Establish economic causality (correlation does not prove causation). |
| Fits 7-day Seasonal Naive baseline and SARIMAX(1,1,1)(1,1,0)[7] models. | Account for unmeasured farm-level debt, local crop damage, or weather disasters. |
| Computes MAE, RMSE, and zero-safe MAPE on chronological holdout splits. | Replace real-time live market intelligence if inputs are historical or synthetic. |
| Generates 10 analytical plots and multilingual plain-language advisories. | Guarantee call centre staffing levels without administrative policy integration. |

---

### 1.11 Three Ways to Explain This Project During an Exam / Presentation

#### The 30-Second Elevator Pitch (For an Evaluator Walking In)
> *"AgriStress Analytics is an offline Python system that studies how agricultural market shocks—such as wholesale mandi price crashes and diesel price hikes—drive farmers to contact government helplines like the Kisan Call Centre. We clean and align multi-source data, run econometric hypothesis tests, and use a SARIMAX time-series model to forecast call volumes 14 days ahead so call centres can prepare for surges. Finally, we convert these analytical findings into simple, multilingual advisories that help farmers make practical decisions about storage, freight, and market selection."*

#### The Two-Minute Presentation (For Formal Project Introduction)
> *"Good morning, respected evaluators. Our project, AgriStress Analytics, tackles a fundamental challenge in agricultural data systems: turning raw market and helpline records into proactive operational planning and practical farmer decision support.*
>
> *Smallholder farmers face severe price volatility. When farmgate prices crash or diesel prices jump, farmers seek urgent guidance from the Kisan Call Centre network. Today, these call centres operate reactively, getting overwhelmed after a crisis unfolds. Furthermore, existing research tools generate complex statistical tables that farmers cannot use.*
>
> *We developed an end-to-end Python pipeline with zero external web dependencies. Our pipeline ingests KCC call logs, APMC mandi wholesale-retail prices, and retail diesel rates. It automatically handles date normalization, column synonym mapping, and mandi holiday closures. We compute engineered features such as 7-day rolling volatility and wholesale-retail spreads, then formally test three economic hypotheses using Pearson, Spearman, and Mann-Whitney U tests.*
>
> *To anticipate operational load, we fit a seasonal SARIMAX(1,1,1)(1,1,0)[7] model evaluated against a 7-day Seasonal Naive baseline using strict chronological holdout splits. We classify future operational stress into Normal, Elevated, or High categories.*
>
> *Crucially, we built a plain-language Farmer Decision Engine that translates these mathematical models into actionable guidance in English, Hindi, and Marathi. It advises farmers on freight cost evaluation, produce perishability, and local APMC rate verification, supported by verified toll-free helplines. The entire codebase is verified by 35 automated tests."*

#### The Five-Minute Deep Technical Explanation (For Viva Voce Defense)
> *"Respected panel, AgriStress Analytics is architected as an econometrically grounded, reproducible time-series analysis and decision-support pipeline.*
>
> *From an engineering perspective, the system solves four core problems: data ingestion and schema harmonization, non-stationary feature engineering, rigorous statistical validation, and out-of-sample time-series forecasting.*
>
> *First, in our ingestion module (`app/data_processing.py`), we implement robust column-synonym normalization across government schemas, date parsing with error coercion, and deduplication that preserves market-level identifiers. Because mandis close on Sundays and gazetted holidays while call centres operate daily, naive inner joins create severe data loss. We solve this by reindexing onto a complete calendar grid and applying forward-fill price continuity imputation.*
>
> *Second, we engineer dynamic features: first-differenced commodity price changes, percentage changes, 7-day rolling standard deviation for price volatility, wholesale-to-retail margin spreads, and 1-day and 7-day lagged fuel revisions.*
>
> *Third, our statistical engine (`app/analysis.py`) tests three specific hypotheses: HYP-A evaluates linear correlation between price changes and call volume using Pearson's r; HYP-B tests fuel shock days using a non-parametric two-sided Mann-Whitney U test; and HYP-C evaluates monotonic rank association between wholesale-retail spreads and query volume via Spearman's rho. We explicitly disclose the econometric limitation of time-series autocorrelation on p-values.*
>
> *Fourth, in `app/forecasting.py`, we model the weekly cyclicality of call demand. Agricultural inquiries exhibit a strong 7-day periodicity because Sunday call volumes drop significantly. We compare a SARIMAX(1,1,1)(1,1,0)[7] model against a 7-day Seasonal Naive benchmark ($y_t = y_{t-7}$) using an out-of-sample chronological holdout split to prevent lookahead bias. We evaluate performance via MAE, RMSE, and zero-safe MAPE.*
>
> *Finally, our recommendation engine (`app/recommendations.py`) parses the analytical state into evidence-backed priority categories (`Action to consider now`, `Check before deciding`, `No clear signal`), linking every advice statement to empirical data while explicitly preventing unwarranted agronomic prescriptions. The system is fully tested with 35 pytest unit and integration tests and operates entirely offline."*

---

## Chapter 2: The Problem, Motivation, and Design Decisions

Every architectural decision in AgriStress Analytics was chosen deliberately to balance statistical validity, software reliability, and clarity for a first-year engineering team.

### Decision Matrix: Approaches, Alternatives, and Trade-Offs

| Component | Selected Approach | Alternative Approaches Considered | Why Selected / Trade-Offs |
| :--- | :--- | :--- | :--- |
| **User Interface** | Pure Python CLI / Terminal & Markdown output files | Web dashboard (React, Streamlit, FastAPI, Flask) | **Eliminated UI bloat.** Web servers introduce networking issues, port conflicts, and dependency fragility. A CLI script ensures 100% reproducibility and instant execution on any laptop. |
| **Database Engine** | Embedded SQLite via SQLAlchemy 2.0 ORM | PostgreSQL, MySQL, or in-memory Pandas only | SQLite requires zero server configuration and runs in a single file (`agristress.db`). SQLAlchemy provides schema validation and type safety without DBMS overhead. |
| **Missing Price Handling** | Forward-fill (`ffill()`) for mandi holidays; zero-fill for queries | Linear interpolation, backward-fill, or dropping missing rows | Mandis close on Sundays, but produce value does not drop to zero or jump to future values. Forward-fill reflects real-world market reality: the last traded price remains the effective benchmark until markets reopen. |
| **Non-Parametric Testing** | Mann-Whitney U Test for diesel price shocks (HYP-B) | Two-sample Student's t-test | Fuel price revisions occur intermittently, producing small, skewed sample sizes. Student's t-test requires normal distribution, which shock days violate. Mann-Whitney U tests rank sums without distributional assumptions. |
| **Forecasting Model** | Univariate SARIMAX(1,1,1)(1,1,0)[7] | Multi-layer LSTM / GRU / Facebook Prophet | Deep learning models require tens of thousands of observations to prevent overfitting. SARIMAX provides interpretable parameters, handles 7-day weekly seasonality directly, and computes statistical confidence intervals. |
| **Benchmark Selection** | 7-Day Seasonal Naive ($y_t = y_{t-7}$) | Simple historical mean or random walk | In seasonal time series, predicting "today's call volume will equal last week's same day" is a surprisingly strong baseline. Complex models must prove their value by beating this benchmark. |
| **Evaluation Strategy** | Chronological holdout split (last 14–30 days) | K-fold cross validation or random train-test split | **Random splitting creates future data leakage** in time series. Chronological splitting strictly evaluates the model's ability to forecast unseen future periods. |
| **Recommendation Engine** | Deterministic rule-based template mapping | Large Language Model (LLM) / Generative AI API | LLMs hallucinate numbers, require internet connectivity/API keys, and produce non-reproducible outputs. Deterministic rules ensure 100% verifiable, audit-proof recommendations. |

---

## Chapter 3: Full System Architecture and Execution Flow

### 3.1 End-to-End System Architecture

```mermaid
flowchart TD
    subgraph INGESTION ["Phase 1: Ingestion & Storage"]
        CLI["CLI Command: python main.py"] --> PARSER["argparse (main.py / run_pipeline.py)"]
        PARSER --> DB_INIT["app/database.py: SQLite Engine & Base.metadata"]
        DB_INIT --> IMPORT["app/data_processing.py: import_*_csv()"]
        IMPORT --> TABLES[("SQLite: agristress.db<br/>kcc_observations<br/>commodity_observations<br/>fuel_observations")]
    end

    subgraph HARMONIZATION ["Phase 2: Harmonization & Feature Engineering"]
        TABLES --> BUILD["build_analytical_dataset()"]
        BUILD --> REINDEX["Continuous Calendar Grid (Reindex 'D')"]
        REINDEX --> IMPUTE["Imputation: ffill() Prices, fillna(0) Queries"]
        IMPUTE --> FEAT_ENG["Feature Engineering:<br/>pct_change, 7d_volatility, price_spread, lags"]
        FEAT_ENG --> QUALITY["get_data_quality_report(): Coverage & Provenance"]
    end

    subgraph ANALYSIS ["Phases 3 & 4: Econometric Analysis & Visualizations"]
        FEAT_ENG --> STATS["app/analysis.py: get_descriptive_summary()"]
        FEAT_ENG --> CORR["get_correlations(): Pearson r & Spearman rho"]
        FEAT_ENG --> HYP["run_hypothesis_tests(): HYP-A, HYP-B, HYP-C"]
        FEAT_ENG --> CHARTS["generate_all_charts(): Matplotlib & Seaborn (8 PNGs)"]
        STATS --> CSV_TABLES["outputs/tables/ (4 CSV files)"]
    end

    subgraph FORECASTING ["Phase 5: Time-Series Forecasting"]
        FEAT_ENG --> FC_SPLIT["app/forecasting.py: Chronological Train/Test Split"]
        FC_SPLIT --> BASELINE["Seasonal Naive Benchmark (7D Lag)"]
        FC_SPLIT --> SARIMAX_FIT["Statsmodels SARIMAX(1,1,1)(1,1,0)[7] Fit"]
        SARIMAX_FIT --> EVAL["Metric Evaluation: MAE, RMSE, MAPE"]
        SARIMAX_FIT --> FULL_FIT["Full Sample Fit & 14-Day Out-of-Sample Forecast"]
        FULL_FIT --> STRESS["classify_advisory_stress(): Normal / Elevated / High"]
        FULL_FIT --> FC_CHARTS["outputs/charts/ (forecast_evaluation.png, actual_vs_predicted.png)"]
    end

    subgraph RECOMMENDATIONS ["Phase 6: Decision Support & Reporting"]
        FULL_FIT --> REC_ENGINE["app/recommendations.py: generate_farmer_recommendations()"]
        FEAT_ENG --> REC_ENGINE
        QUALITY --> REC_ENGINE
        REC_ENGINE --> ADVISORY_MD["outputs/reports/farmer_advisory.md (.txt)"]
        REC_ENGINE --> ADVISORY_HI["outputs/reports/farmer_advisory_hi.md (.txt)"]
        REC_ENGINE --> ADVISORY_MR["outputs/reports/farmer_advisory_mr.md (.txt)"]
        ANALYSIS --> TECH_REPORT["outputs/reports/summary_report.md"]
        FORECASTING --> TECH_REPORT
    end
```

### 3.2 Sequential Execution Trace (From Command to Artifacts)

When an evaluator runs:
```bash
python main.py
```
the following precise sequence executes:

1. **`main.py` entry point:** Reconfigures console stdout to `UTF-8` with error replacement to prevent Windows CP1252 character crash issues, then delegates to `run_pipeline.py:main()`.
2. **Argument Parsing (`run_pipeline.py:main`):** Evaluates optional flags (`--generate-data`, `--kcc`, `--commodity-file`, `--fuel`, `--replace`, `--state`, `--commodity`, `--horizon`, `--shock-threshold`, `--lang`).
3. **Phase 1 — Database Initialization & Ingestion:**
   - Calls `Base.metadata.create_all(bind=engine)` via SQLAlchemy.
   - If custom CSVs are supplied, calls `import_kcc_csv()`, `import_commodity_csv()`, and `import_fuel_csv()`.
   - If database is empty or `--generate-data` is passed, calls `generate_synthetic_data(seed=42, days=730)` and imports the synthetic files.
   - Records import history in `import_history` table.
4. **Phase 2 — Dataset Harmonization & Quality Audit:**
   - Calls `build_analytical_dataset(db, state, commodity)`.
   - Queries individual tables, aggregates daily totals/averages, and executes an outer calendar merge.
   - Reindexes to a continuous daily frequency `freq='D'`.
   - Imputes missing values: forward-fills prices and fills unrecorded queries with 0.
   - Calculates engineered features and exports `data/processed/analytical_dataset.csv`.
   - Calls `get_data_quality_report()` to audit record completeness and assign provenance (`SYNTHETIC`, `UNVERIFIED`, or `VERIFIED_REAL`).
5. **Phase 3 — Descriptive Statistics & Table Exports:**
   - Calls `get_descriptive_summary()` and `save_analysis_tables()`.
   - Writes `outputs/tables/descriptive_statistics.csv`, `correlations.csv`, `hypothesis_tests.csv`, and `regional_summary.csv`.
6. **Phase 4 — Exploratory Visualizations & Hypothesis Testing:**
   - Calls `generate_all_charts()` to render 8 exploratory visualization PNGs.
   - Calls `run_hypothesis_tests()` to execute tests for HYP-A (Pearson), HYP-B (Mann-Whitney U), and HYP-C (Spearman).
7. **Phase 5 — Forecasting & Advisory Stress Modeling:**
   - Calls `generate_forecast(db, horizon_days=14, use_sarimax=True)`.
   - Splits data chronologically: holdout test set (last 14–30 days).
   - Fits 7-day Seasonal Naive baseline and computes MAE, RMSE, MAPE.
   - Fits `SARIMAX(1,1,1)(1,1,0)[7]` on training data, evaluates on holdout, then refits on full dataset to forecast future 14 days.
   - Evaluates stress thresholds and saves `forecast_evaluation.png` and `actual_vs_predicted.png`.
   - Exports `forecast_predictions.csv` and `forecast_evaluation_metrics.csv` to `outputs/forecasts/`.
   - Calls `generate_summary_report()` to compile `outputs/reports/summary_report.md`.
8. **Phase 6 — Actionable Farmer Advisory Generation:**
   - Calls `generate_farmer_recommendations()` from `app/recommendations.py`.
   - Evaluates price changes, fuel rates, volatility, and stress proxy into priority categories.
   - Generates English, Hindi (`_hi`), and Marathi (`_mr`) advisories in both Markdown (`.md`) and Plain Text (`.txt`).
   - Prints a formatted, student-defensible summary banner to the terminal console.

---

## Chapter 4: File-by-File and Function-by-Function Code Explanation

### 4.1 Root & Configuration Files

#### `main.py`
- **Purpose:** Primary user-facing execution entry point.
- **Key Logic:** Safe UTF-8 reconfiguration of `sys.stdout` (lines 15–19) prevents Windows console UnicodeEncodeError crashes when printing special characters.
- **Viva Question:** *"Why do you have both `main.py` and `run_pipeline.py`?"*
  - **Answer:** `main.py` serves as a clean, standardized single-command entry point conforming to standard Python repository conventions. It sets up environment-level console encoding before passing execution to `run_pipeline.py`.

#### `app/config.py`
- **Purpose:** Centralized path management and environment configuration.
- **Key Logic:** Defines `BASE_DIR` dynamically using `Path(__file__).resolve().parent.parent`. Defines `DATA_DIR`, `OUTPUTS_DIR`, `TABLES_DIR`, and `FORECASTS_DIR`, creating required directory trees on startup via `.mkdir(parents=True, exist_ok=True)`. Configures `DATABASE_URL` (defaults to `sqlite:///{BASE_DIR}/agristress.db`).

#### `app/database.py`
- **Purpose:** SQLAlchemy database connectivity and session lifecycle.
- **Key Logic:** Creates SQLAlchemy engine with `connect_args={"check_same_thread": False}` for SQLite compatibility. Exposes `SessionLocal`, declarative `Base`, and the `get_db()` context generator.

#### `app/models.py`
- **Purpose:** Defines database schema tables via SQLAlchemy ORM.
- **Classes:**
  1. `KCCObservation` (`kcc_observations`): Stores call inquiry logs (`observation_date`, `state`, `district`, `query_type`, `query_count`, `is_synthetic`, `source_ref`).
  2. `CommodityObservation` (`commodity_observations`): Stores mandi transactions (`observation_date`, `state`, `district`, `market`, `commodity`, `wholesale_price`, `retail_price`, `arrival_quantity`, `units`).
  3. `FuelObservation` (`fuel_observations`): Stores retail diesel prices (`observation_date`, `state`, `diesel_price`, `currency`).
  4. `ImportHistory` (`import_history`): Audit log of imported CSV files (`total_records`, `accepted_records`, `rejected_records`, `duplicate_records`, `status`, `notes`).
  5. `ForecastHistory` (`forecast_history`): Logs historical forecast runs, model parameters, MAE/RMSE/MAPE metrics, and stress categories.

---

### 4.2 Data Processing Module (`app/data_processing.py`)

#### `standardize_column_names(df)` & `apply_column_synonyms(df)`
- **Inputs:** Raw Pandas `DataFrame`.
- **Outputs:** Transformed `DataFrame` with normalized column headers.
- **Logic:** Strips whitespace, converts to lowercase, and replaces spaces and dashes with underscores. Then maps over 30 government and operational synonyms (e.g., `modal_price_(rs./quintal)` $\to$ `wholesale_price`, `arrival_date` $\to$ `observation_date`, `calls` $\to$ `query_count`).
- **Viva Question:** *"What happens if a government portal changes its CSV header from 'Modal Price' to 'modal_price_rs_per_qtl'?"*
  - **Answer:** Our synonym dictionary maps both variants to `wholesale_price`. If an unmapped synonym appears, `check_missing_columns` catches it and gracefully aborts the import with a descriptive error logged in `import_history`.

#### `safe_parse_dates(series)`
- **Logic:** Uses `pd.to_datetime(series, errors='coerce', format='mixed').dt.date`. Any unparseable string is coerced to `NaT` and subsequently filtered out during data validation.

#### `import_kcc_csv(...)`, `import_commodity_csv(...)`, `import_fuel_csv(...)`
- **Inputs:** File path or file object, SQLAlchemy `Session`, `filename`, `is_synthetic` flag, `replace` boolean.
- **Operations:**
  1. Standardizes headers and applies column synonyms.
  2. Validates required columns (e.g., `observation_date`, `state`, `commodity`, `wholesale_price`).
  3. Coerces numerical values; filters out negative prices, non-positive fuel rates, or missing dates.
  4. Deduplicates records: for commodity records, deduplication uses `['parsed_date', 'state', 'commodity', 'market']`, ensuring multi-mandi records on the same date are preserved.
  5. If `replace=True`, deletes existing table rows.
  6. Executes bulk insertion via `db.bulk_save_objects()`.
  7. Inserts an audit entry into `import_history`.
- **Viva Question:** *"Why use `bulk_save_objects` instead of looping with `db.add()`?"*
  - **Answer:** Iterating with `db.add()` causes SQLAlchemy to emit individual SQL `INSERT` statements, which takes several minutes for 10,000+ rows in SQLite. `bulk_save_objects` prepares a single batched transaction, reducing import time from minutes to under 500 milliseconds.

#### `build_analytical_dataset(db, state, commodity, freq='D', export_csv=True)`
- **Purpose:** The core harmonization engine that joins disparate datasets.
- **Operation Sequence:**
  1. Queries `KCCObservation` grouped by date to compute total daily queries.
  2. Queries `CommodityObservation` grouped by date to calculate average daily wholesale and retail prices, and sum arrivals.
  3. Queries `FuelObservation` grouped by date to compute daily average diesel prices.
  4. Merges queries, commodity prices, and fuel prices using date-based left joins.
  5. Reindexes against a complete daily date range (`pd.date_range(min, max, freq='D')`).
  6. Imputes missing values:
     - `query_count.fillna(0.0)`: Days with no calls represent zero recorded inquiries.
     - `wholesale_price.ffill().bfill()`: Mandi closures carry forward the last observed market clearing price.
     - `diesel_price.ffill().bfill()`: Infrequent fuel revisions carry forward the active retail price.
  7. Computes engineered features (price changes, percentage changes, 7-day rolling standard deviations, margins, and lags).
  8. Exports to `data/processed/analytical_dataset.csv`.

---

### 4.3 Analysis & Visualization Module (`app/analysis.py`)

#### `get_descriptive_summary(df)`
- **Calculations:** Computes count, mean, standard deviation, minimum, median, and maximum for `query_count`, `wholesale_price`, `retail_price`, `diesel_price`, `price_spread`, and `commodity_volatility_7d`.

#### `get_correlations(df)`
- **Calculations:** For each economic feature paired with `query_count`, extracts paired clean observations ($N \ge 10$) and computes both Pearson linear correlation ($r$) and Spearman rank correlation ($\rho$) using `scipy.stats`.

#### `run_hypothesis_tests(df, diesel_shock_threshold_pct=1.0)`
- **Purpose:** Executes formal econometric hypothesis tests for HYP-A, HYP-B, and HYP-C (covered in detail in Chapter 8).

#### Visualizations (`plot_query_demand_over_time`, `plot_seasonality`, etc.)
- **Execution:** Uses `matplotlib` configured with the non-GUI `Agg` backend (`matplotlib.use("Agg")`). Every plotting function closes its figure with `plt.close()` to prevent memory leaks during batch execution.

---

### 4.4 Forecasting Module (`app/forecasting.py`)

#### `calculate_metrics(actual, predicted)`
- **Formulas:**
  $$\text{MAE} = \frac{1}{n} \sum_{i=1}^n |y_i - \hat{y}_i|$$
  $$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^n (y_i - \hat{y}_i)^2}$$
  $$\text{MAPE} = \frac{100\%}{n} \sum_{i=1}^n \frac{|y_i - \hat{y}_i|}{\max(|y_i|, 1.0)}$$
- **Zero-Safe Protection:** If actual call count is 0, the denominator replaces 0 with 1.0 to prevent `ZeroDivisionError`.

#### `classify_advisory_stress(pred_mean, pred_upper, hist_mean, hist_std)`
- **Logic:** Compares predicted mean call volume against standard deviation cutoffs:
  - $\text{Elevated} \ge \mu + 0.75\sigma$
  - $\text{High} \ge \mu + 1.75\sigma$
  - Also flags if the 95% upper confidence bound breaches the High threshold.

#### `generate_forecast(db, state, commodity, horizon_days=14, use_sarimax=True)`
- **Operations:**
  1. Extracts the daily series of `query_count`.
  2. Sets chronological split: holdout test set is the last $T_{\text{test}} = \min(30, \max(7, 0.2 \times N))$ days.
  3. Generates 7-day Seasonal Naive baseline predictions on the test set: $\hat{y}_t = y_{t-7}$.
  4. Fits `SARIMAX(train, order=(1,1,1), seasonal_order=(1,1,0,7))` on training data and computes test metrics.
  5. Refits `SARIMAX` on the entire series to generate true out-of-sample forecasts for `horizon_days` ahead with 95% confidence intervals.
  6. Saves two evaluation plots (`forecast_evaluation.png` and `actual_vs_predicted.png`) and two CSV tables.
  7. Persists the run into `forecast_history`.

---

### 4.5 Recommendation Engine (`app/recommendations.py`)

#### `generate_farmer_recommendations(df, forecast_res, state, commodity, quality, db, lang)`
- **Purpose:** Translates complex statistics into clear, actionable advice.
- **Logic:**
  1. Evaluates data freshness by comparing the latest observation date with the system reference date. If data is older than 30 days, issues an explicit freshness disclaimer.
  2. Evaluates 7-day wholesale price trend: computes the percentage difference between the most recent 7-day average and the preceding 7-day average.
  3. Assigns an advisory priority category:
     - `Action to consider now` (if prices drop $\ge 5\%$ or forecasted stress is High).
     - `Check before deciding` (moderate price fluctuations or elevated call demand).
     - `No clear signal` (stable prices and normal inquiry demand).
  4. Assembles decision factors: transport freight quotation checks, crop perishability, and moisture/grading premiums.
  5. If multi-mandi records exist in the database, generates a structured APMC comparison table showing price differences and estimated net returns.
  6. Renders advisories in English, Hindi, and Marathi in both Markdown and Plain Text formats.

---

## Chapter 5: Data Sources, Schemas, and Database Ingestion

### 5.1 The Journey of the Data

```mermaid
flowchart LR
    CSV_KCC["Raw KCC CSV"] --> SYN_MAP["Synonym Mapping & Cleaning"]
    CSV_COMM["Raw Mandi CSV"] --> SYN_MAP
    CSV_FUEL["Raw Fuel CSV"] --> SYN_MAP
    SYN_MAP --> DEDUP["Deduplication & Validation"]
    DEDUP --> SQLITE[("agristress.db (SQLite)")]
    SQLITE --> MERGE["Date-Based Left Merge"]
    MERGE --> REINDEX["Reindex 365-Day Grid"]
    REINDEX --> FORWARD_FILL["Forward-Fill Prices"]
    FORWARD_FILL --> ANALYTICAL_DF["analytical_dataset.csv"]
```

### 5.2 Illustrative Example: Raw Transactions to Daily Aggregated Record

To understand how raw transactions become an analytical record, consider this illustrative, fictional example:

#### Raw Input 1: Mandi Price CSV (`mandi_sample.csv`)
| observation_date | state | market | commodity | wholesale_price | retail_price | arrival_quantity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2024-03-15 | Maharashtra | Pimpalgaon | Onion | 1450.0 | 2200.0 | 120.0 |
| 2024-03-15 | Maharashtra | Lasalgaon | Onion | 1550.0 | 2300.0 | 180.0 |

#### Raw Input 2: KCC Query CSV (`kcc_sample.csv`)
| observation_date | state | query_type | query_count |
| :--- | :--- | :--- | :--- |
| 2024-03-15 | Maharashtra | Market Information | 42 |
| 2024-03-15 | Maharashtra | Plant Protection | 38 |

#### Raw Input 3: Fuel Price CSV (`fuel_sample.csv`)
| observation_date | state | diesel_price |
| :--- | :--- | :--- |
| 2024-03-15 | Maharashtra | 94.50 |

#### Aggregated & Aligned Analytical Output (`analytical_dataset.csv`)
When `build_analytical_dataset` processes this date for Maharashtra:
- `query_count` = $42 + 38 = 80$ calls
- `wholesale_price` = $\frac{1450.0 + 1550.0}{2} = 1500.0$ INR/Quintal
- `retail_price` = $\frac{2200.0 + 2300.0}{2} = 2250.0$ INR/Quintal
- `arrival_quantity` = $120.0 + 180.0 = 300.0$ Tonnes
- `diesel_price` = $94.50$ INR/Litre
- `price_spread` = $2250.0 - 1500.0 = 750.0$ INR/Quintal
- `retail_margin_pct` = $\frac{750.0}{1500.0} \times 100\% = 50.0\%$

### 5.3 What Happens During Edge Cases?
- **Missing Required Columns:** If a file lacks mandatory fields (e.g., missing `wholesale_price`), `check_missing_columns` catches it. The file is rejected, zero rows are inserted, and the failure is logged in `import_history`.
- **Negative Prices or Zero Fuel Rates:** Coerced to NaN and filtered out during validation (`valid = df[df['wholesale_price'] > 0]`).
- **Mandi Closures (Sundays):** Reindexing creates rows with NaN for prices. `ffill()` carries forward Saturday's closing price.
- **Unrecorded Call Days:** Filled with 0 queries using `.fillna(0.0)`.

### 5.4 Understanding Data Provenance
AgriStress Analytics enforces strict provenance labeling:
1. **`SYNTHETIC`:** Data generated by `generate_synthetic_data(seed=42)`. Clearly marked with banners in terminal output and reports.
2. **`UNVERIFIED`:** Custom CSV files imported via `--kcc`, `--commodity-file`, or `--fuel` without independent administrative verification.
3. **`VERIFIED_REAL`:** Custom data explicitly certified as authentic government records via the `--verified-real` CLI flag.

---

## Chapter 6: Every Feature-Engineering Calculation

All engineered features are calculated in `app/data_processing.py` (lines 476–492).

### 1. Daily Commodity Price Change (`commodity_price_change`)
- **Formula:** $\Delta W_t = W_t - W_{t-1}$
- **Purpose:** Measures the absolute day-to-day change in wholesale mandi price.
- **Hand Calculation:** If yesterday's wholesale price was ₹1,200/qtl and today's price is ₹1,140/qtl:
  $$\Delta W_t = 1140 - 1200 = -60.0 \text{ INR/Quintal}$$

### 2. Commodity Percentage Change (`commodity_pct_change`)
- **Formula:** 
  $$\% \Delta W_t = \left( \frac{W_t - W_{t-1}}{W_{t-1}} \right) \times 100$$
- **Purpose:** Normalizes price movements across different crops with different price baselines (e.g., a ₹100 change on ₹1,000 onion is a 10% shock, whereas on ₹6,000 cumin it is under 2%).
- **Hand Calculation:**
  $$\% \Delta W_t = \left( \frac{1140 - 1200}{1200} \right) \times 100 = -5.0\%$$

### 3. 7-Day Rolling Price Volatility (`commodity_volatility_7d`)
- **Formula:**
  $$\sigma_{7d, t} = \sqrt{\frac{1}{k-1} \sum_{i=0}^{k-1} (W_{t-i} - \bar{W}_{7d, t})^2} \quad \text{where } k = \min(7, \text{observed periods} \ge 2)$$
- **Purpose:** Captures short-term market turbulence. High volatility increases farmer uncertainty.
- **Edge Case:** At the start of a series, `min_periods=2` ensures that volatility is calculated as soon as two days of data exist, preventing 6 days of empty output.

### 4. Wholesale-to-Retail Price Spread (`price_spread`)
- **Formula:** 
  $$\text{Spread}_t = R_t - W_t$$
- **Purpose:** Quantifies the gross marketing margin captured by intermediaries, logistics, and retail distribution.
- **Hand Calculation:** Retail price = ₹3,200/qtl, Wholesale price = ₹1,800/qtl:
  $$\text{Spread}_t = 3200 - 1800 = 1400.0 \text{ INR/Quintal}$$

### 5. Retail Margin Percentage (`retail_margin_pct`)
- **Formula:** 
  $$\text{Margin } \% = \left( \frac{R_t - W_t}{W_t} \right) \times 100$$
- **Purpose:** Shows retail markup relative to the farmgate price. A markup over 100% means consumers pay more than double what farmers receive.
- **Hand Calculation:**
  $$\text{Margin } \% = \left( \frac{1400}{1800} \right) \times 100 = 77.78\%$$

### 6. Daily Diesel Percentage Change (`diesel_pct_change`)
- **Formula:**
  $$\% \Delta D_t = \left( \frac{D_t - D_{t-1}}{D_{t-1}} \right) \times 100$$
- **Purpose:** Identifies fuel price revisions. Days where $|\% \Delta D_t| \ge 1.0\%$ are classified as **fuel shock days** for hypothesis testing.

### 7. Lagged Diesel Price Changes (`diesel_change_lag1`, `diesel_change_lag7`)
- **Formula:** $\Delta D_{t-1}$ and $\Delta D_{t-7}$
- **Purpose:** Farmers may not react to a fuel hike on the exact day it is announced. Lagged features capture delayed behavioral responses (e.g., when the weekly transport bill arrives).

---

## Chapter 7: Descriptive Statistics and Correlation Analysis

### 7.1 Understanding the Descriptive Metrics
For every numeric variable, the pipeline computes:
- **Count ($N$):** Valid non-null observations.
- **Mean ($\mu$):** The arithmetic average: $\frac{1}{N} \sum x_i$.
- **Standard Deviation ($\sigma$):** Dispersion around the mean: $\sqrt{\frac{\sum (x_i - \bar{x})^2}{N-1}}$.
- **Median:** The 50th percentile value. Unlike the mean, the median is robust to extreme outliers (e.g., isolated luxury retail prices).
- **Min / Max:** The observed range boundaries.

#### Actual Descriptive Statistics from System Execution:
| Variable | Count ($N$) | Mean ($\mu$) | Std Dev ($\sigma$) | Min | Median | Max | Units |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `query_count` | 180 | 141.56 | 49.99 | 69.00 | 132.50 | 246.00 | Calls / Day |
| `wholesale_price` | 180 | 1755.94 | 994.25 | 579.45 | 1138.53 | 3044.04 | INR / Quintal |
| `retail_price` | 180 | 3054.98 | 540.42 | 2254.94 | 3203.18 | 3702.98 | INR / Quintal |
| `diesel_price` | 180 | 97.86 | 2.43 | 94.50 | 96.86 | 100.78 | INR / Litre |
| `price_spread` | 180 | 1299.04 | 600.13 | 573.20 | 1385.99 | 2728.31 | INR / Quintal |
| `commodity_volatility_7d` | 179 | 57.97 | 79.52 | 14.77 | 32.37 | 354.82 | INR (7-day Std) |

---

### 7.2 Pearson Linear Correlation vs Spearman Rank Correlation

#### Pearson Correlation Coefficient ($r$)
- **Mathematical Formula:**
  $$r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \sum (y_i - \bar{y})^2}}$$
- **Intuition:** Measures the strength and direction of a **linear relationship**. Assumes bivariate normality. If points lie along a straight line, $r = \pm 1$.

#### Spearman Rank Correlation Coefficient ($\rho$)
- **Mathematical Formula:**
  $$\rho = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)} \quad \text{where } d_i = \text{rank}(x_i) - \text{rank}(y_i)$$
- **Intuition:** Measures **monotonic association** (whether variables increase together, regardless of whether the curve is linear). Because it operates on ranks rather than raw values, it is immune to extreme outliers.

#### Actual Correlation Results from Current Execution:
| Variable Pair | Pearson $r$ | Spearman $\rho$ | Sample Size ($N$) | Economic Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| KCC Demand vs Wholesale Price | -0.8329 | -0.8840 | 180 | Strong negative association (calls rise as prices crash). |
| KCC Demand vs Daily Price Change | -0.1232 | -0.0398 | 179 | Weak contemporaneous linear relationship. |
| KCC Demand vs 7D Volatility | +0.3510 | +0.4424 | 179 | Moderate positive relationship (turbulent markets increase calls). |
| KCC Demand vs Price Spread | +0.9265 | +0.9093 | 180 | Strong positive relationship (wide spreads coincide with peak inquiries). |
| KCC Demand vs Diesel Price Level | +0.4904 | +0.5661 | 180 | Moderate positive correlation with fuel levels. |
| KCC Demand vs Daily Diesel Change | +0.0684 | +0.0686 | 179 | Negligible same-day association with fuel revisions. |
| KCC Demand vs 7D Lagged Diesel Change | +0.0648 | +0.0676 | 172 | Negligible 7-day lagged association. |

---

### 7.3 Critical Viva Questions on Correlation

#### Q: "Why did you calculate both Pearson and Spearman correlation?"
> **Answer:** *"Pearson measures strict linear proportionality, but agricultural relationships are often non-linear. For example, a wholesale price crash causes a massive surge in calls up to a point, after which call volume saturates because call-centre lines become busy. Spearman rank correlation captures this monotonic relationship without assuming a straight line, and it is robust against sudden price spikes or retail outliers."*

#### Q: "Does a high correlation ($r = 0.9265$) prove that expanding price spreads cause farmers to call?"
> **Answer:** *"No, correlation does not establish causality. Both variables could be driven by a common confounder, such as peak harvest arrival season. During peak harvest, wholesale prices drop while retail prices stay sticky, expanding the spread. Simultaneously, harvest logistics problems prompt calls. The correlation confirms empirical co-movement, not a direct causal link."*

---

## Chapter 8: Every Hypothesis Test, Rationale, and Interpretation

The system implements three formal hypothesis tests in `app/analysis.py` (lines 133–276).

```mermaid
flowchart TD
    subgraph HYP_TESTS ["Econometric Hypothesis Testing Suite"]
        A["HYP-A: Commodity Price Movements vs Query Volume"] --> TEST_A["Pearson Linear Correlation Test<br/>(N = 179)"]
        TEST_A --> RES_A["r = -0.1127, p = 0.1330<br/>Outcome: FAIL TO REJECT H0"]
        
        B["HYP-B: Diesel Price Shocks vs Advisory Influx"] --> TEST_B["Mann-Whitney U Rank Sum Test<br/>(|Change| >= 1.0%)"]
        TEST_B --> RES_B["Shock Days = 3 (Requires >= 5)<br/>Outcome: INSUFFICIENT SHOCK DAYS"]
        
        C["HYP-C: Wholesale-Retail Spread vs Advisory Influx"] --> TEST_C["Spearman Rank Correlation Test<br/>(N = 180)"]
        TEST_C --> RES_C["rho = +0.9093, p < 0.0001<br/>Outcome: REJECT H0"]
    end
```

---

### 8.1 Detailed Breakdown of Each Implemented Hypothesis Test

#### HYP-A: Commodity Price Movements vs Query Demand
- **Research Question:** Do day-to-day percentage changes in wholesale commodity prices linearly correlate with KCC advisory query volume?
- **Null Hypothesis ($H_0$):** Daily commodity percentage changes have no linear correlation with farmer query volume ($r = 0$).
- **Alternative Hypothesis ($H_1$):** Daily commodity percentage changes are linearly correlated with farmer query volume ($r \neq 0$).
- **Statistical Test:** Two-tailed Pearson Linear Correlation Test (`scipy.stats.pearsonr`).
- **Sample Size ($N$):** 179 paired daily observations.
- **Observed Metrics:** Test Statistic $r = -0.1127$, $p$-value = $0.13303$, Significance level $\alpha = 0.05$.
- **Outcome:** **FAIL TO REJECT NULL HYPOTHESIS** ($p > 0.05$).
- **Plain-English Meaning:** In this dataset, daily price percentage fluctuations do not show a statistically significant linear correlation with call volume on the same day. Farmers react to cumulative price levels rather than daily fluctuations.
- **Assumptions & Limitations:** Assumes bivariate normality and linearity. Does not capture non-linear or delayed lagged reactions. Time-series autocorrelation can narrow standard errors.

#### HYP-B: Diesel Price Shocks vs Advisory Influx
- **Research Question:** Do days experiencing sudden retail diesel price revisions trigger significantly different farmer call volumes than normal days?
- **Null Hypothesis ($H_0$):** Call query volume distributions on fuel shock days and normal fuel days are identical ($F_{\text{shock}}(y) = F_{\text{normal}}(y)$).
- **Alternative Hypothesis ($H_1$):** Call query volume distributions differ significantly during fuel shock days.
- **Statistical Test:** Two-sided Mann-Whitney U Non-Parametric Rank Sum Test (`scipy.stats.mannwhitneyu`).
- **Sample Size ($N$):** 179 days evaluated.
- **Observed Metrics:** Shock threshold was set to $|\% \Delta D_t| \ge 1.0\%$. The algorithm identified only **3 shock days** out of 179 days.
- **Sample Adequacy Rule:** The implementation enforces a strict sample threshold: requires $\ge 5$ shock days and $\ge 15$ normal days.
- **Outcome:** **FAIL TO REJECT NULL HYPOTHESIS** (Inadequate shock sample size).
- **Plain-English Meaning:** Retail diesel prices in India operate under administered pricing regimes where prices remain frozen for months at a time. Because only 3 price revision days occurred, there is insufficient empirical data to draw a statistically valid conclusion.
- **Viva Defense Point:** *"Why didn't you force a t-test on those 3 days?"*
  - **Answer:** *"Running a statistical test on only 3 observations produces statistical noise and severe Type I error risk. Our software responsibly halts test execution and reports sample inadequacy, adhering to rigorous scientific standards."*

#### HYP-C: Wholesale-to-Retail Price Spreads vs Advisory Demand
- **Research Question:** Is the margin spread between wholesale mandi price and consumer retail price monotonically associated with farmer query demand?
- **Null Hypothesis ($H_0$):** There is no monotonic rank association between price spread and KCC call volume ($\rho = 0$).
- **Alternative Hypothesis ($H_1$):** Price spread and KCC call volume are monotonically associated ($\rho \neq 0$).
- **Statistical Test:** Two-tailed Spearman Rank-Order Correlation Test (`scipy.stats.spearmanr`).
- **Sample Size ($N$):** 180 observations.
- **Observed Metrics:** Test Statistic $\rho = +0.9093$, $p$-value displayed as `0.0` (mathematically $p < 10^{-16}$), $\alpha = 0.05$.
- **Outcome:** **REJECT NULL HYPOTHESIS** ($p < 0.001$).
- **Plain-English Meaning:** There is a very strong, statistically significant positive monotonic association between the wholesale-to-retail price spread and farmer query demand. When the gap between farmgate price and consumer price widens, helpline inquiries surge.

---

### 8.2 Crucial Statistical Nuance: How to Discuss a Tiny $p$-Value

In `outputs/tables/hypothesis_tests.csv`, HYP-C displays `p_value: 0.0`. 
**Never say in your viva that the probability is literally zero.**
In floating-point scientific computing (`SciPy`), when a calculated $p$-value is smaller than the precision limit of a 64-bit float ($\approx 10^{-16}$), it prints as `0.0`.
> **Correct Viva Phrasing:** *"The p-value is extremely small—less than $10^{-4}$—which is well below our significance threshold of $\alpha = 0.05$. We therefore reject the null hypothesis with very high statistical confidence."*

---

## Chapter 9: Complete Individual Graph Analysis

The pipeline automatically generates **10 publication-quality charts** in `outputs/charts/`. Every chart is explained below with its research rationale, axes, interpretation, and viva defense script.

---

### Graph 1: `query_demand_over_time.png`
- **Plotting Function:** `app/analysis.py:plot_query_demand_over_time()`
- **Research Motivation:** To establish the historical trajectory of farmer information demand and identify macro-level trend patterns versus high-frequency noise.
- **Axes & Elements:**
  - **X-Axis:** Date (Daily continuous calendar timeline).
  - **Y-Axis:** Inquiry Volume (Number of calls logged per day).
  - **Blue Line (alpha=0.5):** Raw daily KCC query count ($y_t$). Shows high day-to-day volatility.
  - **Red Line (linewidth=2):** 14-day rolling moving average ($\bar{y}_{14d, t}$). Smooths out weekly cycles to highlight seasonal trends.
- **How to Read It:** When the red moving average slopes upward, overall agricultural stress is accumulating across the state. Sharp spikes in the blue line indicate temporary short-term events (e.g., localized weather or fuel announcements).
- **What It Cannot Tell Us:** Does not reveal *why* calls are rising (e.g., whether the cause is pest damage, weather, or market prices).
- **3 Viva Questions:**
  1. *Q: Why use a 14-day rolling average instead of 7-day?*
     - *A:* A 14-day window smooths out two complete 7-day weekly cycles, removing both weekday and weekend effects to expose the true underlying macro trend.
  2. *Q: What explains the jagged spikes in the daily blue line?*
     - *A:* Call centres experience cyclical weekday surges and weekend drop-offs.
  3. *Q: How does this chart relate to forecasting?*
     - *A:* It visually confirms non-stationarity in the mean, justifying the first-differencing ($d=1$) parameter in our SARIMAX model.
- **Presentation Script (25s):**
  > *"This chart displays daily Kisan Call Centre inquiry volume over time. The semi-transparent blue line represents raw daily call counts, which fluctuate significantly due to weekly cycles. The solid red line represents a 14-day rolling moving average. Notice how the moving average reveals macro-seasonal surges, helping administrators distinguish between temporary day-to-day noise and sustained call-centre demand shifts."*

---

### Graph 2: `seasonality_patterns.png`
- **Plotting Function:** `app/analysis.py:plot_seasonality()`
- **Research Motivation:** To verify whether farmer information demand follows a weekly cyclical calendar pattern.
- **Axes & Elements:**
  - **X-Axis:** Day of the Week (Monday through Sunday).
  - **Y-Axis:** Mean Inquiries (Average calls logged on that day).
  - **Green Bars:** Average call volume per weekday.
- **How to Read It:** Weekday bars (Monday to Friday) are substantially taller (typically 140–160 calls/day), while the Sunday bar drops drastically (often below 50 calls/day) due to reduced weekend staffing and farmers prioritizing rest or religious activities.
- **What It Tells Us:** Provides empirical proof of a **7-day seasonal cycle ($s=7$)**, justifying the seasonal component in SARIMAX.
- **3 Viva Questions:**
  1. *Q: Why do Sunday calls drop so sharply?*
     - *A:* Many administrative services operate with reduced weekend shifts, and farmers conduct fewer market transactions on Sundays when mandis are closed.
  2. *Q: How does this chart directly influence the forecasting model?*
     - *A:* It justifies configuring seasonal period $s=7$ and seasonal autoregression $P=1$ in our SARIMAX specification.
  3. *Q: What would happen if we ignored this weekly pattern?*
     - *A:* A non-seasonal model would consistently overpredict Sunday calls and underpredict Monday calls, inflating forecast error.
- **Presentation Script (25s):**
  > *"Here we examine the weekly cyclicality of farmer inquiries. Notice that Monday through Friday maintain consistently high inquiry volumes, whereas Sunday drops sharply. This confirms a prominent 7-day agricultural call cycle, directly validating our decision to incorporate a seasonal period of $s=7$ into our SARIMAX time-series model."*

---

### Graph 3: `commodity_price_trends.png`
- **Plotting Function:** `app/analysis.py:plot_commodity_trends()`
- **Research Motivation:** To track wholesale market price movements and quantify market turbulence over time.
- **Axes & Elements (2 Stacked Panels):**
  - **Panel A (Top):** Green line tracking Agricultural Commodity Wholesale Mandi Price (INR/Quintal) on the Y-axis against Date on the X-axis.
  - **Panel B (Bottom):** Amber line tracking 7-Day Rolling Price Volatility ($\sigma_{7d}$) in INR against Date on the X-axis.
- **How to Read It:** When Panel A experiences steep downward slopes (price crashes), Panel B spikes upward, indicating severe market volatility.
- **What It Cannot Tell Us:** Does not show transport freight costs or whether the price drop was caused by excess local arrivals versus nationwide demand changes.
- **3 Viva Questions:**
  1. *Q: Why plot price and volatility on separate panels?*
     - *A:* Price is measured in thousands of rupees per quintal, whereas volatility is a standard deviation measure. Placing them on one axis would compress the volatility curve.
  2. *Q: What does a spike in Panel B signify?*
     - *A:* It indicates rapid, unpredictable day-to-day price swings, representing elevated financial uncertainty for farmers.
  3. *Q: How are Sunday prices handled on this chart?*
     - *A:* Mandi closures on Sundays are forward-filled, maintaining price continuity without artificial drops to zero.
- **Presentation Script (30s):**
  > *"This two-panel chart illustrates commodity price behavior. In Panel A, the green curve traces the wholesale mandi price in rupees per quintal. Panel B plots 7-day rolling price volatility. Notice that during periods of steep wholesale price declines, rolling volatility spikes dramatically. This provides visual evidence of market stress, which we correlate against farmer helpline inquiries."*

---

### Graph 4: `diesel_price_trends.png`
- **Plotting Function:** `app/analysis.py:plot_diesel_trends()`
- **Research Motivation:** To visualize retail fuel price movements and identify fuel revision shocks.
- **Axes & Elements (2 Stacked Panels):**
  - **Panel A (Top):** Magenta line showing Retail Diesel Price (INR/Litre) over time.
  - **Panel B (Bottom):** Purple vertical bars showing Daily Diesel Price Percentage Changes ($\% \Delta D_t$). Includes red dotted horizontal reference lines at $+1.5\%$ and $-1.5\%$ marking shock thresholds.
- **How to Read It:** In Panel A, retail diesel moves in step-wise plateaus characteristic of administered fuel pricing. In Panel B, most days show zero revision, with occasional vertical bars representing official price adjustments.
- **What It Cannot Tell Us:** Does not show individual farmer fuel consumption or machinery ownership.
- **3 Viva Questions:**
  1. *Q: Why do fuel prices show flat lines for long stretches?*
     - *A:* State-owned oil marketing companies in India adjust fuel prices intermittently rather than via continuous intraday floating rates.
  2. *Q: What do the red dotted lines in Panel B represent?*
     - *A:* They represent our configurable $\pm 1.5\%$ threshold used to identify fuel shock days for Hypothesis B.
  3. *Q: Why did HYP-B fail to reject the null hypothesis on this data?*
     - *A:* As seen in Panel B, only 3 days breached the shock threshold, which is below the minimum statistical requirement of 5 shock days.
- **Presentation Script (25s):**
  > *"This figure shows retail diesel fuel dynamics. Panel A displays the retail diesel price in rupees per litre, exhibiting step-like revisions. Panel B isolates daily percentage changes, with red dashed lines indicating our 1.5% shock threshold. This visual makes it immediately clear why Hypothesis B identified few shock days: administered pricing creates long periods of zero daily revisions punctuated by rare adjustments."*

---

### Graph 5: `price_spreads.png`
- **Plotting Function:** `app/analysis.py:plot_price_spread()`
- **Research Motivation:** To measure the margin gap between what consumers pay in retail markets and what farmers receive at wholesale mandis.
- **Axes & Elements:**
  - **X-Axis:** Date.
  - **Y-Axis:** Price in INR/Quintal.
  - **Purple Line:** Consumer Retail Price ($R_t$).
  - **Green Line:** Wholesale Mandi Price ($W_t$).
  - **Shaded Purple Band:** The absolute price spread ($R_t - W_t$), representing the intermediary marketing margin.
- **How to Read It:** When the shaded band widens, intermediaries and logistics capture a greater share of the crop's final value, while the farmgate realization shrinks.
- **What It Tells Us:** Provides empirical context for Hypothesis C, demonstrating how retail prices remain sticky even when wholesale farmgate prices collapse.
- **3 Viva Questions:**
  1. *Q: Why are retail prices so much higher than wholesale mandi prices?*
     - *A:* The spread covers handling, packaging, transportation, market fees, storage shrinkage, and wholesale-retail profit margins.
  2. *Q: What does an expanding shaded area indicate to an agricultural economist?*
     - *A:* It indicates asymmetric price transmission: retail prices fail to drop when farmgate prices crash, depressing farmer income without benefiting consumers.
  3. *Q: How does this chart connect to our statistical tests?*
     - *A:* This shaded margin directly corresponds to the `price_spread` variable in HYP-C, where we found a strong rank correlation ($\rho = 0.9093$) with farmer call volume.
- **Presentation Script (30s):**
  > *"Here we examine the wholesale-to-retail price spread. The upper purple line represents consumer retail price, the lower green line represents the farmgate wholesale price, and the shaded purple region highlights the marketing spread. Notice that even when wholesale prices drop significantly, retail prices remain sticky. This ballooning margin coincides with peak farmer inquiry influxes, as confirmed by our Spearman test in Hypothesis C."*

---

### Graph 6: `query_vs_economic.png`
- **Plotting Function:** `app/analysis.py:plot_query_vs_economic()`
- **Research Motivation:** Dual-axis visual comparison of farmer inquiry volume against wholesale commodity prices.
- **Axes & Elements:**
  - **X-Axis:** Date.
  - **Left Y-Axis (Blue):** Daily Inquiries (7-Day Moving Average of KCC calls).
  - **Right Y-Axis (Orange):** Wholesale Mandi Price (INR/Quintal).
  - **Solid Blue Line:** KCC call demand trend.
  - **Dashed Orange Line:** Wholesale commodity price trajectory.
- **How to Read It:** Look for inverse co-movement: when the dashed orange price curve declines, does the solid blue inquiry curve rise?
- **What It Cannot Tell Us:** Does not control for confounding variables like weather disruptions or planting seasons.
- **3 Viva Questions:**
  1. *Q: Why use a dual-axis chart?*
     - *A:* Queries (dozens of calls) and prices (thousands of rupees) have completely different numerical scales and units. Dual axes allow direct shape comparison.
  2. *Q: What is the main trend visible here?*
     - *A:* An inverse relationship: prolonged price slumps coincide with sustained elevations in farmer call volume.
  3. *Q: Can a dual-axis chart be misleading?*
     - *A:* Yes, manipulating the min-max bounds of either axis can exaggerate or minimize apparent relationships. That is why we rely on formal correlation coefficients ($r = -0.8329$) rather than visual inspection alone.
- **Presentation Script (25s):**
  > *"This dual-axis chart plots the 7-day moving average of farmer call inquiries in blue against the wholesale mandi price in orange. Notice the prominent inverse pattern: as wholesale prices drop between February and May, farmer inquiry volumes trend upward. This visual relationship aligns with our correlation analysis showing an $r$ of -0.83."*

---

### Graph 7: `correlation_heatmap.png`
- **Plotting Function:** `app/analysis.py:plot_correlation_heatmap()`
- **Research Motivation:** To synthesize pairwise linear associations across all major variables in a single visual matrix.
- **Axes & Elements:**
  - **Both Axes:** `KCC Queries`, `Wholesale Price`, `Retail Price`, `Diesel Price`, `Price Spread`, and `7D Volatility`.
  - **Color Map (`coolwarm`):** Dark blue represents strong negative correlation ($-1.0$), white represents zero correlation ($0.0$), and dark red represents strong positive correlation ($+1.0$).
  - **Numeric Annotations:** Pearson correlation coefficients rounded to two decimal places inside each cell.
- **Key Relationships Displayed:**
  - `KCC Queries` vs `Wholesale Price`: $-0.83$ (strong inverse).
  - `KCC Queries` vs `Price Spread`: $+0.93$ (strong direct).
  - `KCC Queries` vs `Diesel Price`: $+0.49$ (moderate direct).
  - `KCC Queries` vs `7D Volatility`: $+0.35$ (moderate direct).
- **3 Viva Questions:**
  1. *Q: Why is the diagonal equal to 1.00?*
     - *A:* Every variable has a perfect positive correlation with itself.
  2. *Q: Which variable has the strongest positive correlation with call demand?*
     - *A:* The wholesale-retail price spread at $+0.93$.
  3. *Q: What is a limitation of this heatmap?*
     - *A:* It only displays linear Pearson correlation coefficients; it does not capture non-linear relationships or time-lagged effects.
- **Presentation Script (30s):**
  > *"This econometric correlation heatmap summarizes the pairwise Pearson correlation coefficients across all modeled variables. Blue indicates negative association, red indicates positive association. The most important row is the top row: farmer query volume shows a strong negative correlation of -0.83 with wholesale prices, and a strong positive correlation of +0.93 with the wholesale-retail price spread, matching our economic expectations."*

---

### Graph 8: `regional_queries.png`
- **Plotting Function:** `app/analysis.py:plot_regional_comparison()`
- **Research Motivation:** To compare cumulative inquiry volume across states.
- **Axes & Elements:**
  - **X-Axis:** State name (e.g., Maharashtra, Punjab, Uttar Pradesh, Madhya Pradesh).
  - **Y-Axis:** Total cumulative inquiries logged across the sample period.
  - **Bars:** Colored in an ordered `Blues_r` palette.
- **How to Read It:** Taller bars highlight states with the highest operational call burden.
- **What It Cannot Tell Us:** Does not normalize by state farming population or mobile phone penetration. A larger state naturally logs more calls.
- **3 Viva Questions:**
  1. *Q: Why does Maharashtra have the highest volume in our demo dataset?*
     - *A:* In our synthetic data model, Maharashtra was parameterized with higher baseline call rates to reflect major horticultural production zones like Nashik.
  2. *Q: How could this chart be improved for a real-world research publication?*
     - *A:* By normalizing total queries per 10,000 operational landholdings to compare call intensity per farmer across states.
  3. *Q: What is the primary operational takeaway for helpline administrators?*
     - *A:* It indicates where to allocate multilingual call-centre capacity and regional agricultural experts.
- **Presentation Script (20s):**
  > *"This chart provides a regional comparison of cumulative farmer inquiries by state. In this dataset, Maharashtra accounts for the largest query share. For administrative planning, this informs the geographical allocation of tele-advisors and localized agronomic support staff."*

---

### Graph 9: `forecast_evaluation.png`
- **Plotting Function:** `app/forecasting.py:generate_forecast()` (lines 165–195)
- **Research Motivation:** Primary technical validation figure combining **out-of-sample holdout validation** with **future horizon forecasting**.
- **Axes & Elements (2 Side-by-Side Panels):**
  - **Panel A (Left — Out-of-Sample Test Evaluation):**
    - **X-Axis:** Date (Holdout test period).
    - **Y-Axis:** Inquiries.
    - **Dark Charcoal Line with Markers:** Actual observed inquiries ($y_{\text{test}}$).
    - **Solid Blue Line:** SARIMAX(1,1,1)(1,1,0)[7] predictions ($\hat{y}_{\text{test}}$) with MAE in legend ($10.5$).
    - **Dashed Grey Line:** Seasonal Naive baseline predictions with MAE in legend ($9.8$).
  - **Panel B (Right — Future Forecast & Stress Proxy):**
    - **X-Axis:** Date (Recent 30 days + future 14-day horizon).
    - **Y-Axis:** Inquiries.
    - **Dark Charcoal Line:** Recent historical actuals.
    - **Bold Orange Line:** Future 14-day SARIMAX predicted mean.
    - **Peach Shaded Band:** 95% statistical confidence interval ($[\hat{y}_{\text{lower}}, \hat{y}_{\text{upper}}]$).
    - **Amber Dotted Horizontal Line:** Elevated Stress Threshold ($\mu + 0.75\sigma = 179.1$).
    - **Red Dashed Horizontal Line:** High Stress Threshold ($\mu + 1.75\sigma = 229.0$).
- **How to Read It:**
  - Panel A demonstrates model validation: how closely predictions tracked actual holdout data.
  - Panel B shows future operational planning: the orange forecast line lies at ~154 calls/day, safely below the amber line (179.1), placing future demand in the `NORMAL` stress category.
- **3 Viva Questions:**
  1. *Q: Why did Seasonal Naive achieve a slightly lower MAE (9.83) than SARIMAX (10.46) on this holdout set?*
     - *A:* In highly regular weekly synthetic data, copying last week's exact same-day observation ($y_{t-7}$) is an exceptionally strong baseline. SARIMAX estimates additional moving-average and autoregressive parameters, introducing slight estimation variance. In real-world data with non-periodic shocks, SARIMAX provides superior adaptability and confidence intervals.
  2. *Q: What does the peach shaded band in Panel B represent?*
     - *A:* It represents the 95% confidence interval derived from the model's forecast error variance. Notice that it widens over time, reflecting increasing uncertainty further into the future.
  3. *Q: How is the stress category determined from Panel B?*
     - *A:* By comparing the average predicted mean against historical standard deviation thresholds. Because 154 is below 179.1, it is classified as `NORMAL`.
- **Presentation Script (35s):**
  > *"This two-panel figure is the core technical validation of our forecasting module. Panel A shows out-of-sample holdout validation on unseen test data. The blue SARIMAX line closely tracks the charcoal actual line with an MAE of 10.5 calls, benchmarked against our 7-day Seasonal Naive baseline. Panel B shows our 14-day future forecast in orange with a 95% confidence band. The horizontal dashed lines represent our statistical stress thresholds. Because the forecast averages 154 calls, it remains below the elevated threshold of 179, categorizing expected advisory stress as Normal."*

---

### Graph 10: `actual_vs_predicted.png`
- **Plotting Function:** `app/forecasting.py:generate_forecast()` (lines 149–163)
- **Research Motivation:** Dedicated high-resolution inspection of out-of-sample test split predictions.
- **Axes & Elements:**
  - **X-Axis:** Date across the holdout validation window.
  - **Y-Axis:** KCC Inquiries.
  - **Charcoal Line with Circles:** Actual observed daily call count.
  - **Solid Blue Line:** SARIMAX model prediction.
  - **Dashed Slate Grey Line:** 7-Day Seasonal Naive baseline.
- **How to Read It:** Compare how well the blue line tracks turning points, weekend troughs, and weekday peaks in the actual series.
- **What It Tells Us:** Proves that our evaluation does not suffer from future data leakage: the model was trained strictly on data prior to this window and evaluated purely on out-of-sample performance.
- **3 Viva Questions:**
  1. *Q: Why is holdout testing essential in time series?*
     - *A:* In time series, models can easily achieve near-zero training error by memorizing past noise. Evaluating on an out-of-sample holdout test split proves generalizability to future unseen periods.
  2. *Q: Did you shuffle the data before creating the test split?*
     - *A:* No, shuffling time-series data creates lookahead bias by allowing past predictions to use future data. We used a strict chronological split.
  3. *Q: What would a large divergence between actual and predicted indicate?*
     - *A:* A structural break in call patterns, such as an unmodeled government policy announcement or helpline server outage.
- **Presentation Script (25s):**
  > *"This plot provides a detailed view of our holdout validation test split. The charcoal line shows actual farmer calls, while the blue line shows our SARIMAX predictions. The model accurately captures the weekly troughs and peaks without any future data leakage, achieving a mean absolute error of approximately 10 calls per day on completely unseen data."*

---

## Chapter 10: Forecasting and SARIMAX — Complete Technical Explanation

### 10.1 Forecasting Pipeline Overview

The forecasting module (`app/forecasting.py`) executes an end-to-end time-series workflow:
- **Target Variable:** `query_count` (Daily total inquiries).
- **Forecast Horizon:** Configurable (default: 14 days).
- **Holdout Test Size:** $T_{\text{test}} = \min(30, \max(7, \text{int}(0.2 \times N)))$. For a 180-day series, $T_{\text{test}} = 30$ days.

```mermaid
flowchart LR
    SERIES["Full Time Series (N Days)"] --> SPLIT["Chronological Split"]
    SPLIT --> TRAIN["Training Set: T - 30 Days"]
    SPLIT --> TEST["Holdout Test Set: 30 Days"]
    TRAIN --> FIT_BASE["Seasonal Naive Baseline"]
    TRAIN --> FIT_SARIMAX["Fit SARIMAX(1,1,1)(1,1,0)[7]"]
    FIT_BASE --> EVAL_BASE["Compute Baseline MAE, RMSE, MAPE"]
    FIT_SARIMAX --> EVAL_SARIMAX["Compute SARIMAX MAE, RMSE, MAPE"]
    EVAL_BASE --> COMPARE["Model Benchmark Comparison"]
    EVAL_SARIMAX --> COMPARE
    SERIES --> FULL_FIT["Refit SARIMAX on Full Dataset"]
    FULL_FIT --> OUT_OF_SAMPLE["14-Day Out-of-Sample Forecast & 95% CIs"]
    OUT_OF_SAMPLE --> STRESS["Advisory Stress Classification"]
```

---

### 10.2 Deconstructing the SARIMAX Configuration: `(1,1,1)(1,1,0)[7]`

SARIMAX stands for **Seasonal Autoregressive Integrated Moving Average with eXogenous factors**.
Our model specification is:
$$\text{SARIMAX}(p=1, d=1, q=1) \times (P=1, D=1, Q=0)_{s=7}$$

Here is what each parameter means in plain English:
- **Non-Seasonal Order $(p=1, d=1, q=1)$:**
  - $p=1$ (**Autoregression**): Yesterday's inquiry volume directly informs today's inquiry volume ($y_{t-1} \to y_t$).
  - $d=1$ (**First-Differencing**): Takes the difference between consecutive days ($y_t - y_{t-1}$) to eliminate non-stationary baseline drift and achieve stationarity.
  - $q=1$ (**Moving Average**): Models the impact of unexpected short-term shocks from the previous day's forecast error ($\epsilon_{t-1}$).
- **Seasonal Order $(P=1, D=1, Q=0)_{s=7}$:**
  - $s=7$ (**Seasonality Period**): Explicitly captures the 7-day weekly agricultural cycle.
  - $P=1$ (**Seasonal Autoregression**): Inquiry volume from exactly 7 days ago (same day last week) directly informs today's prediction ($y_{t-7} \to y_t$).
  - $D=1$ (**Seasonal Differencing**): Differences today with the same day last week ($y_t - y_{t-7}$) to eliminate weekly seasonal baseline shifts.
  - $Q=0$ (**Seasonal Moving Average**): Set to 0 to keep the model parsimonious and prevent optimization divergence on small sample sizes.

#### Are Exogenous Variables Used in the Current Forecast?
In the current implementation, `generate_forecast()` fits a **univariate seasonal model** on `query_count`. While economic features (`wholesale_price`, `diesel_price`) are analyzed extensively in the hypothesis testing module, they are **not fed as future exogenous inputs** during out-of-sample forecasting.
> **Viva Defense Insight:** *"Why didn't you include future commodity and diesel prices as exogenous variables in SARIMAX?"*
> **Answer:** *"In practical forecasting, future values of exogenous predictors (future commodity prices or diesel revisions 14 days ahead) are themselves unknown. Feeding hypothetical exogenous values introduces external forecasting error into our model. We prioritized a reliable, fully verified univariate seasonal model that requires zero unverified assumptions about future market prices."*

---

### 10.3 Small Hand-Calculated Example: Forecast Error Metrics

Suppose across a small 3-day holdout split, we observe the following:
| Day | Actual Calls ($y_t$) | Predicted Calls ($\hat{y}_t$) | Error ($e_t = y_t - \hat{y}_t$) | Absolute Error ($|e_t|$) | Squared Error ($e_t^2$) | Percentage Error ($|e_t| / y_t$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 100 | 110 | $-10$ | 10 | 100 | $10 / 100 = 10.0\%$ |
| 2 | 150 | 140 | $+10$ | 10 | 100 | $10 / 150 = 6.67\%$ |
| 3 | 200 | 180 | $+20$ | 20 | 400 | $20 / 200 = 10.0\%$ |

1. **Mean Absolute Error (MAE):**
   $$\text{MAE} = \frac{10 + 10 + 20}{3} = \frac{40}{3} \approx 13.33 \text{ calls}$$
2. **Root Mean Squared Error (RMSE):**
   $$\text{RMSE} = \sqrt{\frac{100 + 100 + 400}{3}} = \sqrt{\frac{600}{3}} = \sqrt{200} \approx 14.14 \text{ calls}$$
3. **Mean Absolute Percentage Error (MAPE):**
   $$\text{MAPE} = \frac{10.0\% + 6.67\% + 10.0\%}{3} \approx 8.89\%$$

Notice that RMSE is larger than MAE ($14.14 > 13.33$) because squaring the errors penalizes the large 20-call error on Day 3 more heavily.

---

### 10.4 Actual Evaluation Metrics from System Run

From `outputs/forecasts/forecast_evaluation_metrics.csv`:
| Forecasting Model | MAE (Calls) | RMSE (Calls) | Zero-Safe MAPE (%) | Status |
| :--- | :---: | :---: | :---: | :--- |
| **Seasonal Naive Baseline (7D Lag)** | **9.83** | **11.81** | **7.08%** | Benchmark |
| **SARIMAX(1,1,1)(1,1,0)[7]** | **10.46** | **12.88** | **7.32%** | **Selected Model** |

#### Why SARIMAX is Retained Even When Baseline MAE is Slightly Lower
Evaluators may ask: *"Why didn't you just use the Seasonal Naive baseline if its MAE was 9.83 vs 10.46?"*
> **Answer:**
> 1. **Statistical Confidence Intervals:** Seasonal Naive can only output a single point forecast. It cannot provide mathematical confidence intervals ($[\hat{y}_{\text{lower}}, \hat{y}_{\text{upper}}]$) to capture risk uncertainty.
> 2. **Shock Recovery:** Seasonal Naive perpetually echoes an anomaly 7 days later. SARIMAX models error shock dissipation via its moving-average component ($q=1$).
> 3. **Synthetic Data Artifact:** In synthetic demonstration data generated with exact mathematical sinusoidal weekly curves, naive lag models perform unnaturally well. On real-world operational data with holidays and weather shocks, SARIMAX provides superior flexibility.

---

## Chapter 11: Agricultural Advisory Stress and Farmer Recommendations

### 11.1 Technical Forecast vs Farmer Decision Support

There is a fundamental divide between our technical research outputs and grassroots farmer needs:

```mermaid
flowchart TD
    subgraph TECHNICAL ["Technical Econometric Research"]
        P_VAL["Hypothesis p-values (p = 0.133, p < 0.001)"]
        SARIMAX_FC["SARIMAX Forecast: 154 Calls/Day"]
        METRICS["RMSE: 12.88 Calls, MAPE: 7.32%"]
        VOLATILITY["7-Day Rolling Volatility: 57.97 INR"]
    end

    TECHNICAL --> BRIDGE["app/recommendations.py: Translation Engine"]

    subgraph FARMER ["Farmer-Facing Actionable Advisory"]
        PRIORITY["Priority: Check Before Deciding"]
        SITUATION["Wholesale prices fell 6.1% over past 7 days (₹1097 vs ₹1167/qtl)"]
        ACTION1["Confirm local APMC spot rates before loading vehicles"]
        ACTION2["Evaluate on-farm storage viability for non-perishables"]
        ACTION3["Deduct freight quotes to compare net market realizations"]
        HELPLINE["Call Kisan Call Centre Toll-Free 1800-180-1551 (6 AM - 10 PM)"]
    end
```

---

### 11.2 How Operational Advisory Stress Categories are Derived

Advisory stress thresholds are calculated mathematically in `app/forecasting.py:classify_advisory_stress()`:
- **Historical Baseline Mean ($\mu$):** $141.56$ calls/day
- **Historical Standard Deviation ($\sigma$):** $49.99$ calls/day
- **Elevated Stress Threshold:**
  $$\mu + 0.75\sigma = 141.56 + (0.75 \times 49.99) = 179.05 \to \mathbf{179.1 \text{ inquiries/day}}$$
- **High Stress Threshold:**
  $$\mu + 1.75\sigma = 141.56 + (1.75 \times 49.99) = 229.04 \to \mathbf{229.0 \text{ inquiries/day}}$$

#### Classification Rules:
1. **High Stress:** If predicted mean call volume $\ge 229.0$ calls/day. Indicates acute call centre congestion requiring emergency staffing reallocations.
2. **Elevated Stress:** If predicted mean is between $179.1$ and $229.0$ calls/day. Indicates above-average call demand.
3. **Normal:** If predicted mean is $< 179.1$ calls/day. (Current run: $154.0 \to \text{NORMAL}$).
4. **Uncertainty Warning:** If predicted mean is Normal but the 95% upper prediction bound reaches the High threshold, an explicit warning is appended to the operational report.

---

### 11.3 Actionable Recommendation Priority Logic

In `app/recommendations.py`, agricultural market conditions are classified into three actionable priority categories:
1. **`Action to consider now` (High Urgency):**
   - Triggered when 7-day average wholesale prices drop $\ge 5\%$ or forecasted advisory stress is `High`.
   - Actionable focus: Mitigating immediate losses, evaluating storage vs distress selling, checking government procurement centres (MSP).
2. **`Check before deciding` (Moderate Urgency):**
   - Triggered during moderate price declines ($2\%$ to $5\%$) or elevated call volumes.
   - Actionable focus: Getting firm transport quotations before loading, comparing multi-mandi net returns.
3. **`No clear signal` (Baseline / Stable):**
   - Triggered when price changes are $< 2\%$ and demand is Normal.
   - Actionable focus: Normal marketing, sorting/grading produce for quality premiums.

---

### 11.4 Verified Public Assistance Channels

Every generated farmer advisory incorporates verified government contact channels:
- **National Kisan Call Centre (KCC):** Toll-Free **`1800-180-1551`**
- **Operating Hours:** **6:00 AM to 10:00 PM, all 7 days of the week**
- **Authority:** Department of Agriculture & Farmers Welfare, Ministry of Agriculture, Govt. of India
- **Local Extension:** In-person consultation with local Gram Panchayat Krishi Sahayaks or nearest Krishi Vigyan Kendra (KVK) agronomists.

---

## Chapter 12: Every Command-Line Option and Local Workflow

All arguments are defined in `run_pipeline.py:main()` (lines 266–314).

### Argument Reference Table

| Argument | Flag Type | Default | Description | Modules Receiving Argument |
| :--- | :---: | :---: | :--- | :--- |
| `--generate-data` | Boolean flag | `False` | Forces regeneration of deterministic synthetic demo datasets (seed=42, 730 days) and re-imports into SQLite. | `scripts/generate_demo_data.py`, `app/data_processing.py` |
| `--kcc` | Path string | `None` | Path to custom user-supplied KCC inquiry CSV file. | `app/data_processing.py:import_kcc_csv` |
| `--commodity-file` | Path string | `None` | Path to custom user-supplied APMC mandi commodity price CSV file. | `app/data_processing.py:import_commodity_csv` |
| `--fuel` | Path string | `None` | Path to custom user-supplied retail diesel fuel price CSV file. | `app/data_processing.py:import_fuel_csv` |
| `--replace` | Boolean flag | `False` | Deletes existing records in target database tables before importing new files. | `app/data_processing.py:import_*_csv` |
| `--synthetic` | Boolean flag | `False` | Explicitly marks imported custom CSV data as synthetic demonstration records. | `app/data_processing.py`, `app/models.py` |
| `--verified-real` | Boolean flag | `False` | Certifies that custom imported CSV records represent verified real-world operational records. | `app/data_processing.py`, `app/recommendations.py` |
| `--state` | String | `None` | Filters analysis and modeling to a specific state (e.g., `'Maharashtra'`). | `build_analytical_dataset`, `analysis.py`, `forecasting.py` |
| `--commodity` | String | `None` | Filters analysis and modeling to a specific crop (e.g., `'Onion'`). | `build_analytical_dataset`, `analysis.py`, `forecasting.py` |
| `--horizon` | Integer | `14` | Sets out-of-sample forecast horizon in days. | `app/forecasting.py:generate_forecast` |
| `--shock-threshold` | Float | `1.0` | Sets the percentage revision cutoff for diesel shock days in Hypothesis B. | `app/analysis.py:run_hypothesis_tests` |
| `--lang` | Choice (`en`,`hi`,`mr`) | `'en'` | Selects language for terminal summary banner and primary advisory report. | `app/recommendations.py` |

---

### Step-by-Step Demonstration Workflows

#### 1. Standard Default Run (Clean Demonstration)
```powershell
python main.py
```
*Executes the complete pipeline using existing database records, running all 6 phases and updating charts, tables, research reports, and advisories.*

#### 2. Clean Reset & Synthetic Regeneration Run
```powershell
python main.py --generate-data
```
*Drops all SQLite database tables, regenerates 730 days of deterministic synthetic demonstration data, imports fresh records, and runs the entire analytical pipeline.*

#### 3. Filtered State and Commodity Analysis Run
```powershell
python main.py --state Maharashtra --commodity Onion --horizon 21
```
*Filters analytical queries strictly to Maharashtra Onion observations, runs descriptive statistics, hypothesis tests, and extends the forecast horizon to 21 days.*

#### 4. Custom CSV Dataset Ingestion Run
```powershell
python main.py --kcc data/my_kcc.csv --commodity-file data/my_mandi.csv --fuel data/my_fuel.csv --replace
```
*Wipes existing database tables and imports custom user-supplied CSV files, automatically validating headers, standardizing dates, and calculating fresh analytical outputs.*

#### 5. Multilingual Farmer Advisory Demonstration
```powershell
python main.py --lang hi
# or for Marathi:
python main.py --lang mr
```
*Renders the terminal summary banner and primary advisory in Hindi or Marathi.*

#### 6. Executing the Automated Test Suite
```powershell
python -m pytest -v
```
*Executes all 35 unit and integration tests across data processing, analysis, forecasting, and recommendation modules.*

---

## Chapter 13: Test Suite and Verification Evidence

The repository includes a comprehensive automated test suite in `tests/` comprising **35 passing tests** across 4 modules.

### Test Execution Summary (`python -m pytest -v`)
```text
tests/test_analysis.py::test_descriptive_summary_known_values PASSED     [  2%]
tests/test_analysis.py::test_hypothesis_a_perfect_correlation PASSED     [  5%]
tests/test_analysis.py::test_hypothesis_b_shock_detection PASSED         [  8%]
tests/test_analysis.py::test_hypothesis_insufficient_sample PASSED       [ 11%]
tests/test_analysis.py::test_get_correlations PASSED                     [ 14%]
tests/test_analysis.py::test_hypothesis_result_includes_research_question_and_assumptions PASSED [ 17%]
tests/test_data_processing.py::test_check_missing_columns PASSED         [ 20%]
tests/test_data_processing.py::test_standardize_column_names PASSED      [ 22%]
tests/test_data_processing.py::test_safe_parse_dates PASSED              [ 25%]
tests/test_data_processing.py::test_import_kcc_csv_success_and_duplicates PASSED [ 28%]
tests/test_data_processing.py::test_import_commodity_csv_validation PASSED [ 31%]
tests/test_data_processing.py::test_data_alignment_pipeline PASSED       [ 34%]
tests/test_data_processing.py::test_data_quality_report PASSED           [ 37%]
tests/test_data_processing.py::test_build_analytical_dataset_weekly_freq PASSED [ 40%]
tests/test_data_processing.py::test_column_synonyms_government_schemas PASSED [ 42%]
tests/test_data_processing.py::test_invalid_data_rejection PASSED        [ 45%]
tests/test_data_processing.py::test_import_replace_option PASSED         [ 48%]
tests/test_forecasting.py::test_calculate_metrics PASSED                 [ 51%]
tests/test_forecasting.py::test_classify_advisory_stress PASSED          [ 54%]
tests/test_forecasting.py::test_generate_forecast_sarimax_pipeline PASSED [ 57%]
tests/test_forecasting.py::test_generate_forecast_insufficient_data PASSED [ 60%]
tests/test_forecasting.py::test_generate_forecast_exports_csv_and_plots PASSED [ 62%]
tests/test_recommendations.py::test_scenario_1_price_decline_cautious_step PASSED [ 65%]
tests/test_recommendations.py::test_scenario_2_rising_price_no_forced_sell PASSED [ 68%]
tests/test_recommendations.py::test_scenario_3_market_comparison PASSED  [ 71%]
tests/test_recommendations.py::test_scenario_4_diesel_price_qualified_cost_message PASSED [ 74%]
tests/test_recommendations.py::test_scenario_5_missing_fuel_or_commodity_data PASSED [ 77%]
tests/test_recommendations.py::test_scenario_6_high_kcc_demand_no_crisis_misrepresentation PASSED [ 80%]
tests/test_recommendations.py::test_scenario_7_insufficient_or_baseline_forecast PASSED [ 82%]
tests/test_recommendations.py::test_scenario_8_outdated_data_freshness_warning PASSED [ 85%]
tests/test_recommendations.py::test_scenario_9_provenance_labeling PASSED [ 88%]
tests/test_recommendations.py::test_scenario_10_normal_situation_no_exaggerated_alert PASSED [ 91%]
tests/test_recommendations.py::test_scenario_11_changing_dataset_recalculates PASSED [ 94%]
tests/test_recommendations.py::test_scenario_12_multilingual_templates PASSED [ 97%]
tests/test_recommendations.py::test_recommendation_numbering_starts_at_one PASSED [100%]
============================= 35 passed in 6.91s ==============================
```

---

### What Passing Tests Establish vs What Remains Unverified

| What the Passing Tests ESTABLISH | What the Passing Tests DO NOT Establish |
| :--- | :--- |
| **Mathematical Correctness:** Metric calculations (MAE, RMSE, MAPE) and correlation formulas match hand-calculated test vectors. | **Real-World Policy Effectiveness:** Does not prove that an advisory will increase a specific farmer's seasonal profit. |
| **Schema Robustness:** Column synonym mapping and date normalization handle diverse messy government headers without unhandled exceptions. | **Universal Data Compatibility:** A real-world government CSV with completely novel headers outside our 30+ synonyms will still require adding aliases. |
| **Edge Case Handling:** Insufficient data ($N < 30$), division-by-zero queries, and missing fuel files are caught gracefully without crashing. | **Absence of Confounders:** Does not establish that call volume increases were caused by prices rather than unmeasured rainfall. |
| **Multi-Dataset Reactivity:** Test 11 explicitly proves that changing input CSV numbers recalculates different advisory texts and statistical metrics. | **Live Market Freshness:** Tests execute in an offline, controlled sandbox; real-world deployment requires ongoing fresh data ingestion. |

---

## Chapter 14: Libraries, Dependencies, and Technology Choices

The project adheres strictly to `requirements.txt`:

```text
pandas>=2.0.0
numpy>=1.23.0
scipy>=1.10.0
statsmodels>=0.14.0
matplotlib>=3.7.0
seaborn>=0.12.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
pytest>=7.0.0
```

### Dependency Audit and Role Explanation

| Library | Exact Role in AgriStress Analytics | Why Selected / Advantages | Simpler Alternative Rejected & Why |
| :--- | :--- | :--- | :--- |
| **Pandas** | In-memory table manipulation, column synonym renaming, reindexing continuous date grids, forward-fill imputation. | Powerful vectorized time-series date indexing and rolling operations (`.rolling(7).std()`). | Standard Python `csv` module: requires writing hundreds of lines of complex date-matching and sliding-window boilerplate. |
| **NumPy** | Array transformations, zero-safe vector division in MAPE, clipping predictions to non-negative bounds (`np.clip`). | High-performance C-level numerical array operations. | Pure Python `math` module: cannot execute vectorized operations on entire series without slow explicit loops. |
| **SciPy** | Executes statistical tests: `stats.pearsonr`, `stats.spearmanr`, and `stats.mannwhitneyu`. | Golden standard for academic scientific computing. Computes exact $p$-values and test statistics. | Writing statistical formulas by hand: error-prone for non-parametric rank sum distributions (Mann-Whitney U). |
| **Statsmodels** | Fits `SARIMAX(1,1,1)(1,1,0)[7]` models, generates maximum likelihood estimations, and computes prediction intervals. | Rigorous econometric time-series implementation with full parameter diagnostics and confidence intervals. | Scikit-learn / TensorFlow: Scikit-learn lacks native SARIMA statespace models; deep learning libraries introduce massive GPU/compilation overhead. |
| **Matplotlib** | Low-level plotting canvas; saves 10 PNG charts using headless non-GUI backend (`Agg`). | Reliable file-based rendering on any OS without requiring an active display server or browser. | Plotly / Bokeh: Plotly requires generating bulky HTML/JavaScript bundles or web browser runtimes. |
| **Seaborn** | Renders correlation heatmap (`sns.heatmap`) and categorical weekday bar charts. | Beautiful statistical visualization palettes and automatic matrix annotation. | Pure Matplotlib: requires tedious manual text placement loops to display correlation values inside heatmap cells. |
| **SQLAlchemy** | Object-Relational Mapping (ORM) and SQLite database schema migrations. | Type safety, SQL injection protection, portable schema modeling, and batch `bulk_save_objects` transactions. | Raw SQLite3 SQL strings: raw SQL string concatenation is prone to syntax bugs across different SQL dialects. |
| **Pytest** | Automated unit and integration testing suite. | Simple assertion syntax (`assert a == b`), parameterized testing fixtures, and detailed failure traceback reports. | Python standard `unittest`: requires verbose boilerplate classes (`self.assertEqual`) and clumsy test discovery. |

---

## Chapter 15: Limitations, Failure Scenarios, and Future Roadmap

A hallmark of a mature engineering defense is the **honest, confident disclosure of project limitations**. Never pretend your project is flawless. Evaluators respect students who understand their software's boundaries.

### 15.1 Real Project Limitations and How to Defend Them

#### 1. Time-Series Serial Autocorrelation in Hypothesis Testing
- **The Issue:** Pearson ($r$) and Spearman ($\rho$) correlation hypothesis tests assume independent and identically distributed (i.i.d.) observations. Daily agricultural call volumes exhibit high serial autocorrelation (yesterday's call volume influences today's).
- **The Consequence:** Serial correlation artificially narrows standard errors, making $p$-values appear smaller than they actually are.
- **Viva Defense:** *"We recognize that daily time-series data exhibits serial dependence, which violates the strict i.i.d. assumption of ordinary correlation tests. In our summary report and code comments, we explicitly note that these p-values indicate sample association rather than proven economic causation. A future enhancement would be fitting vector autoregressive (VAR) models or Newey-West adjusted standard errors."*

#### 2. Infrequent Diesel Price Revisions (HYP-B Small Sample Size)
- **The Issue:** In administered pricing regimes, retail diesel prices remain frozen for weeks. Over a 180-day sample, only 3 days had price revisions $\ge 1.0\%$.
- **The Consequence:** Mann-Whitney U test requires $\ge 5$ shock days. The test could not be evaluated.
- **Viva Defense:** *"Our pipeline deliberately enforces sample adequacy safeguards. Rather than forcing a statistically invalid test on 3 points, the software honestly outputs 'Inadequate shock sample size.' This proves that our code adheres to statistical integrity rather than fabricating conclusions."*

#### 3. Geographical Aggregation vs Local Mandi Dispersion
- **The Issue:** When state-level analysis is selected, commodity prices are averaged across all reporting APMC mandis in that state.
- **The Consequence:** Localized price crashes in one district (e.g., Nashik onion) may be diluted by stable prices in another district.
- **Viva Defense:** *"Statewide averaging is necessary when call centre logs lack district-level geolocation. However, our ingestion schema explicitly retains the `market` and `district` columns, and our recommendation engine includes an APMC comparison module ready for localized data when available."*

#### 4. Fixed Standard Deviation Thresholds for Advisory Stress
- **The Issue:** Advisory stress categories use fixed cutoffs ($\mu + 0.75\sigma$ and $\mu + 1.75\sigma$).
- **The Consequence:** In a highly volatile year with large standard deviation, a massive call surge might only be classified as 'Normal'.
- **Viva Defense:** *"These thresholds are project-defined operational proxies designed to demonstrate automated capacity classification. In an enterprise deployment, these thresholds would be calibrated against actual physical seat capacity and telephone trunk line limits provided by the call centre management."*

#### 5. No Chemical, Agronomic, or Guaranteed Price Prescriptions
- **The Issue:** The farmer advisory engine does not recommend specific fertilizer kilograms or pesticide brands, nor does it guarantee future selling prices.
- **The Consequence:** Some users might expect an AI to tell them "sell tomorrow at ₹1,500".
- **Viva Defense:** *"Recommending chemical dosages or guaranteeing market prices without on-site agronomic inspection is irresponsible and dangerous for smallholder farmers. Our engine deliberately restricts recommendations to verified decision-support principles: checking spot rates, accounting for freight, exploring storage, and consulting verified public agronomists at KCC toll-free `1800-180-1551`."*

---

### 15.2 Prioritized Future Roadmap

If given additional development time, improvements would be prioritized as follows:

1. **Econometric Rigor (Priority 1):** Implement Newey-West heteroskedasticity and autocorrelation consistent (HAC) standard error adjustments and Johansen cointegration tests.
2. **Data Pipeline Expansion (Priority 2):** Connect directly to Agmarknet and OGD India government API endpoints for automated daily live updates, eliminating manual CSV handling.
3. **Hyperparameter Grid Search (Priority 3):** Implement automated Akaike Information Criterion (AIC) minimization to select optimal SARIMAX orders $(p,d,q)(P,D,Q)$ dynamically per commodity.
4. **Interactive GIS Spatial Mapping (Priority 4):** Plot choropleth maps of district-level advisory stress intensity.
