# AgriStress Analytics — Comprehensive Research Summary Report

**Date Generated:** 2026-10-20 12:57:57 UTC  
**Research Topic:** Econometric and Spatial-Temporal Analysis of Farmer Information Demand: Modeling Kisan Call Centre (KCC) Query Influx Against Commodity Price Spreads and Fuel Inflation Shocks to Forecast Agricultural Advisory Stress  
**Data Provenance:** REAL OPERATIONAL DATASET  

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

- **Sample Date Range:** 2023-01-01 to 2023-06-29
- **Total Calendar Days:** 180
- **Observed Query Days:** 180
- **Unrecorded / Zero Query Days:** 0 (0.0%)
- **Data Quality Assessment:** GOOD

**Quality & Missingness Handling Notes:**
- PROVENANCE: Real operational data imported from official sources.
- Mandi holiday / Sunday closures are forward-filled for price continuous continuity.

---

## 3. Descriptive Statistics

| Variable | Count | Mean | Std Dev | Min | Median | Max | Units |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `query_count` | 180 | 141.56 | 49.99 | 69.00 | 132.50 | 246.00 | Calls / Day |
| `wholesale_price` | 180 | 1755.94 | 994.25 | 579.45 | 1138.53 | 3044.04 | INR / Quintal |
| `retail_price` | 180 | 3054.98 | 540.42 | 2254.94 | 3203.18 | 3702.98 | INR / Quintal |
| `diesel_price` | 180 | 97.86 | 2.43 | 94.50 | 96.86 | 100.78 | INR / Litre |
| `price_spread` | 180 | 1299.04 | 600.13 | 573.20 | 1385.99 | 2728.31 | INR / Quintal |
| `commodity_volatility_7d` | 179 | 57.97 | 79.52 | 14.77 | 32.37 | 354.82 | INR (7D Std) |

---

## 4. Econometric Correlation Analysis

| Variable Pair | Pearson $r$ | Spearman $\rho$ | Sample Size ($N$) | Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| KCC Demand vs Wholesale Commodity Price | -0.8329 | -0.8840 | 180 | Strong correlation |
| KCC Demand vs Commodity Price Daily Change | -0.1232 | -0.0398 | 179 | Weak correlation |
| KCC Demand vs 7-Day Commodity Price Volatility | 0.3510 | 0.4424 | 179 | Weak correlation |
| KCC Demand vs Wholesale-Retail Price Spread | 0.9265 | 0.9093 | 180 | Strong correlation |
| KCC Demand vs Diesel Price Level | 0.4904 | 0.5661 | 180 | Moderate correlation |
| KCC Demand vs Diesel Daily Price Change | 0.0684 | 0.0686 | 179 | Weak correlation |
| KCC Demand vs 7-Day Lagged Diesel Price Change | 0.0648 | 0.0676 | 172 | Weak correlation |

---

## 5. Formal Hypothesis Testing Results

### ⚪ HYP-A: Commodity Price Movements vs Query Demand
- **Research Question:** Do day-to-day percentage changes in wholesale commodity prices linearly correlate with KCC advisory query volume?
- **Null Hypothesis ($H_0$):** Daily commodity percentage changes have no linear correlation with farmer query volume (r = 0).
- **Alternative Hypothesis ($H_1$):** Daily commodity percentage changes are linearly correlated with farmer query volume (r != 0).
- **Statistical Test Used:** Pearson Linear Correlation Test ($N = 179$)
- **Test Statistic:** `-0.1127` | **p-value:** `0.13303` | **Significance Level ($\\alpha$):** 0.05
- **Outcome:** **FAIL TO REJECT NULL HYPOTHESIS**
- **Plain English Verdict:** Fail to reject null hypothesis (r=-0.1127, p=0.1330)
- **Statistical Assumptions:** Assumes linear relationship and bivariate normality. Time-series autocorrelation can artificially narrow standard errors.
- **Research Limitations:** Linear correlation does not imply causality; price shocks may have delayed non-linear effects not captured by contemporaneous Pearson r.

### ⚪ HYP-B: Diesel Price Shocks vs Advisory Influx
- **Research Question:** Do diesel price shocks trigger advisory demand shifts?
- **Null Hypothesis ($H_0$):** Query demand is identical during shock and normal fuel days.
- **Alternative Hypothesis ($H_1$):** Query demand differs significantly during diesel price shocks.
- **Statistical Test Used:** Mann-Whitney U Test ($N = 179$)
- **Test Statistic:** `None` | **p-value:** `None` | **Significance Level ($\\alpha$):** 0.05
- **Outcome:** **FAIL TO REJECT NULL HYPOTHESIS**
- **Plain English Verdict:** Too few diesel price shocks detected (3 shock days with |change| >= 1.0%).
- **Statistical Assumptions:** Requires >= 5 shock days and >= 15 normal days.
- **Research Limitations:** Fuel price revisions occur intermittently in administered pricing regimes.

### 🔴 HYP-C: Wholesale-to-Retail Price Spreads vs Query Influx
- **Research Question:** Is the spread between wholesale mandi price and retail consumer price monotonically associated with farmer query demand?
- **Null Hypothesis ($H_0$):** There is no monotonic rank association between price spread and KCC query demand (rho = 0).
- **Alternative Hypothesis ($H_1$):** Price spread and KCC query demand are monotonically associated (rho != 0).
- **Statistical Test Used:** Spearman Rank-Order Correlation Test ($N = 180$)
- **Test Statistic:** `0.9093` | **p-value:** `0.0` | **Significance Level ($\\alpha$):** 0.05
- **Outcome:** **REJECT NULL HYPOTHESIS**
- **Plain English Verdict:** Reject null hypothesis (rho=0.9093, p=0.0000)
- **Statistical Assumptions:** Monotonic relationship; does not assume linear bivariate normality.
- **Research Limitations:** Wholesale-retail spread is observable only where matching commodity retail observations exist.

---

## 6. Time-Series Forecasting & Model Validation

- **Model Selected:** `SARIMAX(1,1,1)(1,1,0)[7]`
- **Evaluation Methodology:** Chronological Train/Test Holdout Split (avoiding future data leakage)
- **Train Period:** 2023-01-01 to 2023-05-30
- **Test Period:** 2023-05-31 to 2023-06-29
- **Forecast Horizon:** 14 Days

### Out-of-Sample Holdout Performance Comparison

| Forecasting Model | MAE (Calls) | RMSE (Calls) | Zero-Safe MAPE (%) | Status |
| :--- | :---: | :---: | :---: | :--- |
| Seasonal Naive Baseline (7-Day Lag) | 9.83 | 11.81 | 7.08% | Benchmark |
| SARIMAX(1,1,1)(1,1,0)[7] | 10.46 | 12.88 | 7.32% | **Selected Model** |

---

## 7. Agricultural Advisory Stress Indicator

- **Operational Stress Category:** `NORMAL`
- **Historical Baseline Mean:** 141.6 inquiries/day
- **Elevated Stress Threshold:** >= 179.1 inquiries/day (Historical Mean + 0.75 * Std Dev)
- **High Advisory Stress Threshold:** >= 229.0 inquiries/day (Historical Mean + 1.75 * Std Dev)
- **Interpretation:** Forecast (154.0) is within normal parameters (baseline mean: 141.6).
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