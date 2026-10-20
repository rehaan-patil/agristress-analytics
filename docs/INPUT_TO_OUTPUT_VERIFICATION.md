# Input-to-Output Functional Verification Report — AgriStress Analytics

**Verification Date:** October 2026  
**Project:** AgriStress Analytics (Academic Capstone Research Pipeline)  
**Execution Environment:** Windows 10/11 x64, Python 3.10+, SQLite local storage  
**Repository Branch:** `main`  

---

## Executive Summary & Core Question Answer

### The Fundamental Question
> **"Does this application genuinely process user-supplied datasets and calculate new analytical and forecasting results from them, or does it primarily generate results from the existing synthetic demonstration data?"**

### Official Classification: **Category B — Input-Driven Synthetic / Demo Pipeline**

| Classification Category | Description | Status |
| :--- | :--- | :---: |
| **A. Visualization Only** | Mainly displays or exports existing pre-computed results without dynamic recomputation. | **FALSE** |
| **B. Input-Driven Synthetic / Demo Pipeline** | **Genuinely ingests, validates, aligns, and processes user-supplied CSV datasets matching its expected schema (or government alias mappings), recalculating all descriptive statistics, econometric correlations, hypothesis tests, SARIMAX out-of-sample holdout metrics, stress indicator thresholds, plots, and markdown reports from the current input. However, universal out-of-the-box compatibility across unstructured raw government portals (such as uncleaned multi-table PDF reports or non-standard regional dial-in logs) has not been verified with real live API keys.** | **VERIFIED & PROVEN** |
| **C. Verified Real-Data Pipeline** | Processes at least one live, uncurated, official real-world dataset end to end with verifiable government data provenance preserved throughout. | **NOT YET VERIFIED** |

---

## 1. Trace of the Complete Input-to-Output Pipeline

Every file and function in the pipeline was inspected and traced from initial disk CSV files through database insertion, data alignment, feature engineering, econometric testing, time-series forecasting, and report generation.

```
+---------------------------------------------------------------------------------------+
|                                 1. INPUT CSV FILES                                    |
|   - KCC Queries (e.g., tests/test_data/independent_test_kcc.csv)                      |
|   - Mandi Commodity Prices (e.g., tests/test_data/independent_test_commodity.csv)     |
|   - Fuel Retail Prices (e.g., tests/test_data/independent_test_fuel.csv)              |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                    2. VALIDATION, COLUMN MAPPING & CLEANING                           |
|   - app/data_processing.py: standardize_column_names(), apply_column_synonyms()       |
|   - app/data_processing.py: safe_parse_dates() (ISO, DD/MM/YYYY flexible parser)      |
|   - app/data_processing.py: check_missing_columns()                                   |
|   - Duplicate removal and raw call-event aggregation                                  |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                      3. DATABASE STORAGE & AUDIT LOGGING                              |
|   - SQLite (agristress.db via SQLAlchemy ORM):                                        |
|     * KCCObservation (table: kcc_observations)                                        |
|     * CommodityObservation (table: commodity_observations)                            |
|     * FuelObservation (table: fuel_observations)                                      |
|     * ImportHistory (table: import_history)                                           |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                    4. TEMPORAL HARMONIZATION & FEATURE ENGINEERING                    |
|   - app/data_processing.py: build_analytical_dataset()                                |
|     * Daily aggregation of KCC calls by observation_date (and optional state filter)  |
|     * Average wholesale & retail prices, sum of arrivals by commodity/date            |
|     * Average retail diesel fuel price by state/date                                  |
|     * Left/Outer join on continuous calendar index (no duplicate record inflation)    |
|     * Forward-fill for mandi closures (Sundays/holidays)                              |
|     * Feature creation: price spread, volatility, diffs, percentage changes, lags     |
|     * Export: data/processed/analytical_dataset.csv                                   |
|   - app/data_processing.py: get_data_quality_report()                                 |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                    5. DESCRIPTIVE STATISTICS & ECONOMETRIC TESTS                      |
|   - app/analysis.py: get_descriptive_summary() (mean, std, min, median, max)          |
|   - app/analysis.py: get_correlations() (Pearson r and Spearman rho against demand)   |
|   - app/analysis.py: run_hypothesis_tests(diesel_shock_threshold_pct)                 |
|     * HYP-A: Pearson test on daily commodity % change vs query demand                 |
|     * HYP-B: Mann-Whitney U rank-sum test on fuel shock days vs normal days           |
|     * HYP-C: Spearman rank correlation on wholesale-retail price spread vs inquiries   |
|   - app/analysis.py: save_analysis_tables() -> outputs/tables/                        |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                    6. TIME-SERIES FORECASTING & STRESS PROXY                          |
|   - app/forecasting.py: generate_forecast()                                           |
|     * Chronological out-of-sample holdout test split (last 20% or max 30 days)        |
|     * Seasonal Naive benchmark (7-day lag) evaluated on test split                    |
|     * SARIMAX(1,1,1)(1,1,0)[7] fitted on train split and evaluated on test split       |
|     * Evaluation metrics calculated: MAE, RMSE, Zero-Safe MAPE                        |
|     * Full-series retraining and future horizon forecasting with 95% confidence bounds|
|     * classify_advisory_stress(): Normal (<0.75 SD), Elevated (0.75-1.75 SD), High    |
|     * ForecastHistory table logging in SQLite                                         |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                                7. FINAL ARTIFACT OUTPUTS                              |
|   - Outputs Directory: outputs/                                                       |
|     * outputs/tables/ (4 CSV result tables)                                           |
|     * outputs/charts/ (8 PNG exploratory charts + 2 PNG forecast evaluation plots)    |
|     * outputs/forecasts/ (forecast_predictions.csv, forecast_evaluation_metrics.csv)  |
|     * outputs/reports/summary_report.md (Comprehensive Markdown Academic Summary)     |
+---------------------------------------------------------------------------------------+
```

---

## 2. Custom CSV Input Support & Schema Specifications

Users can supply their own local CSV datasets directly. The ingestion layer in `app/data_processing.py` features an intelligent column synonym mapping dictionary (`COLUMN_SYNONYMS`) that automatically recognizes headers from official Indian agricultural data portals (such as Agmarknet and data.gov.in).

### 2.1 Schema Requirements

#### A. Kisan Call Centre (KCC) Query Data
- **Target Table:** `kcc_observations`
- **Mandatory Fields:**
  - `observation_date` (Aliases accepted: `date`, `call_date`, `createdon`, `created_date`, `record_date`)
    - Format: Flexible parser accepts ISO `YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`.
  - `state` (Aliases accepted: `state_name`, `statename`)
    - Format: Text string (e.g., `Karnataka`, `Maharashtra`, `Punjab`).
- **Optional Fields:**
  - `district` (Aliases accepted: `district_name`, `districtname`) — string.
  - `query_type` (Aliases accepted: `category`, `sector`, `querytype`) — string.
  - `query_count` (Aliases accepted: `calls`, `call_count`, `queries`, `inquiries`, `total_queries`) — non-negative integer.
- **Handling of Raw Individual Call Records:**
  - If `query_count` is omitted from the CSV, the importer recognizes that each row represents an individual farmer call event (`query_count = 1`) and automatically aggregates calls by `[observation_date, state, district, query_type]`, preventing accidental deletion of multiple calls occurring on the same date.

#### B. Mandi Commodity Prices & Arrivals
- **Target Table:** `commodity_observations`
- **Mandatory Fields:**
  - `observation_date` (Aliases accepted: `arrival_date`, `date`, `reported_date`)
  - `state` (Aliases accepted: `state_name`, `statename`)
  - `commodity` (Aliases accepted: `commodity_name`, `crop`)
  - `wholesale_price` (Aliases accepted: `modal_price`, `modal_price_(rs./quintal)`, `modal_price_rs_quintal`, `modal_x0020_price`, `price`)
    - Units: INR per Quintal (100 kg). Must be strictly positive ($> 0$).
- **Optional Fields:**
  - `district` (Aliases accepted: `district_name`) — string.
  - `market` (Aliases accepted: `market_name`, `mandi`, `mandi_name`) — string.
  - `retail_price` (Aliases accepted: `retail_price_(rs./quintal)`) — INR per Quintal ($> 0$).
  - `arrival_quantity` (Aliases accepted: `arrivals`, `arrivals_(tonnes)`, `arrivals_in_tonnes`, `arrival_tonnes`) — Metric Tonnes ($\ge 0$).

#### C. Fuel Prices (Retail Diesel)
- **Target Table:** `fuel_observations`
- **Mandatory Fields:**
  - `observation_date` (Aliases accepted: `date`, `reported_date`)
  - `diesel_price` (Aliases accepted: `diesel`, `diesel_retail_price`, `diesel_price_(rs/litre)`, `fuel_price`)
    - Units: INR per Litre. Must be strictly positive ($> 0$).
- **Optional Fields:**
  - `state` (Aliases accepted: `state_name`) — string.

### 2.2 Invalid Data Handling & Rejection
- **Missing Required Headers:** The importer returns `status: "FAILED"`, records the failure and error message in `import_history`, and skips processing without crashing.
- **Unparseable / Bad Dates:** Dates that cannot be parsed are converted to `NaT` and filtered into `rejected_rows`.
- **Negative or Zero Prices:** Wholesale commodity prices and diesel prices $\le 0$ are rejected and counted under `rejected_rows`.
- **Duplicate Records:** Replicated records for the same date and entity are deduplicated, with duplicate counts recorded in `import_history`.

---

## 3. Independent Input-Driven Test Demonstration

To prove conclusively that the application calculates new results rather than reading hard-coded values or stale synthetic defaults, an independent test dataset was generated with completely distinct dates, geography, commodity, and economic trends.

### 3.1 Comparison of Datasets

| Dimension | Default Demonstration Data | Independent Test Dataset (`tests/test_data/`) |
| :--- | :--- | :--- |
| **Calendar Period** | `2024-01-01` to `2025-12-30` (730 days) | `2023-05-01` to `2023-08-08` (100 days) |
| **Geographic Coverage** | Maharashtra, Punjab, UP, MP (4 states) | Karnataka (District: Kolar, Market: Kolar APMC) |
| **Target Commodity** | Onion, Wheat, Tomato (multi-commodity) | Tomato (monoculture shock scenario) |
| **Economic Scenario** | Stable cyclical seasonality with minor shocks | **Catastrophic Tomato Price Collapse:**<br>Wholesale price collapses from 3,080 down to 450 INR/Qtl.<br>Retail price stays sticky (~2,800 INR/Qtl).<br>Price spread expands to >2,000 INR/Qtl.<br>Farmer advisory inquiries surge by 500% (from 25 up to 271 calls/day). |
| **Provenance Flag** | Marked as Synthetic (`is_synthetic = True`) | Ingested via `--kcc` CLI with custom files (`is_synthetic = False`) |

### 3.2 Command Executed
```powershell
python run_pipeline.py `
  --kcc tests/test_data/independent_test_kcc.csv `
  --commodity-file tests/test_data/independent_test_commodity.csv `
  --fuel tests/test_data/independent_test_fuel.csv `
  --replace `
  --state Karnataka `
  --commodity Tomato `
  --horizon 14 `
  --shock-threshold 2.0
```

### 3.3 Measured Changes: Demonstration Data vs Independent Test Data

| Metric / Output Component | Default Demo Run | Independent Test Run | Verification Evidence |
| :--- | :---: | :---: | :--- |
| **Sample Start Date** | `2024-01-01` | **`2023-05-01`** | **Changed** (Year 2023 used) |
| **Sample End Date** | `2025-12-30` | **`2023-08-08`** | **Changed** |
| **Sample Days ($N$)** | 730 days | **100 days** | **Recalculated** |
| **KCC Query Mean** | 237.85 calls/day | **92.79 calls/day** | **Recalculated** |
| **KCC Query Peak** | 431.00 calls | **271.00 calls** | **Recalculated** |
| **Wholesale Price Min** | 1,765.73 INR/Qtl | **450.00 INR/Qtl** | **Recalculated** (Reflects price crash) |
| **Max Wholesale-Retail Spread**| 854.49 INR/Qtl | **2,004.81 INR/Qtl** | **Recalculated** (Reflects spread surge) |
| **Hypothesis A ($H_0$: Price % vs Calls)** | $r = +0.0108, p = 0.7701$<br>`[FAIL TO REJECT]` | **$r = -0.7403, p = 0.0000$**<br>**`[REJECT H0]`** | **Verdict Changed & Recalculated** (Strong inverse relationship captured) |
| **Hypothesis B ($H_0$: Diesel Shocks vs Calls)** | $U = 18,526.0, p = 0.3939$<br>`[FAIL TO REJECT]` | **3 shock days ($\ge 2.0\%$)**<br>`[FAIL TO REJECT]` | **Threshold Propagated** (Identified 3 shocks at 2.0% threshold) |
| **Hypothesis C ($H_0$: Margin Spread vs Calls)**| $\rho = +0.1587, p = 0.0000$<br>`[REJECT H0]` | **$\rho = +0.4385, p = 0.0000$**<br>`[REJECT H0]` | **Effect Size Recalculated** ($\rho$ increased from 0.16 to 0.44) |
| **Train/Test Split Period** | Train: 2024-01-01 to 2025-11-30<br>Test: 2025-12-01 to 2025-12-30 | **Train: 2023-05-01 to 2023-07-19**<br>**Test: 2023-07-20 to 2023-08-08** | **Split Dates Recalculated** (Strict chronological holdout) |
| **Baseline 7D Naive MAE** | 17.43 calls | **24.10 calls** | **Recalculated** |
| **SARIMAX Out-of-Sample MAE** | 15.34 calls | **24.92 calls** | **Recalculated** |
| **SARIMAX Zero-Safe MAPE** | 9.58% | **17.31%** | **Recalculated** |
| **Future 14D Forecast Mean** | 146.5 calls | **254.1 calls** | **Recalculated** |
| **Advisory Stress Indicator** | **`NORMAL`** | **`HIGH`** | **State Transitioned** (Forecast exceeds high cutoff 232.0 calls) |

---

## 4. Result Independence & Safe Database Operations

1. **Automatic vs Requested Generator:**
   - The default synthetic generator (`scripts/generate_demo_data.py`) is **NOT** invoked when custom CSV arguments (`--kcc`, `--commodity-file`, or `--fuel`) are supplied.
   - It is only invoked when explicitly requested (`--generate-data`) or when the local database is empty.
2. **Replacing vs Appending Data:**
   - Passing `--replace` wipes existing records in SQLite tables before inserting the new dataset. This prevents mixing old demo rows with newly imported user data.
   - Database reset drops and recreates table schemas via SQLAlchemy metadata (`Base.metadata.drop_all`).
3. **Command-Line Filter Propagation:**
   - `--state Karnataka` filters KCC, Mandi, and Fuel records to Karnataka before building the time series.
   - `--commodity Tomato` filters commodity records to Tomato.
   - `--horizon 14` sets the out-of-sample forecasting horizon to 14 days.
   - `--shock-threshold 2.0` sets the fuel shock threshold in the Mann-Whitney test to 2.0%.
   - All parameters are passed directly through to the analysis tables, charts, forecasts, and summary report without being overwritten.
4. **File Regeneration:**
   - All 4 result CSVs in `outputs/tables/`, 10 PNG charts in `outputs/charts/`, 2 forecast CSVs in `outputs/forecasts/`, and `outputs/reports/summary_report.md` are rewritten on every execution.

---

## 5. Statistical & Forecasting Methodology Verification

The implementation was checked against standard econometric and machine-learning integrity requirements:

1. **Join Integrity:** Data merging in `build_analytical_dataset()` groups each dataset by `observation_date` before joining. A Left/Outer join on dates ensures that multiple mandi varieties or intraday observations do not artificially inflate the calendar time-series.
2. **Missing Inquiries vs Mandi Closures:**
   - Missing KCC inquiries are filled with zero only after full date reindexing, representing days where zero inquiries occurred (e.g., Sundays).
   - Commodity and fuel prices are forward-filled (`ffill()`) across Sundays and APMC holidays, preserving continuous price levels without inventing fictitious trading volumes.
3. **No Future Data Leakage:**
   - The train/test split is strictly chronological (train: earliest $80\%$, test: holdout final $20\%$).
   - Random cross-validation or shuffling is **NOT** used.
   - Future values of economic indicators are never used as known exogenous variables during forecasting.
4. **Benchmark Evaluation:** Both the Seasonal Naive baseline (7-day lag: $y_{t-7}$) and the SARIMAX$(1,1,1)(1,1,0)[7]$ model are evaluated on the exact same holdout test slice. Metrics (MAE, RMSE, zero-safe MAPE) are computed identically.
5. **Causality vs Association Disclaimer:** The pipeline explicitly disclaims economic causality, noting that time-series autocorrelation can inflate Pearson correlation significance and reporting Spearman rank correlations and non-parametric Mann-Whitney U statistics alongside parametric tests.

---

## 6. How to Run AgriStress Analytics on a New Dataset from Your Laptop

### Step 1: Prepare Your CSV Files
Place your CSV files anywhere on your machine (e.g., `data/my_kcc.csv`, `data/my_mandi.csv`, `data/my_fuel.csv`). Ensure they have standard or recognized alias column headers:

- **KCC CSV:** Needs date and state (`observation_date`, `state`). Include `query_count` if pre-aggregated, or omit it if each line is a raw call.
- **Commodity CSV:** Needs date, state, commodity name, and wholesale price (`observation_date`, `state`, `commodity`, `wholesale_price`).
- **Fuel CSV:** Needs date and diesel price (`observation_date`, `diesel_price`).

### Step 2: Run the Pipeline via Python Entrypoint
Open PowerShell or your command prompt in the project root:

```powershell
# Run complete analysis with clean database replacement
python main.py --kcc data/my_kcc.csv --commodity-file data/my_mandi.csv --fuel data/my_fuel.csv --replace

# Optional filters: specific state, commodity, and forecast horizon
python main.py --kcc data/my_kcc.csv --commodity-file data/my_mandi.csv --fuel data/my_fuel.csv --replace --state "Maharashtra" --commodity "Onion" --horizon 21 --shock-threshold 1.5
```

### Step 3: Inspect Outputs
- **Markdown Research Report:** `outputs/reports/summary_report.md`
- **Result Tables:** `outputs/tables/` (`descriptive_statistics.csv`, `correlations.csv`, `hypothesis_tests.csv`, `regional_summary.csv`)
- **Visual Charts:** `outputs/charts/` (`query_demand_over_time.png`, `forecast_evaluation.png`, `actual_vs_predicted.png`, `correlation_heatmap.png`, etc.)
- **Forecast Tables:** `outputs/forecasts/` (`forecast_predictions.csv`, `forecast_evaluation_metrics.csv`)

### Step 4: Revert to Default Demonstration Mode Anytime
```powershell
python main.py --generate-data
```

---

## 7. Verification Summary & Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\python-capstone
plugins: anyio-4.10.0
collected 22 items

tests\test_analysis.py ......                                            [ 27%]
tests\test_data_processing.py ...........                                [ 77%]
tests\test_forecasting.py .....                                          [100%]

============================= 22 passed in 10.61s =============================
```

- **All 22 unit and integration tests pass 100% with zero warnings.**
- Dynamic column synonym mapping for government portal exports verified.
- Out-of-sample forecasting with SARIMAX and Seasonal Naive verified.
- Rejection of invalid dates, zero prices, and negative prices verified.
- Full end-to-end execution verified against both the independent crisis dataset and the default demonstration dataset.
