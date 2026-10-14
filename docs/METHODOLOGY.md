# AgriStress Analytics — Econometric and Forecasting Methodology

This document outlines the theoretical, mathematical, and algorithmic foundations of the AgriStress Analytics system. It is written to serve as both technical documentation and a reference guide for an academic defense or viva.

---

## 1. Research Motivation and Problem Definition

Public agricultural advisory infrastructure in India, primarily delivered through the **Kisan Call Centre (KCC)** network (toll-free 1800-180-1551), experiences sharp temporal and seasonal fluctuations in farmer inquiries. 

While seasonal agro-climatic drivers (such as monsoon onset and sowing periods) explain a major portion of call volume, farmers also experience severe **economic distress shocks** caused by:
1. Volatile farm-gate commodity prices and sudden market crashes.
2. Expanding margins between wholesale and retail prices (where consumers pay high prices while farmers receive low realizations).
3. Fuel inflation shocks (spikes in High Speed Diesel prices that inflate irrigation pumping and tractor transport costs).

The core objective of AgriStress Analytics is to model whether these economic indicators can help forecast peaks in farmer advisory demand and evaluate operational advisory-service stress using SARIMAX time-series econometrics.

---

## 2. Mathematical Definition of Variables

| Variable Symbol | Variable Name | Unit | Mathematical Definition |
| :--- | :--- | :--- | :--- |
| $Q_t$ | Daily Query Influx | Inquiries / day | $Q_t = \sum_{k \in \text{Categories}} q_{k, t}$ |
| $P_t^W$ | Wholesale Mandi Price | INR / Quintal | Modal wholesale transaction price reported by APMC Mandis |
| $P_t^R$ | Retail Price | INR / Quintal | Retail selling price reported at major consumption markets |
| $D_t$ | Diesel Fuel Price | INR / Litre | Retail Selling Price (RSP) of High Speed Diesel |
| $\Delta P_t^W$ | Price Daily Difference | INR / Quintal | $\Delta P_t^W = P_t^W - P_{t-1}^W$ |
| $\% \Delta P_t^W$ | Commodity Percentage Return | Percent (%) | $\% \Delta P_t^W = \left(\frac{P_t^W - P_{t-1}^W}{P_{t-1}^W}\right) \times 100$ |
| $\sigma_{7, t}^P$ | 7-Day Rolling Volatility | INR / Quintal | $\sqrt{\frac{1}{6} \sum_{i=0}^6 (P_{t-i}^W - \bar{P}_{7, t}^W)^2}$ |
| $S_t$ | Wholesale-to-Retail Spread | INR / Quintal | $S_t = P_t^R - P_t^W$ (defined only when $P_t^R$ exists) |
| $M_t$ | Retail Margin Spread (%) | Percent (%) | $M_t = \left(\frac{P_t^R - P_t^W}{P_t^W}\right) \times 100$ |
| $\% \Delta D_t$ | Fuel Percentage Change | Percent (%) | $\% \Delta D_t = \left(\frac{D_t - D_{t-1}}{D_{t-1}}\right) \times 100$ |

---

## 3. Data Alignment and Frequency Strategy

1. **Daily Continuous Grid:**
   - Mandi auctions typically occur Monday through Saturday; call centers operate daily.
   - To avoid false missing values on non-trading days, commodity prices and fuel rates are carried forward using forward-fill ($\text{ffill}$), preserving the last available market information available to farmers.
2. **Avoiding Many-to-Many Join Explosion:**
   - Instead of joining raw district records directly, KCC queries are aggregated at the regional/state level before joining with state-level fuel prices.
3. **Missing Count Policy:**
   - Missing call counts for observed center operational days are assigned $0$ (zero recorded calls), rather than dropped.

---

## 4. Hypothesis Testing Framework

The system tests three specific, scientifically defensible hypotheses.

### Hypothesis A: Commodity Price Movements
- **Null Hypothesis ($H_0$):** There is no statistically detectable linear association between commodity price percentage changes and KCC query demand ($\rho = 0$).
- **Alternative Hypothesis ($H_1$):** A statistically detectable linear association exists ($\rho \neq 0$).
- **Statistical Test:** Pearson product-moment correlation test:
  $$r = \frac{\sum_{t=1}^N (Q_t - \bar{Q})(\%\Delta P_t^W - \bar{\%\Delta P})}{\sqrt{\sum (Q_t - \bar{Q})^2 \sum (\%\Delta P_t^W - \bar{\%\Delta P})^2}}$$
- **Decision Rule:** Reject $H_0$ if $p < 0.05$.

### Hypothesis B: Diesel Fuel Price Shocks
- **Shock Rule Definition:** An observation day $t$ is designated as a "Shock Day" if the absolute daily diesel percentage change meets or exceeds 2%:
  $$\text{Shock}_t = \begin{cases} 1 & \text{if } |\% \Delta D_t| \ge 2.0\% \\ 0 & \text{otherwise} \end{cases}$$
- **Null Hypothesis ($H_0$):** The distribution of query demand on diesel price shock days is identical to query demand on normal days ($F_{\text{shock}}(Q) = F_{\text{normal}}(Q)$).
- **Alternative Hypothesis ($H_1$):** The distributions differ significantly.
- **Statistical Test:** Mann-Whitney U Two-Sample Rank-Sum Test (non-parametric, robust to non-normal distributions and outlier spikes).

### Hypothesis C: Wholesale-to-Retail Price Spreads
- **Null Hypothesis ($H_0$):** The wholesale-to-retail margin spread $S_t$ has no monotonic association with query volume.
- **Alternative Hypothesis ($H_1$):** A monotonic association exists.
- **Statistical Test:** Spearman Rank-Order Correlation Coefficient ($\rho_s$).
- **Note:** Computed strictly when comparable retail price data is logged.

---

## 5. Time-Series Forecasting: SARIMAX

### Model Specification
The time series exhibits both trend persistence and a prominent 7-day cyclical periodicity (due to weekend call center operations). We specify a seasonal autoregressive integrated moving average model with weekly seasonality:
$$\text{SARIMAX}(p=1, d=1, q=1) \times (P=1, D=1, Q=0)_{s=7}$$

In lag operator polynomial form:
$$\Phi_P(L^7) \phi_p(L) (1 - L)^d (1 - L^7)^D Q_t = \theta_q(L) \Theta_Q(L^7) \epsilon_t + \beta X_t$$
where:
- $L$ is the backshift lag operator ($L^k y_t = y_{t-k}$).
- $(1 - L)^1$ represents first-order non-seasonal differencing (to achieve stationarity).
- $(1 - L^7)^1$ represents 7-day seasonal differencing (to remove weekly seasonality).
- $s = 7$ specifies the weekly period.
- $X_t$ represents optional exogenous economic variables (e.g., commodity price volatility or fuel shock indicators).

### Chronological Validation
**Random train-test splits (such as K-fold cross-validation) violate the temporal order of time series.** If random shuffling is used, future observations leak into the past, causing severe lookahead bias.
We enforce strict chronological splitting:
- **Training Set:** The initial 80% chronological observations ($t = 1, \dots, T_{\text{train}}$).
- **Testing Set:** The remaining 20% chronological observations ($t = T_{\text{train}}+1, \dots, T$).

### Baseline Benchmark Model
Any forecasting model must be evaluated against a transparent naive baseline before claiming superior performance. We implement a **7-Day Seasonal Naive Baseline**:
$$\hat{Q}_{t}^{\text{baseline}} = Q_{t-7}$$
This predicts that query volume today will equal the query volume observed exactly one week ago.

### Error Metrics
1. **Mean Absolute Error (MAE):**
   $$\text{MAE} = \frac{1}{N} \sum_{t=1}^N |Q_t - \hat{Q}_t|$$
2. **Root Mean Squared Error (RMSE):**
   $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{t=1}^N (Q_t - \hat{Q}_t)^2}$$
3. **Zero-Safe Mean Absolute Percentage Error (MAPE):**
   $$\text{MAPE} = \frac{1}{N} \sum_{t=1}^N \frac{|Q_t - \hat{Q}_t|}{\max(Q_t, 1)} \times 100\%$$

---

## 6. Transparent Advisory-Stress Indicator

To translate numerical forecasts into practical operational insights, forecasted demand $\hat{Q}_{t}$ is mapped into three explainable stress categories based on the historical sample mean $\mu_{\text{hist}}$ and standard deviation $\sigma_{\text{hist}}$:

```
[ Normal ]   :  Demand < Baseline Mean + (0.75 * StdDev)
[ Elevated ] :  Baseline Mean + (0.75 * StdDev) <= Demand < Baseline Mean + (1.75 * StdDev)
[ High ]     :  Demand >= Baseline Mean + (1.75 * StdDev)
```

### Uncertainty Handling
If the 95% upper confidence interval bound $\hat{Q}_{t}^{\text{upper}}$ crosses into the `High` stress threshold while the point forecast $\hat{Q}_{t}$ is in `Elevated`, the system explicitly appends an **uncertainty advisory warning**.
