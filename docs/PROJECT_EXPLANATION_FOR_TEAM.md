# AgriStress Analytics — Internal Project Explanation & Technical Handover Report

> **Audience:** Internal Project Team Members & Collaborators  
> **Purpose:** Comprehensive, plain-English technical guide explaining what we built, why we built it, how every line works, and how to independently run, test, explain, and modify the code.  
> **Academic Context:** First-Year Engineering / Semester Project  
> **Status:** Backend Complete, Verified, and Tested (26/26 Tests Passing)

---

# Table of Contents
1. [Part A: Understanding the Project](#part-a-understanding-the-project)
   - [1. What is AgriStress Analytics?](#1-what-is-agristress-analytics)
   - [2. The Complete Problem Statement](#2-the-complete-problem-statement)
   - [3. An Intuitive Real-World Example](#3-an-intuitive-real-world-example)
   - [4. What the Project Currently Does](#4-what-the-project-currently-does)
2. [Part B: Understanding the Complete System](#part-b-understanding-the-complete-system)
   - [5. End-to-End Architecture](#5-end-to-end-architecture)
   - [6. One Complete Example of the Data Flow](#6-one-complete-example-of-the-data-flow)
   - [7. Project Folder & File-by-File Explanation](#7-project-folder--file-by-file-explanation)
3. [Part C: Understanding the Data and Database](#part-c-understanding-the-data-and-database)
   - [8. Data Sources and Data Quality](#8-data-sources-and-data-quality)
   - [9. CSV Ingestion and Cleaning](#9-csv-ingestion-and-cleaning)
   - [10. Database Design & Schema](#10-database-design--schema)
4. [Part D: Understanding the Analytical and Mathematical Logic](#part-d-understanding-the-analytical-and-mathematical-logic)
   - [11. Data Processing and Feature Engineering](#11-data-processing-and-feature-engineering)
   - [12. Exploratory Data Analysis & Visualizations](#12-exploratory-data-analysis--visualizations)
   - [13. Statistical Hypothesis Testing](#13-statistical-hypothesis-testing)
   - [14. Time-Series Forecasting Using SARIMAX](#14-time-series-forecasting-using-sarimax)
   - [15. Agricultural Advisory Stress Indicator](#15-agricultural-advisory-stress-indicator)
5. [Part E: Understanding the Backend and API](#part-e-understanding-the-backend-and-api)
   - [16. FastAPI and Backend Logic](#16-fastapi-and-backend-logic)
   - [17. Reports, History, and Outputs](#17-reports-history-and-outputs)
   - [18. Configuration, Environment, and Deployment](#18-configuration-environment-and-deployment)
6. [Part F: How Teammates Can Use and Maintain the Project](#part-f-how-teammates-can-use-and-maintain-the-project)
   - [19. Complete Setup Guide from Scratch](#19-complete-setup-guide-from-scratch)
   - [20. Complete Demonstration Walkthrough](#20-complete-demonstration-walkthrough)
   - [21. Testing and Debugging](#21-testing-and-debugging)
   - [22. How to Modify the Code Safely](#22-how-to-modify-the-code-safely)
   - [23. Current Limitations and Next Steps](#23-current-limitations-and-next-steps)
   - [24. Glossary and Teammate Knowledge Checklist](#24-glossary-and-teammate-knowledge-checklist)

---

# Part A: Understanding the Project

## 1. What is AgriStress Analytics?

### The Core Idea in Plain English
**AgriStress Analytics** is a Python-only backend and research toolkit. Its goal is to study and forecast the volume of phone inquiries received from Indian farmers through the national **Kisan Call Centre (KCC)** toll-free helpline (1800-180-1551).

In India, over 140 million farming households make critical daily decisions:
- *When should I harvest?*
- *Should I sell my crop today or store it in a warehouse?*
- *Why is the mandi price falling so fast?*
- *How can I lower my diesel pumping costs for irrigation?*

When economic conditions become unpredictable—such as a sudden collapse in onion prices at the local APMC mandi, or a sharp hike in diesel fuel prices—farmers experience acute distress and seek guidance. They call the Kisan Call Centre.

### What Does "Agricultural Advisory Stress" Mean?
In our project, **advisory stress** does *not* mean mental stress of an individual farmer. Instead, it refers to **operational strain on the advisory support infrastructure**:
- When call volume spikes far above normal capacity, call centres face queue backlogs, long wait times, and unanswered inquiries.
- By forecasting upcoming call demand based on recent agricultural and economic trends, advisory administrators can proactively adjust operator shift schedules or prepare automated advisory advisories.

### Who Could Use This System?
1. **Call Centre Supervisors:** To schedule adequate agricultural agronomists on shifts ahead of predicted surges.
2. **State Agricultural Departments:** To identify districts where farmers are experiencing market panic or pest outbreaks.
3. **Agricultural Economists:** To investigate how commodity market volatility and fuel inflation correlate with farmer inquiries.

---

## 2. The Complete Problem Statement

The formal academic problem statement is:
> *"Econometric and Spatial-Temporal Analysis of Farmer Information Demand: Modeling Kisan Call Centre (KCC) Query Influx Against Commodity Price Spreads and Fuel Inflation Shocks to Forecast Agricultural Advisory Stress."*

Let us break down every technical term into everyday words:

| Term | Everyday Meaning |
| :--- | :--- |
| **Kisan Call Centre (KCC) Query Influx** | The number of incoming phone calls and agricultural inquiries received each day at government call centres. |
| **Commodity Prices** | The wholesale price at which agricultural produce (like onions, wheat, or tomatoes) is sold at APMC Mandis (regulated wholesale markets). |
| **Wholesale-to-Retail Price Spread** | The gap between what a farmer gets at the wholesale mandi ($P_{\text{wholesale}}$) and what urban consumers pay in retail shops ($P_{\text{retail}}$). If consumers pay ₹50/kg for onions while farmers only get ₹15/kg, the spread is ₹35/kg. |
| **Fuel Inflation Shocks** | Sudden, sharp increases in retail diesel fuel prices (e.g., a daily rise of $\ge 2\%$). Diesel powers irrigation pump sets and tractors, directly increasing cultivation expenses. |
| **Econometric Analysis** | Applying statistical mathematics to economic data to test whether two economic events move together. |
| **Spatial-Temporal Analysis** | Analyzing how data patterns change across different geographical **spaces** (states/districts) and over **time** (days, weeks, seasons). |
| **Forecasting** | Predicting future numbers (daily call counts for the next 14 to 30 days) based on past historical patterns using time-series models. |

### Research Boundary: Correlation vs. Causation
> [!IMPORTANT]
> **Correlation is not Causation.**  
> If our statistical tests show that falling commodity prices and rising call volumes happen at the same time ($p < 0.05$), this **proves an association**, but does **not prove that price crashes directly caused the calls**.  
> *Analogy:* Ice cream sales and drowning rates both spike in June. Eating ice cream does not cause drowning; hot summer weather causes people to both buy ice cream and go swimming. Similarly, monsoon weather patterns influence both farm harvest prices and farmer inquiry calls simultaneously.

---

## 3. An Intuitive Real-World Example

To understand how the pieces connect, imagine this illustrative, hypothetical scenario:

```
[Day 1-10]  Normal Conditions:
            - Wholesale Onion Price: ₹22/kg
            - Diesel Price: ₹90/Litre
            - KCC Call Influx: ~250 calls/day (Advisory Stress: NORMAL)

[Day 11]    The Shock:
            - Unseasonal rains hit Nashik district. Mandi wholesale price crashes to ₹12/kg.
            - Oil marketing companies announce a fuel revision: Diesel jumps to ₹93.5/Litre (+3.9%).

[Day 12-14] Farmer Response:
            - Farmers face higher pumping and hauling costs while crop revenue drops.
            - Uncertainty rises: "Should I hold my stock? Will prices recover?"
            - Calls to the KCC surge to 520 calls/day.

[System]    What AgriStress Analytics Does:
            1. Ingests the new CSV records into SQLite.
            2. Automatically detects a "Diesel Shock" (+3.9% >= 2.0% threshold).
            3. Detects negative commodity return (-45%) and widening margin spread.
            4. SARIMAX model projects future 14-day demand will stay above 480 calls/day.
            5. Flags Advisory Stress as [HIGH] (forecast > baseline mean + 1.75 * std).
            6. Produces a chart showing the surge with 95% confidence intervals.
```
*(Note: The numbers in this example are purely hypothetical to illustrate the system workflow.)*

---

## 4. What the Project Currently Does

### Fully Implemented and Working Features
1. **Automated CSV Ingestion & Quality Checking:** Reads KCC call logs, APMC commodity prices, and diesel rates. Validates columns, parses dates safely, filters duplicate rows, and logs results in `import_history`.
2. **Temporal Data Alignment:** Combines three disparate data feeds into one daily harmonized dataset (`data/processed/analytical_dataset.csv`) without multiplying row counts.
3. **Feature Engineering:** Calculates daily price differences, percentage returns, 7-day rolling volatility, wholesale-retail spreads, and lagged diesel changes.
4. **Econometric Hypothesis Testing:**
   - **Hypothesis A:** Pearson correlation test (commodity price percentage change vs. query demand).
   - **Hypothesis B:** Mann-Whitney U non-parametric two-sample test (diesel shock days vs. normal days).
   - **Hypothesis C:** Spearman rank correlation test (price spread vs. query demand).
5. **Exploratory Visualizations:** 8 Matplotlib/Seaborn charts saved to `outputs/charts/` covering trends, weekly seasonality, price spreads, regional breakdowns, and correlation heatmaps.
6. **Time-Series Forecasting (SARIMAX):**
   - Chronological 80/20 train-test splitting (no future data leakage).
   - Seasonal Naive baseline benchmark ($\hat{y}_t = y_{t-7}$).
   - $\text{SARIMAX}(1,1,1)(1,1,0)[7]$ fitting with weekly seasonality.
   - Computes MAE, RMSE, and zero-safe MAPE.
   - Non-negative count clipping and 95% prediction intervals.
7. **Advisory-Stress Classification:** Automatically categorizes future demand as `Normal`, `Elevated`, or `High` based on historical $\mu$ and $\sigma$.
8. **FastAPI REST API:** 16 endpoints for data status, ingestion, summary metrics, hypothesis testing, forecasting, and reporting. Local Swagger UI at `http://127.0.0.1:8000/docs`.
9. **Automated Research Summary Report:** Generates formatted markdown at `outputs/reports/summary_report.md`.
10. **Automated Test Suite:** 26 passing Pytest unit and integration tests.

### Incomplete or Planned Features (For Future Phases)
- **Live Government API Scraping:** Currently, the system reads local CSV files and synthetic demonstration data; live automated scraping of `data.gov.in` is planned.
- **Frontend User Interface:** Currently backend-only with Swagger UI; a React/Next.js dashboard is planned for the next semester phase.
- **District-Level Fuel Prices:** PPAC publishes fuel prices at the state capital/metro level; district-level rural fuel prices are not currently available in public government datasets.

---

# Part B: Understanding the Complete System

## 5. End-to-End Architecture

```mermaid
flowchart TD
    subgraph Data_Sources ["1. Data Sources"]
        KCC_CSV["KCC Query Logs CSV\n(Date, State, Calls)"]
        COMM_CSV["Agmarknet Commodity CSV\n(Date, Commodity, Price)"]
        FUEL_CSV["PPAC Diesel Fuel CSV\n(Date, Diesel Price)"]
    end

    subgraph Ingestion ["2. Ingestion & Validation (app/data_processing.py)"]
        VAL["Validation & Cleaning\n- Check required columns\n- Parse dates\n- Remove duplicate rows"]
    end

    subgraph Storage ["3. Storage (SQLite / PostgreSQL)"]
        DB[("agristress.db\nSQLAlchemy ORM")]
    end

    subgraph Alignment ["4. Harmonization & Feature Engineering"]
        ALIGN["Daily Continuous Grid Alignment\n- Sum queries by date\n- Forward-fill weekend prices\n- Compute returns, volatility, spread"]
        CSV_OUT["data/processed/analytical_dataset.csv"]
    end

    subgraph Analysis ["5. Analytics & Econometrics (app/analysis.py)"]
        STATS["Descriptive Statistics\n(Mean, Median, Std Dev)"]
        HYP["Hypothesis Tests\n- Hyp A: Pearson r\n- Hyp B: Mann-Whitney U\n- Hyp C: Spearman rho"]
        CHARTS["8 Visualization Plots\n(outputs/charts/*.png)"]
    end

    subgraph Forecasting ["6. Forecasting & Stress (app/forecasting.py)"]
        SARIMAX["SARIMAX(1,1,1)(1,1,0)[7]\nvs. 7-Day Seasonal Naive"]
        STRESS["Advisory Stress Classifier\n(Normal / Elevated / High)"]
        FC_PLOT["outputs/charts/forecast_evaluation.png"]
    end

    subgraph Delivery ["7. API & Reporting"]
        FASTAPI["FastAPI REST API\n(app/api.py & app/main.py)"]
        SWAGGER["Swagger UI Docs\n(http://127.0.0.1:8000/docs)"]
        REPORT["Research Summary Report\n(outputs/reports/summary_report.md)"]
    end

    Data_Sources --> Ingestion
    Ingestion --> Storage
    Storage --> Alignment
    Alignment --> CSV_OUT
    Alignment --> Analysis
    Alignment --> Forecasting
    Analysis --> CHARTS
    Analysis --> REPORT
    Forecasting --> FC_PLOT
    Storage --> FASTAPI
    Analysis --> FASTAPI
    Forecasting --> FASTAPI
    FASTAPI --> SWAGGER
```

### Technology Selection Rationale
- **Python 3.10:** The universal language for scientific computing and backend data engineering.
- **Pandas & NumPy:** For tabular operations, continuous date indexing, and numerical vectorized math.
- **SciPy:** Provides gold-standard statistical tests (`scipy.stats.pearsonr`, `mannwhitneyu`, `spearmanr`).
- **Statsmodels:** Provides the industry-standard `SARIMAX` implementation for seasonal time series.
- **SQLAlchemy 2.0:** Object-Relational Mapping (ORM) that allows switching from SQLite locally to PostgreSQL in cloud deployment without rewriting query logic.
- **FastAPI:** Fast, lightweight web framework that auto-generates interactive Swagger documentation.
- **Matplotlib & Seaborn:** Headless plotting (`matplotlib.use('Agg')`) that generates charts on server environments without needing a desktop window manager.

---

## 6. One Complete Example of the Data Flow

Let us trace a single incoming row of KCC call data through the entire system:

1. **Arrival:** A file named `kcc_queries.csv` arrives with a raw line:
   ```csv
   Observation Date,State Name,District,Query Type,Query Count
   2024-05-10, Maharashtra ,Nashik,Weather,28
   ```
2. **Ingestion & Cleaning (`import_kcc_csv` in `app/data_processing.py`):**
   - [standardize_column_names](file:///d:/python-capstone/app/data_processing.py#L22-L25) strips whitespace and converts headers to lowercase: `observation_date`, `state_name`, `district`, `query_type`, `query_count`.
   - [check_missing_columns](file:///d:/python-capstone/app/data_processing.py#L16-L19) verifies that `observation_date` and `state` are present.
   - [safe_parse_dates](file:///d:/python-capstone/app/data_processing.py#L28-L30) converts `"2024-05-10"` into a Python `datetime.date(2024, 5, 10)`. (If it was `"invalid-date"`, it becomes `NaT` and is rejected).
   - Duplicates are checked on `["parsed_date", "state", "query_type"]`.
3. **Database Insertion (`app/models.py`):**
   - The cleaned record is saved as a `KCCObservation` object in `agristress.db`.
   - An entry is logged in `import_history` recording total, accepted, and rejected row counts.
4. **Harmonization (`build_analytical_dataset`):**
   - All KCC queries for `2024-05-10` across all categories in Maharashtra are summed together.
   - The wholesale onion price (₹2,100) and diesel price (₹92.5) for that same date are joined horizontally on `observation_date`.
   - If `2024-05-10` was preceded by a non-trading day, the price is forward-filled from the previous trading day.
5. **Feature Engineering:**
   - Daily price difference is computed: $\text{wholesale\_price}_t - \text{wholesale\_price}_{t-1}$.
   - Percentage change is computed: `wholesale_price.pct_change(fill_method=None) * 100`.
6. **SARIMAX Model Fitting & Stress Rating (`app/forecasting.py`):**
   - The series of query counts is split into train (first 80%) and test (last 20%).
   - The model learns the weekly 7-day seasonality.
   - A 14-day out-of-sample forecast is computed.
   - The forecast value is compared against $\mu_{\text{historical}} + 0.75\sigma_{\text{historical}}$ to assign `Normal`, `Elevated`, or `High`.
7. **Delivery via API:**
   - A client calls `GET /api/v1/forecast/1` or `GET /api/v1/analysis/summary` and receives clean JSON with all values.

---

## 7. Project Folder & File-by-File Explanation

```
agristress-analytics/
├── app/
│   ├── __init__.py           # Package indicator
│   ├── config.py             # File paths and environment settings
│   ├── database.py           # SQLAlchemy database connection and SessionLocal
│   ├── models.py             # 5 Database tables defined as SQLAlchemy classes
│   ├── schemas.py            # Pydantic data schemas for validating API requests
│   ├── data_processing.py    # CSV cleaning, deduplication, and data alignment
│   ├── analysis.py           # Descriptive statistics, hypothesis tests, and charts
│   ├── forecasting.py        # Baseline naive, SARIMAX, and advisory stress logic
│   ├── api.py                # 16 FastAPI endpoint route handlers
│   └── main.py               # Main FastAPI server initialization and CORS setup
├── scripts/
│   ├── init_db.py            # CLI script to create SQLite database tables
│   ├── generate_demo_data.py # Deterministic synthetic demo data generator (seed=42)
│   ├── import_data.py        # CLI script to import CSVs into SQLite
│   └── run_analysis.py       # End-to-end analytical pipeline runner
├── tests/
│   ├── test_data_processing.py # Tests CSV validation, date parsing, and alignment
│   ├── test_analysis.py        # Tests descriptive stats and hypothesis calculations
│   ├── test_forecasting.py     # Tests error metrics, SARIMAX, and stress classification
│   └── test_api.py             # Tests FastAPI endpoints and HTTP responses
├── data/
│   ├── raw/                  # Storage for uploaded or real raw CSV files
│   ├── processed/            # Contains harmonized analytical_dataset.csv
│   └── synthetic/            # Contains reproducible synthetic demonstration CSVs
├── outputs/
│   ├── charts/               # Stores 9 generated PNG visualization plots
│   └── reports/              # Stores summary_report.md
├── docs/
│   ├── DATA_SOURCES.md       # Target government portals and schema specifications
│   ├── METHODOLOGY.md        # Mathematical definitions, equations, and viva guide
│   ├── LIMITATIONS.md        # Scientific boundaries and correlation disclosures
│   ├── PROJECT_EXPLANATION_FOR_TEAM.md # THIS COMPREHENSIVE DOCUMENT
│   ├── QUICK_START_FOR_TEAM.md         # Setup and run commands in 3 steps
│   ├── API_REFERENCE_FOR_TEAM.md       # Practical endpoint reference with JSON
│   └── RESEARCH_AND_STATISTICS_GUIDE.md # Statistical formulas & hypothesis testing guide
├── requirements.txt          # Python dependencies
├── Dockerfile                # Production container specification
├── render.yaml               # Render Cloud deployment configuration
└── README.md                 # Public repository documentation
```

### Module Responsibilities & Dependencies
- [app/config.py](file:///d:/python-capstone/app/config.py): Reads `.env` and exports `BASE_DIR`, `DATABASE_URL`, `DATA_DIR`, `OUTPUTS_DIR`, `HOST`, and `PORT`. No internal dependencies.
- [app/database.py](file:///d:/python-capstone/app/database.py): Imports `DATABASE_URL` from `config.py`. Creates `engine`, `SessionLocal`, and `Base`. Exports `get_db()` dependency.
- [app/models.py](file:///d:/python-capstone/app/models.py): Inherits from `database.Base`. Defines `KCCObservation`, `CommodityObservation`, `FuelObservation`, `ImportHistory`, and `ForecastHistory`.
- [app/schemas.py](file:///d:/python-capstone/app/schemas.py): Pure Pydantic v2 classes. Defines request/response models. No database dependencies.
- [app/data_processing.py](file:///d:/python-capstone/app/data_processing.py): Imports `models` and `config`. Handles CSV reading, cleaning, and building `analytical_dataset.csv`.
- [app/analysis.py](file:///d:/python-capstone/app/analysis.py): Imports `build_analytical_dataset` from `data_processing.py`. Runs SciPy hypothesis tests and generates Matplotlib charts into `outputs/charts/`.
- [app/forecasting.py](file:///d:/python-capstone/app/forecasting.py): Imports `build_analytical_dataset` from `data_processing.py`. Fits Statsmodels `SARIMAX`, computes MAE/RMSE/MAPE, and classifies advisory stress.
- [app/api.py](file:///d:/python-capstone/app/api.py): Imports route functions from `data_processing.py`, `analysis.py`, and `forecasting.py`. Delegates all business logic to them.
- [app/main.py](file:///d:/python-capstone/app/main.py): Mounts static charts, enables CORS, registers `api_router`, and creates tables on startup.

---

# Part C: Understanding the Data and Database

## 8. Data Sources and Data Quality

The project targets three distinct Indian open data sources:

1. **Kisan Call Centre (KCC) Query Data:**
   - **Portal:** Open Government Data (OGD) Platform India ([data.gov.in](https://www.data.gov.in/))
   - **Expected Columns:** `observation_date`, `state`, `district`, `query_type`, `query_count`.
   - **Characteristics:** Daily call records; Sundays and national holidays have sharply lower volume due to call centre operating hours.
2. **Agricultural Commodity Prices & Arrivals:**
   - **Portal:** Agricultural Marketing Information Network ([agmarknet.gov.in](https://agmarknet.gov.in/))
   - **Expected Columns:** `observation_date`, `state`, `district`, `market`, `commodity`, `wholesale_price` (INR/Quintal), `retail_price`, `arrival_quantity`.
   - **Characteristics:** Wholesale mandi modal trading prices. APMC Mandis are closed on Sundays and festival holidays.
3. **Retail Diesel Fuel Prices:**
   - **Portal:** Petroleum Planning & Analysis Cell ([ppac.gov.in](https://ppac.gov.in/))
   - **Expected Columns:** `observation_date`, `state`, `diesel_price` (INR/Litre).
   - **Characteristics:** Monitored at state capital and metropolitan hub levels, not individual rural revenue blocks.

### Real Data vs. Synthetic Demonstration Data
> [!NOTE]
> When live multi-gigabyte historical dumps or government API keys are unavailable during offline development, the project runs on **deterministic synthetic data** generated by [scripts/generate_demo_data.py](file:///d:/python-capstone/scripts/generate_demo_data.py).
> - Uses a fixed random seed (`seed = 42`) so every teammate gets identical numbers.
> - Covers 730 days (2 full years: 2024-01-01 to 2025-12-30) across 4 agricultural states (Maharashtra, Punjab, Uttar Pradesh, Madhya Pradesh).
> - Simulates realistic agricultural patterns: monsoon query surge in July-August, Sunday dips, and mandi closures.
> - **All synthetic records are explicitly tagged with `is_synthetic = True`** in the database to prevent presenting simulated results as real government findings.

---

## 9. CSV Ingestion and Cleaning

The cleaning functions in [app/data_processing.py](file:///d:/python-capstone/app/data_processing.py) follow explicit rules:

1. **Header Normalization:** Converts column headers like `"Observation Date "` or `"State-Name"` to lowercase with underscores: `observation_date`, `state_name`.
2. **Required Column Check:** If required columns (e.g., `observation_date` or `state`) are missing, the import halts immediately, logs `FAILED` in `import_history`, and returns a clear error message.
3. **Safe Date Parsing:** Uses `pd.to_datetime(series, errors="coerce", format="mixed").dt.date`. Any unparseable string (e.g., `"not-a-date"` or `"N/A"`) becomes `NaT` and the row is rejected.
4. **Valid Range Filtering:**
   - KCC calls must be $\ge 0$.
   - Commodity wholesale price must be $> 0$.
   - Diesel price must be $> 0$.
5. **Deduplication:** Multiple identical entries for the same date, state, and category/commodity within a single batch are removed using `drop_duplicates(keep="first")`.
6. **Handling Missing Query Days:** If a call centre logs zero inquiries on a holiday, the query count is assigned `0`, **not dropped**. Dropping days would create artificial gaps in a time series.

---

## 10. Database Design & Schema

The database uses SQLite locally (`agristress.db`) and supports PostgreSQL for cloud deployments via SQLAlchemy ORM models in [app/models.py](file:///d:/python-capstone/app/models.py).

```mermaid
erDiagram
    KCC_OBSERVATIONS {
        int id PK
        date observation_date "Indexed"
        string state "Indexed"
        string district
        string query_type
        int query_count
        boolean is_synthetic
        string source_ref
    }

    COMMODITY_OBSERVATIONS {
        int id PK
        date observation_date "Indexed"
        string state "Indexed"
        string district
        string market
        string commodity "Indexed"
        float wholesale_price
        float retail_price
        float arrival_quantity
        string units
        boolean is_synthetic
        string source_ref
    }

    FUEL_OBSERVATIONS {
        int id PK
        date observation_date "Indexed"
        string state "Indexed"
        float diesel_price
        string currency
        boolean is_synthetic
        string source_ref
    }

    IMPORT_HISTORY {
        int id PK
        string dataset_type
        string filename
        datetime import_time
        int total_records
        int accepted_records
        int rejected_records
        int duplicate_records
        string status
        text notes
    }

    FORECAST_HISTORY {
        int id PK
        datetime created_at
        string model_name
        string target_variable
        string state
        date forecast_start_date
        date forecast_end_date
        int horizon_days
        float mae
        float rmse
        float mape
        string stress_category
        text details_json
    }
```

### Table Details
- **`kcc_observations`**: Primary table for farmer call influx. `observation_date` and `state` are indexed for fast group-by operations.
- **`commodity_observations`**: Wholesale and retail prices. `retail_price` is nullable because retail prices are only monitored for 22 commodities in India.
- **`fuel_observations`**: Retail diesel fuel prices in INR/Litre.
- **`import_history`**: Audit trail recording when files were uploaded, how many rows were accepted, and whether any failed.
- **`forecast_history`**: Stores every generated SARIMAX run, horizon, error metrics, and full prediction points in `details_json`.

---

# Part D: Understanding the Analytical and Mathematical Logic

## 11. Data Processing and Feature Engineering

When [build_analytical_dataset](file:///d:/python-capstone/app/data_processing.py#L198-L260) executes, it harmonizes the data into a single continuous daily DataFrame.

### 1. Continuous Daily Calendar Grid
APMC Mandis close on Sundays, but call centres operate daily. If we did a standard inner join, all Sundays would vanish from the time series, breaking the 7-day weekly seasonality required by SARIMAX.  
**Solution:** We reindex the dataset to a continuous date range (`pd.date_range(min_date, max_date, freq='D')`). Missing prices on Sundays are forward-filled (`ffill()`) from Saturday's close, preserving the last known price farmers saw.

### 2. Mathematical Features Engineered

| Feature Name | Formula | Meaning | Small Numerical Example |
| :--- | :--- | :--- | :--- |
| **Price Difference** | $\Delta P_t = P_t - P_{t-1}$ | Absolute change in wholesale price from previous day | Yesterday: ₹2000, Today: ₹1850 $\rightarrow \Delta P = -150$ INR/Qtl |
| **Percentage Return** | $\% \Delta P_t = \left(\frac{P_t - P_{t-1}}{P_{t-1}}\right) \times 100$ | Relative change in wholesale price | $\frac{1850 - 2000}{2000} \times 100 = -7.5\%$ |
| **7-Day Price Volatility** | $\sigma_{7,t} = \sqrt{\frac{1}{6} \sum_{i=0}^6 (P_{t-i} - \bar{P}_7)^2}$ | Standard deviation over a rolling 7-day window | Measures whether prices are stable or oscillating wildly |
| **Price Spread** | $S_t = P_t^{\text{retail}} - P_t^{\text{wholesale}}$ | Margin between consumer price and mandi price | Retail: ₹3000, Wholesale: ₹2000 $\rightarrow S_t = ₹1000$ INR/Qtl |
| **Retail Margin (%)** | $M_t = \left(\frac{P_t^{\text{retail}} - P_t^{\text{wholesale}}}{P_t^{\text{wholesale}}}\right) \times 100$ | Percentage markup in retail market over wholesale | $\frac{3000 - 2000}{2000} \times 100 = 50.0\%$ |
| **Diesel Shock (%)** | $\% \Delta D_t = \left(\frac{D_t - D_{t-1}}{D_{t-1}}\right) \times 100$ | Daily percentage change in diesel fuel price | Diesel rises from ₹90 to ₹92.5 $\rightarrow +2.78\%$ (Shock!) |

---

## 12. Exploratory Data Analysis & Visualizations

The application automatically generates 8 charts in [app/analysis.py](file:///d:/python-capstone/app/analysis.py) and saves them to `outputs/charts/`:

1. **`query_demand_over_time.png`**:
   - *X-axis:* Date (2024 to 2025). *Y-axis:* Daily query volume.
   - *Visuals:* Light blue line (daily calls) + bold red line (14-day rolling moving average).
   - *Interpretation:* Shows the seasonal surge during the monsoon sowing window (June-August).
2. **`seasonality_patterns.png`**:
   - *Visuals:* Bar chart showing average call volume by day of week (Monday through Sunday).
   - *Interpretation:* Highlights the sharp dip on Sundays due to call centre operational schedules.
3. **`commodity_price_trends.png`**:
   - *Visuals:* Green line showing wholesale mandi prices (INR/Quintal) over time.
4. **`diesel_price_trends.png`**:
   - *Visuals:* Pink line showing retail diesel prices (INR/Litre). Highlights step-like price jumps following policy revisions.
5. **`price_spreads.png`**:
   - *Visuals:* Retail price line, wholesale price line, and shaded purple region representing the margin spread ($S_t$).
6. **`query_vs_economic.png`**:
   - *Visuals:* Dual-axis plot with KCC query demand on the left axis (blue) and wholesale commodity price on the right axis (orange).
7. **`regional_queries.png`**:
   - *Visuals:* Bar chart comparing total inquiries across states (Maharashtra, Punjab, Uttar Pradesh, Madhya Pradesh).
8. **`correlation_heatmap.png`**:
   - *Visuals:* Heatmap matrix of Pearson correlation coefficients across calls, wholesale price, retail price, diesel price, and volatility.

---

## 13. Statistical Hypothesis Testing

All tests are implemented in [run_hypothesis_tests](file:///d:/python-capstone/app/analysis.py#L107-L180):

### Hypothesis A: Commodity Price Movements
- **Research Question:** Do changes in agricultural commodity prices correlate with changes in KCC call volume?
- **$H_0$ (Null):** Commodity price percentage change has no linear correlation with query demand ($r = 0$).
- **$H_1$ (Alternative):** A statistically detectable linear correlation exists ($r \neq 0$).
- **Test Used:** Pearson Product-Moment Correlation Test (`scipy.stats.pearsonr`).
- **Threshold:** $\alpha = 0.05$. Reject $H_0$ if $p < 0.05$.
- **Sample Requirement:** At least 15 valid matched observation days.

### Hypothesis B: Diesel Fuel Price Shocks
- **Research Question:** Does farmer advisory demand surge during or immediately following diesel price shocks?
- **Shock Rule:** A day is classified as a shock day if $|\% \Delta D_t| \ge 2.0\%$.
- **$H_0$ (Null):** Call volume distributions on diesel shock days and normal days are identical.
- **$H_1$ (Alternative):** Call volume differs significantly on shock days.
- **Test Used:** Mann-Whitney U Two-Sample Rank-Sum Test (`scipy.stats.mannwhitneyu`). Non-parametric test chosen because call counts are non-normal and contain weekend dips.
- **Sample Requirement:** At least 5 shock days and 15 normal days.

### Hypothesis C: Wholesale-to-Retail Price Spreads
- **Research Question:** Does a widening margin between retail consumer prices and wholesale farm-gate prices associate with higher inquiry volumes?
- **$H_0$ (Null):** Price spread has no monotonic rank correlation with query influx ($\rho_s = 0$).
- **$H_1$ (Alternative):** A monotonic rank correlation exists ($\rho_s \neq 0$).
- **Test Used:** Spearman Rank-Order Correlation Test (`scipy.stats.spearmanr`).
- **Limitation:** Computed only when matched retail prices exist.

---

## 14. Time-Series Forecasting Using SARIMAX

Time-series forecasting is implemented in [app/forecasting.py](file:///d:/python-capstone/app/forecasting.py).

### Why SARIMAX?
KCC inquiries have two dominant properties:
1. **Long-Term Trend:** Overall growth or seasonal drift over months.
2. **Weekly Cyclicality ($s=7$):** Call centres experience heavy volume Monday–Friday, moderate volume Saturday, and low volume Sunday.

Standard regression models treat observations as independent, completely ignoring time order. **SARIMAX** explicitly models past values (Autoregression), trends (Differencing), past shocks (Moving Average), and recurring seasonal cycles.

$$\text{SARIMAX}(p=1, d=1, q=1) \times (P=1, D=1, Q=0)_{s=7}$$
- $p=1$: Uses the call count from yesterday ($t-1$).
- $d=1$: First-order non-seasonal differencing ($Q_t - Q_{t-1}$) to stabilize trend.
- $q=1$: Uses yesterday's forecast error shock.
- $P=1, D=1, s=7$: Compares today's value to the value on the exact same day of the week last week ($t-7$).

### Strict Chronological Validation
> [!WARNING]
> We never use standard random train-test splitting (like Scikit-Learn's `train_test_split(shuffle=True)`). Shuffling time-series data leaks future observations into the training split, resulting in artificially inflated, invalid accuracy.  
> We enforce **chronological splitting**: the first 80% of days are used for training, and the final 20% of days are used for testing.

### Baseline Benchmark
Before claiming SARIMAX is accurate, we compare it against a **7-Day Seasonal Naive Baseline**:
$$\hat{Q}_t^{\text{baseline}} = Q_{t-7}$$
*(Predicting that call volume this Tuesday will equal call volume last Tuesday).*

### Accuracy Metrics
- **Mean Absolute Error (MAE):** Average difference in calls between actual and predicted.
- **Root Mean Squared Error (RMSE):** Penalizes larger forecast misses more heavily.
- **Zero-Safe MAPE:** Avoids division by zero on days with zero recorded calls:
  $$\text{MAPE} = \frac{1}{N} \sum_{t=1}^N \frac{|Q_t - \hat{Q}_t|}{\max(Q_t, 1)} \times 100\%$$

---

## 15. Agricultural Advisory Stress Indicator

Implemented in [classify_advisory_stress](file:///d:/python-capstone/app/forecasting.py#L36-L61), this heuristic translates raw numerical predictions into three operational categories:

```
[ Normal ]   :  Predicted Demand < Baseline Mean + (0.75 * StdDev)
[ Elevated ] :  Baseline Mean + (0.75 * StdDev) <= Predicted Demand < Baseline Mean + (1.75 * StdDev)
[ High ]     :  Predicted Demand >= Baseline Mean + (1.75 * StdDev)
```

- **Uncertainty Notice:** If the point prediction is `Elevated`, but the **95% upper confidence interval** crosses into the `High` threshold, the system appends a warning to advise management of potential upside volatility.
- **Disclaimer:** This is a project-defined planning indicator, not an official government workforce regulation.

---

# Part E: Understanding the Backend and API

## 16. FastAPI and Backend Logic

### What is an API?
*Analogy:* Think of a restaurant. You (the client/frontend) sit at a table and look at a menu. You cannot walk into the kitchen (the database). Instead, you give your order to the **waiter (the API)**. The waiter takes your request to the kitchen, gets the meal, and returns it to your table formatted cleanly on a plate (JSON).

### Complete Endpoint Reference Table

| HTTP Method | Endpoint Path | What It Does | Parameters / Body | Response Summary |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | Verifies database connectivity and server status | None | `{"status": "healthy", "database": "connected"}` |
| `GET` | `/api/v1/datasets/status` | Reports table counts, date ranges, and analytical readiness | None | Counts per table, min/max dates, readiness flag |
| `GET` | `/api/v1/overview` | High-level summary of total queries and states | None | Total queries, commodity/fuel rows, state list |
| `POST` | `/api/v1/data/import/kcc` | Ingests and validates a KCC query CSV file | Multipart File (`.csv`) | Total rows, accepted, rejected, duplicates |
| `POST` | `/api/v1/data/import/commodity` | Ingests wholesale commodity price CSV | Multipart File (`.csv`) | Accepted/rejected row summary |
| `POST` | `/api/v1/data/import/fuel` | Ingests diesel fuel price CSV | Multipart File (`.csv`) | Accepted/rejected row summary |
| `GET` | `/api/v1/analysis/summary` | Descriptive statistics (mean, std, min, median, max) | Optional `state`, `commodity` | Stats per variable + analytical insights |
| `GET` | `/api/v1/analysis/trends` | Daily chronological points for frontend line charts | Optional `state`, `limit` (default 60) | List of `{date, query_count, wholesale_price, diesel_price}` |
| `GET` | `/api/v1/analysis/regions` | Total and daily average queries by state | None | List of state totals and observation days |
| `GET` | `/api/v1/analysis/correlations` | Pairwise Pearson and Spearman correlations | Optional `state`, `commodity` | Correlation coefficients and sample sizes |
| `POST` | `/api/v1/analysis/hypothesis-tests` | Executes formal Hypothesis A, B, and C tests | JSON `HypothesisTestRequest` | Test statistics, p-values, verdicts, limitations |
| `POST` | `/api/v1/forecast` | Runs SARIMAX forecast & advisory stress rating | JSON `ForecastRequest` (`horizon_days: 14`) | Daily predictions, bounds, stress assessment |
| `GET` | `/api/v1/forecast/history` | Lists previous forecast runs from database | `limit: 10` | Previous forecast IDs, dates, metrics, ratings |
| `GET` | `/api/v1/forecast/{id}` | Detailed predictions and intervals for a forecast run | Path `forecast_id` | Full prediction points and evaluation details |
| `POST` | `/api/v1/reports/generate` | Triggers chart and research report generation | None | Report file path, chart paths, generation timestamp |
| `GET` | `/api/v1/reports/latest` | Returns markdown text of the latest summary report | None | Full markdown report content |

---

## 17. Reports, History, and Outputs

All analytical outputs are stored in dedicated folders:
1. **Charts:** Saved to `outputs/charts/` as 120-150 DPI PNG images. Also accessible over the API via the `/static/charts/` route.
2. **Research Summary Report:** Generated at `outputs/reports/summary_report.md`. Contains sample dates, descriptive statistics table, hypothesis test results, and limitations.
3. **Harmonized Dataset:** Saved to `data/processed/analytical_dataset.csv`.
4. **Forecast History:** Every forecast run is recorded in the `forecast_history` SQLite table, storing the horizon, error metrics, and complete predictions in JSON.

---

## 18. Configuration, Environment, and Deployment

### Configuration (`app/config.py`)
- Reads environment variables with fallback defaults:
  - `DATABASE_URL`: Defaults to `sqlite:///./agristress.db`. For PostgreSQL, set to `postgresql://user:password@host:5432/dbname`.
  - `DATA_DIR`: Defaults to `data/`.
  - `OUTPUTS_DIR`: Defaults to `outputs/`.
  - `HOST`: Defaults to `0.0.0.0`.
  - `PORT`: Defaults to `8000`.

### Containerization (`Dockerfile`)
- Builds on `python:3.10-slim`.
- Installs `build-essential`, copies source code, runs `scripts/init_db.py`, generates demo data, and imports it.
- Exposes port 8000 and launches Uvicorn.

### Render Cloud Blueprint (`render.yaml`)
- Configured as a Python web service.
- Build command: `pip install -r requirements.txt && python scripts/init_db.py && python scripts/generate_demo_data.py && python scripts/import_data.py --all`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

---

# Part F: How Teammates Can Use and Maintain the Project

## 19. Complete Setup Guide from Scratch

### For Windows:
```powershell
# 1. Clone repository and enter directory
git clone https://github.com/rehaan-patil/agristress-analytics.git
cd agristress-analytics

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Copy environment configuration
copy .env.example .env

# 5. Initialize SQLite database tables
python scripts/init_db.py
```

### For Linux / macOS:
```bash
# 1. Clone repository and enter directory
git clone https://github.com/rehaan-patil/agristress-analytics.git
cd agristress-analytics

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Copy environment configuration
cp .env.example .env

# 5. Initialize SQLite database tables
python3 scripts/init_db.py
```

---

## 20. Complete Demonstration Walkthrough

Follow these 4 commands to demonstrate the entire project:

```bash
# Step 1: Generate reproducible demo data (730 days, seed=42)
python scripts/generate_demo_data.py

# Step 2: Import demo data into SQLite database
python scripts/import_data.py --all

# Step 3: Run the complete analytical pipeline
python scripts/run_analysis.py
```

```bash
# Step 4: Start the FastAPI REST server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Open browser to: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
- Click `GET /health` $\rightarrow$ Click **"Try it out"** $\rightarrow$ Click **"Execute"**.
- Click `POST /api/v1/forecast` $\rightarrow$ Click **"Try it out"** $\rightarrow$ Click **"Execute"** with default 14-day horizon.

---

## 21. Testing and Debugging

Run the entire automated test suite:
```bash
python -m pytest -v
```

### What the 26 Tests Cover
- `tests/test_data_processing.py`: Column validation, whitespace cleaning, date parsing, duplicate dropping, and temporal alignment.
- `tests/test_analysis.py`: Descriptive summaries, perfect correlation verification on known data, diesel shock detection, sample insufficiency handling.
- `tests/test_forecasting.py`: MAE/RMSE formulas, advisory stress cutoffs, SARIMAX fitting, and out-of-sample prediction intervals.
- `tests/test_api.py`: Root, health, datasets status, overview, trends, hypothesis testing, forecast history, and invalid file upload rejection.

### Common Errors & Solutions
1. **`Address already in use` (Port 8000 occupied):**  
   Run on a different port: `python -m uvicorn app.main:app --port 8080`
2. **`Insufficient data to forecast`:**  
   The database has fewer than 30 observations. Run `python scripts/generate_demo_data.py` and `python scripts/import_data.py --all`.
3. **`Missing required columns` during CSV upload:**  
   Ensure your KCC CSV contains at least `observation_date` and `state`.

---

## 22. How to Modify the Code Safely

### Example 1: Changing the Diesel Shock Threshold
- **File:** [app/analysis.py](file:///d:/python-capstone/app/analysis.py#L131) and [app/schemas.py](file:///d:/python-capstone/app/schemas.py#L82)
- **Change:** Change `diesel_shock_threshold_pct: float = 2.0` to `1.5` or `3.0`.

### Example 2: Adjusting Advisory-Stress Categories
- **File:** [app/forecasting.py](file:///d:/python-capstone/app/forecasting.py#L36-L40)
- **Change:** Modify the standard deviation cutoffs:
  ```python
  elevated_cutoff = hist_mean + (1.0 * hist_std)  # was 0.75
  high_cutoff = hist_mean + (2.0 * hist_std)      # was 1.75
  ```

### Example 3: Adding a New CSV Column
- **Files to update:**
  1. [app/models.py](file:///d:/python-capstone/app/models.py): Add the new `Column(...)`.
  2. [app/data_processing.py](file:///d:/python-capstone/app/data_processing.py): Read the column from the CSV in the import function.
  3. Run `python scripts/init_db.py` to recreate tables.

---

## 23. Current Limitations and Next Steps

### Current Limitations
1. **Observational Data:** Statistical correlations do not prove economic causation.
2. **Spatial Granularity:** Diesel prices are state-level; mandi prices are market-level.
3. **Synthetic Demonstration Data:** Current demonstration outputs use simulated data until live government API tokens are integrated.
4. **Answered vs. Attempted Calls:** KCC logs reflect answered inquiries, not dropped calls during peak congestion.

### Recommended Next Steps for Team
1. **Frontend Development:** Build a clean dashboard (React, Vue, or Vanilla JS) calling our 16 REST endpoints.
2. **Live Data Connectors:** Build an automated periodic fetcher for OGD India (`data.gov.in`) APIs.
3. **PostgreSQL Cloud Integration:** Set up a hosted PostgreSQL database on Render or Supabase and update `DATABASE_URL` in `.env`.

---

## 24. Glossary and Teammate Knowledge Checklist

### Plain English Glossary
- **APMC Mandi:** Government-regulated wholesale agricultural market yard in India.
- **Kisan Call Centre (KCC):** Toll-free telephone advisory service operated by the Ministry of Agriculture.
- **Modal Price:** The most frequently occurring transaction price for a crop on a trading day.
- **SARIMAX:** Seasonal Autoregressive Integrated Moving Average with Exogenous regressors.
- **P-Value:** The probability of observing our test results if there was actually zero true association ($H_0$). If $p < 0.05$, we reject the null hypothesis.
- **MAE (Mean Absolute Error):** Average size of forecast mistakes in raw call counts.
- **RMSE (Root Mean Squared Error):** Forecast error metric that penalizes large blunders more severely.

### Teammate Viva Self-Test Questions
Can you answer these four questions without looking at the notes?
1. *Why do we use chronological train-test splitting instead of random splitting?*  
   *(Answer: To prevent lookahead bias where future data leaks into the past in a time series).*
2. *Why is SARIMAX seasonal order set to $s=7$?*  
   *(Answer: Because KCC call volume follows a strong 7-day weekly cycle with sharp Sunday dips).*
3. *What does the advisory-stress indicator measure?*  
   *(Answer: Expected operational pressure on call centre infrastructure, comparing forecast demand against historical mean and standard deviation).*
4. *Does a statistically significant correlation between commodity price crashes and KCC inquiries prove causation?*  
   *(Answer: No. Confounding variables like monsoon weather affect both harvest prices and farmer inquiry calls simultaneously).*

---

### Supporting Documentation Quick Links
- [docs/QUICK_START_FOR_TEAM.md](file:///d:/python-capstone/docs/QUICK_START_FOR_TEAM.md) — Fast setup & demo steps.
- [docs/API_REFERENCE_FOR_TEAM.md](file:///d:/python-capstone/docs/API_REFERENCE_FOR_TEAM.md) — Endpoint reference with example JSON payloads.
- [docs/RESEARCH_AND_STATISTICS_GUIDE.md](file:///d:/python-capstone/docs/RESEARCH_AND_STATISTICS_GUIDE.md) — Formulas, hypothesis tests, and SARIMAX deep dive.
