# AgriStress Analytics — Research Summary Report
**Generated At:** 2026-10-14 01:55:17 UTC

## 1. Project Background and Research Scope
This report investigates associations between farmer advisory demand logged through India's
Kisan Call Centre (KCC), agricultural commodity wholesale prices, and retail diesel fuel price adjustments.
> **Methodological Disclaimer:** Observed statistical correlations represent descriptive associations
> within the analyzed sample and do not prove economic causation. Query demand reflects received requests
> rather than direct staffing capacity mandates.

## 2. Sample Period and Data Scope
- **Start Date:** 2024-01-01 00:00:00
- **End Date:** 2025-12-30 00:00:00
- **Total Daily Observations:** 730

## 3. Descriptive Statistics
| Variable | Count | Mean | Std Dev | Min | Median | Max |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `query_count` | 730 | 261.78 | 108.03 | 46.0 | 253.5 | 458.0 |
| `wholesale_price` | 730 | 1877.92 | 145.13 | 1526.35 | 1915.82 | 2135.3 |
| `retail_price` | 730 | 2542.44 | 212.85 | 2031.65 | 2575.68 | 2988.29 |
| `diesel_price` | 730 | 100.75 | 5.76 | 90.4 | 101.2 | 111.5 |
| `price_spread` | 730 | 664.52 | 87.52 | 453.27 | 662.92 | 895.98 |
| `commodity_volatility_7d` | 729 | 23.37 | 9.16 | 4.44 | 21.89 | 64.75 |

## 4. Hypothesis Testing Results

### HYP-A: Commodity Price Movements vs Query Demand
- **Null Hypothesis (H0):** Commodity price changes have no statistically detectable association with KCC query demand.
- **Alternative Hypothesis (H1):** Commodity price changes exhibit a statistically detectable linear or rank association with KCC query demand.
- **Statistical Test:** Pearson Correlation Test (N = 729)
- **Test Statistic:** 0.0056 | **P-Value:** 0.88038
- **Decision:** Fail to Reject H0 (alpha = 0.05)
- **Plain English Verdict:** Fail to reject null hypothesis (r = 0.0056, p = 0.8804). No statistically significant linear association was detected between commodity price percentage changes and query demand in this sample.
- **Limitations:** Correlation does not imply economic causation. Seasonal monsoon patterns also influence both prices and queries.

### HYP-B: Diesel Price Shocks vs Advisory Influx
- **Null Hypothesis (H0):** KCC query demand does not differ between diesel price shock days and normal price days.
- **Alternative Hypothesis (H1):** KCC query demand differs significantly during or immediately following diesel price shocks.
- **Statistical Test:** Mann-Whitney U Two-Sample Rank Sum Test (N = 729)
- **Test Statistic:** 2206.5 | **P-Value:** 0.39874
- **Decision:** Fail to Reject H0 (alpha = 0.05)
- **Plain English Verdict:** Fail to reject null hypothesis (Mann-Whitney U = 2206.5, p = 0.3987). No statistically significant difference in query influx was observed between shock days (mean = 299.6) and normal days (mean = 261.6).
- **Limitations:** Shock defined as |daily diesel % change| >= 2.0%. Only 5 shock days identified.

### HYP-C: Wholesale-to-Retail Price Spreads vs Query Influx
- **Null Hypothesis (H0):** The wholesale-to-retail commodity price spread has no association with KCC query influx.
- **Alternative Hypothesis (H1):** Wider wholesale-to-retail price spreads are associated with higher advisory demand.
- **Statistical Test:** Spearman Rank Correlation Test (N = 730)
- **Test Statistic:** 0.0562 | **P-Value:** 0.12936
- **Decision:** Fail to Reject H0 (alpha = 0.05)
- **Plain English Verdict:** Fail to reject null hypothesis (Spearman rho = 0.0562, p = 0.1294). Price spread variation is not significantly correlated with query influx.
- **Limitations:** Retail price data is frequently missing in primary mandi feeds; only matched pairs are tested.

## 5. Generated Visualizations
The following charts were generated and saved to `outputs/charts/`:
- `query_demand_over_time.png`
- `seasonality_patterns.png`
- `commodity_price_trends.png`
- `diesel_price_trends.png`
- `price_spreads.png`
- `query_vs_economic.png`
- `regional_queries.png`
- `correlation_heatmap.png`

## 6. Research Limitations
- **Data Aggregation:** KCC calls are aggregated daily; intraday spikes during weather emergencies are smoothed out.
- **Fuel Price Granularity:** Diesel prices reflect state/metro reporting rather than specific rural revenue blocks.
- **Synthetic Data Caution:** If demonstration data was used, empirical inferences cannot be generalized to real field conditions.