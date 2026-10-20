# AgriStress Analytics — Comprehensive Research Summary Report

**Date Generated:** 2026-10-20 10:43:10 UTC  
**Research Topic:** Econometric and Spatial-Temporal Analysis of Farmer Information Demand: Modeling Kisan Call Centre (KCC) Query Influx Against Commodity Price Spreads and Fuel Inflation Shocks to Forecast Agricultural Advisory Stress  
**Data Provenance:** SYNTHETIC DEMONSTRATION DATASET (Offline Development & Testing)  

---

## 1. Executive Summary & Problem Formulation

Agricultural advisory infrastructure, such as India's Kisan Call Centre (KCC) toll-free network, experiences sudden surges in farmer inquiries during periods of market stress. When commodity mandi prices crash, input diesel prices rise sharply, or the margin spread between farmgate wholesale and consumer retail prices expands, farmers face compressed operating margins and seek information regarding market alternatives, storage viability, and government price support.

This project models daily farmer information demand against key economic and input indicators to:
1. Quantify linear and rank associations between commodity price changes, fuel shocks, wholesale-retail spreads, and KCC call volumes.
2. Formally test three economic hypotheses using SciPy and Statsmodels.
3. Provide out-of-sample time-series demand forecasting using Seasonal Naive baseline and SARIMAX(1,1,1)(1,1,0)[7].
4. Construct a transparent, project-defined **Agricultural Advisory Stress Indicator** to classify expected call centre operational load.

---

## 2. Dataset Coverage, Provenance & Quality

- **Sample Date Range:** 2024-01-01 to 2025-12-30
- **Total Calendar Days:** 730
- **Observed Query Days:** 730
- **Unrecorded / Zero Query Days:** 0 (0.0%)
- **Data Quality Assessment:** GOOD

**Quality & Missingness Handling Notes:**
- PROVENANCE: Data contains synthetic demonstration observations generated deterministically.
- Mandi holiday / Sunday closures are forward-filled for price continuous continuity.

---

## 3. Descriptive Statistics

| Variable | Count | Mean | Std Dev | Min | Median | Max | Units |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `query_count` | 730 | 237.85 | 93.54 | 42.00 | 235.50 | 431.00 | Calls / Day |
| `wholesale_price` | 730 | 2133.81 | 152.07 | 1765.73 | 2132.48 | 2434.80 | INR / Quintal |
| `retail_price` | 730 | 2807.40 | 205.78 | 2336.26 | 2787.71 | 3253.71 | INR / Quintal |
| `diesel_price` | 730 | 102.53 | 5.29 | 90.50 | 104.50 | 110.50 | INR / Litre |
| `price_spread` | 730 | 673.59 | 66.12 | 509.11 | 667.34 | 854.49 | INR / Quintal |
| `commodity_volatility_7d` | 729 | 20.17 | 8.32 | 3.83 | 18.72 | 57.65 | INR (7D Std) |

---

## 4. Econometric Correlation Analysis

| Variable Pair | Pearson $r$ | Spearman $\rho$ | Sample Size ($N$) | Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| KCC Demand vs Wholesale Commodity Price | 0.2307 | 0.2115 | 730 | Weak correlation |
| KCC Demand vs Commodity Price Daily Change | 0.0108 | 0.0273 | 729 | Weak correlation |
| KCC Demand vs 7-Day Commodity Price Volatility | -0.0395 | -0.0330 | 729 | Weak correlation |
| KCC Demand vs Wholesale-Retail Price Spread | 0.1593 | 0.1587 | 730 | Weak correlation |
| KCC Demand vs Diesel Price Level | 0.3096 | 0.3011 | 730 | Weak correlation |
| KCC Demand vs Diesel Daily Price Change | 0.0585 | 0.0556 | 729 | Weak correlation |
| KCC Demand vs 7-Day Lagged Diesel Price Change | 0.0565 | 0.0584 | 722 | Weak correlation |

---

## 5. Formal Hypothesis Testing Results

### ⚪ HYP-A: Commodity Price Movements vs Query Demand
- **Research Question:** Do day-to-day percentage changes in wholesale commodity prices linearly correlate with KCC advisory query volume?
- **Null Hypothesis ($H_0$):** Daily commodity percentage changes have no linear correlation with farmer query volume (r = 0).
- **Alternative Hypothesis ($H_1$):** Daily commodity percentage changes are linearly correlated with farmer query volume (r != 0).
- **Statistical Test Used:** Pearson Linear Correlation Test ($N = 729$)
- **Test Statistic:** `0.0108` | **p-value:** `0.77005` | **Significance Level ($\\alpha$):** 0.05
- **Outcome:** **FAIL TO REJECT NULL HYPOTHESIS**
- **Plain English Verdict:** Fail to reject null hypothesis (r=0.0108, p=0.7701)
- **Statistical Assumptions:** Assumes linear relationship and bivariate normality. Time-series autocorrelation can artificially narrow standard errors.
- **Research Limitations:** Linear correlation does not imply causality; price shocks may have delayed non-linear effects not captured by contemporaneous Pearson r.

### ⚪ HYP-B: Diesel Price Shocks vs Advisory Influx
- **Research Question:** Do days experiencing sudden retail diesel price revisions trigger significantly different farmer call volumes than normal days?
- **Null Hypothesis ($H_0$):** KCC query distribution on fuel shock days is identical to non-shock days.
- **Alternative Hypothesis ($H_1$):** KCC query distribution differs significantly on fuel shock days.
- **Statistical Test Used:** Mann-Whitney U Non-Parametric Rank Sum Test ($N = 729$)
- **Test Statistic:** `18526.0` | **p-value:** `0.3939` | **Significance Level ($\\alpha$):** 0.05
- **Outcome:** **FAIL TO REJECT NULL HYPOTHESIS**
- **Plain English Verdict:** Fail to reject null hypothesis (U=18526.0, p=0.3939)
- **Statistical Assumptions:** Does not assume normal distribution. Assumes independence of observations between groups.
- **Research Limitations:** Shock defined as |daily diesel change| >= 1.0%. Identified 51 shock days vs 678 baseline days.

### 🔴 HYP-C: Wholesale-to-Retail Price Spreads vs Query Influx
- **Research Question:** Is the spread between wholesale mandi price and retail consumer price monotonically associated with farmer query demand?
- **Null Hypothesis ($H_0$):** There is no monotonic rank association between price spread and KCC query demand (rho = 0).
- **Alternative Hypothesis ($H_1$):** Price spread and KCC query demand are monotonically associated (rho != 0).
- **Statistical Test Used:** Spearman Rank-Order Correlation Test ($N = 730$)
- **Test Statistic:** `0.1587` | **p-value:** `2e-05` | **Significance Level ($\\alpha$):** 0.05
- **Outcome:** **REJECT NULL HYPOTHESIS**
- **Plain English Verdict:** Reject null hypothesis (rho=0.1587, p=0.0000)
- **Statistical Assumptions:** Monotonic relationship; does not assume linear bivariate normality.
- **Research Limitations:** Wholesale-retail spread is observable only where matching commodity retail observations exist.

---

## 6. Time-Series Forecasting & Model Validation

- **Model Selected:** `SARIMAX(1,1,1)(1,1,0)[7]`
- **Evaluation Methodology:** Chronological Train/Test Holdout Split (avoiding future data leakage)
- **Train Period:** 2024-01-01 to 2025-11-30
- **Test Period:** 2025-12-01 to 2025-12-30
- **Forecast Horizon:** 14 Days

### Out-of-Sample Holdout Performance Comparison

| Forecasting Model | MAE (Calls) | RMSE (Calls) | Zero-Safe MAPE (%) | Status |
| :--- | :---: | :---: | :---: | :--- |
| Seasonal Naive Baseline (7-Day Lag) | 17.43 | 20.67 | 11.64% | Benchmark |
| SARIMAX(1,1,1)(1,1,0)[7] | 15.34 | 18.96 | 9.58% | **Selected Model** |

---

## 7. Agricultural Advisory Stress Indicator

- **Operational Stress Category:** `NORMAL`
- **Historical Baseline Mean:** 237.8 inquiries/day
- **Elevated Stress Threshold:** >= 308.0 inquiries/day (Historical Mean + 0.75 * Std Dev)
- **High Advisory Stress Threshold:** >= 401.6 inquiries/day (Historical Mean + 1.75 * Std Dev)
- **Interpretation:** Forecast (146.5) is within normal parameters (baseline mean: 237.9).
- **Important Operational Disclaimer:** *Project-defined advisory stress indicator for operational research.*

---

## 8. Artifacts Generated

### Charts (`outputs/charts/`):
- `outputs/charts/query_demand_over_time.png`
- `outputs/charts/seasonality_patterns.png`
- `outputs/charts/commodity_price_trends.png`
- `outputs/charts/diesel_price_trends.png`
- `outputs/charts/price_spreads.png`
- `outputs/charts/query_vs_economic.png`
- `outputs/charts/correlation_heatmap.png`
- `outputs/charts/regional_queries.png`
- `outputs/charts/forecast_evaluation.png` (2-Panel Out-of-Sample Holdout Validation & Future Horizon Forecast)
- `outputs/charts/actual_vs_predicted.png` (Detailed Out-of-Sample Test Comparison)

### Tables (`outputs/tables/`):
- `D:\python-capstone\outputs\tables\descriptive_statistics.csv`
- `D:\python-capstone\outputs\tables\correlations.csv`
- `D:\python-capstone\outputs\tables\hypothesis_tests.csv`
- `D:\python-capstone\outputs\tables\regional_summary.csv`
- `outputs/forecasts/forecast_predictions.csv`
- `outputs/forecasts/forecast_evaluation_metrics.csv`

---

## 9. Viva Voce Defense & Methodology Guide for Engineering Students

1. **Why SARIMAX(1,1,1)(1,1,0)[7]?**
   - Non-seasonal $(1,1,1)$ models autoregression (yesterday's queries influence today), first-differencing eliminates non-stationarity, and moving-average captures short-term shocks.
   - Seasonal $(1,1,0)[7]$ accounts for the weekly 7-day cyclical agricultural pattern (farmers call heavily during weekdays and significantly less on Sundays).
2. **Why compare with a Seasonal Naive baseline?**
   - In time-series research, complex models like SARIMAX must be justified by outperforming a standard benchmark (last week's same-day observation: $y_{t-7}$).
3. **What are the limitations of Pearson Correlation on Time-Series?**
   - Daily time-series data often exhibit serial autocorrelation. Ordinary correlation tests assume independent and identically distributed (i.i.d.) observations, which can inflate test statistics. Therefore, correlation indicates statistical association in this sample, not economic causation.
4. **How are mandi closures and holidays handled?**
   - Mandis are closed on Sundays and gazetted holidays. Commodity wholesale prices are held constant (forward-filled) to preserve continuity without inventing synthetic trade volumes.

---
*AgriStress Analytics — Automated Academic Research Pipeline Output*