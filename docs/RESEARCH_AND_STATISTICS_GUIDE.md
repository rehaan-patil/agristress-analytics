# AgriStress Analytics — Research & Statistics Guide for Teammates

This guide provides an intuitive, step-by-step mathematical explanation of the econometric tests, time-series forecasting models, and error metrics implemented in AgriStress Analytics.

---

## 1. Feature Engineering Formulas

All features are calculated inside [build_analytical_dataset](file:///d:/python-capstone/app/data_processing.py#L198) in `app/data_processing.py`.

### A. Commodity Price Change & Percentage Return
- **Absolute Change:**
  $$\Delta P_t = P_t - P_{t-1}$$
  Measures the raw price drop or increase in INR per Quintal (100 kg).
- **Percentage Change (Return):**
  $$\% \Delta P_t = \left(\frac{P_t - P_{t-1}}{P_{t-1}}\right) \times 100$$
  *Example:* If wheat wholesale price was ₹2,400 yesterday and is ₹2,340 today:
  $$\% \Delta P_t = \frac{2340 - 2400}{2400} \times 100 = -2.5\%$$

### B. 7-Day Rolling Price Volatility
Measures how wildly wholesale prices are swinging over the past week:
$$\sigma_{7,t} = \sqrt{\frac{1}{6} \sum_{i=0}^6 (P_{t-i} - \bar{P}_{7,t})^2}$$
Where $\bar{P}_{7,t}$ is the 7-day average price. A low volatility (₹10–₹20) means stable trading; high volatility (> ₹100) indicates market disruption.

### C. Wholesale-to-Retail Margin Spread
Measures the wedge between farm-gate wholesale price and urban retail price:
$$S_t = P_t^{\text{retail}} - P_t^{\text{wholesale}}$$
- **Retail Margin Percentage:**
  $$M_t = \left(\frac{P_t^{\text{retail}} - P_t^{\text{wholesale}}}{P_t^{\text{wholesale}}}\right) \times 100$$
  *Example:* If wholesale onion is ₹2,000/Qtl (₹20/kg) and retail onion is ₹3,000/Qtl (₹30/kg), $S_t = ₹1,000$ and $M_t = 50\%$.

### D. Diesel Price Shock Rule
A day $t$ is designated as a shock day if the daily percentage change meets or exceeds the threshold:
$$\text{Is Shock}_t = \begin{cases} 1 & \text{if } |\% \Delta D_t| \ge 2.0\% \\ 0 & \text{otherwise} \end{cases}$$

---

## 2. Hypothesis Testing: Intuition & Formulas

Implemented in [run_hypothesis_tests](file:///d:/python-capstone/app/analysis.py#L107) in `app/analysis.py`.

### What is a Hypothesis Test?
Imagine a court trial:
- **Null Hypothesis ($H_0$):** The defendant is innocent (there is **no association** between economic variable $X$ and farmer calls $Y$).
- **Alternative Hypothesis ($H_1$):** The defendant is guilty (a statistically detectable association exists).
- **P-Value:** The probability of seeing our data if $H_0$ was actually true. If $p < 0.05$ (less than 5% chance of pure coincidence), we reject the null hypothesis and declare a statistically significant association!

---

### Hypothesis A: Commodity Price Movements
- **Question:** Do daily commodity price percentage changes associate with KCC call volume?
- **Formula (Pearson Correlation $r$):**
  $$r = \frac{\sum (Q_t - \bar{Q})(\%\Delta P_t - \bar{\%\Delta P})}{\sqrt{\sum (Q_t - \bar{Q})^2 \sum (\%\Delta P_t - \bar{\%\Delta P})^2}}$$
- **Values:** $r \in [-1, 1]$.
  - $r > 0$: As price increases, queries increase.
  - $r < 0$: As price drops, queries increase (distress selling inquiries).
  - $r \approx 0$: No linear relationship.
- **Assumptions:** Continuous linear relationship, approximately normal errors.

---

### Hypothesis B: Diesel Fuel Price Shocks
- **Question:** Is query demand significantly higher on diesel shock days compared to normal price days?
- **Why Mann-Whitney U?**
  Call count data is non-normal and heavily skewed with weekend zeros. A standard Student's t-test assumes bell-curve normal distributions. The **Mann-Whitney U test** is a non-parametric test that ranks observations from smallest to largest and checks whether shock days systematically rank higher:
  $$U = n_1 n_2 + \frac{n_1(n_1 + 1)}{2} - R_1$$
  Where $R_1$ is the sum of ranks for the shock group.

---

### Hypothesis C: Wholesale-to-Retail Price Spreads
- **Question:** Does a wider retail margin spread correlate with call influx?
- **Formula (Spearman Rank Correlation $\rho_s$):**
  $$\rho_s = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)}$$
  Where $d_i$ is the difference between the rank of query demand and the rank of price spread on day $i$. Suitable for non-linear monotonic relationships.

---

## 3. Time-Series Forecasting: SARIMAX

Implemented in [app/forecasting.py](file:///d:/python-capstone/app/forecasting.py).

### Why Standard Regression Fails for Time Series
Standard linear regression assumes observations are independent:
$$y_i = \beta_0 + \beta_1 x_i + \epsilon_i, \quad \epsilon_i \overset{\text{iid}}{\sim} \mathcal{N}(0, \sigma^2)$$
In call centres, today's call count ($Q_t$) is strongly correlated with yesterday's call count ($Q_{t-1}$). Treating them as independent produces biased, invalid standard errors.

### Breaking Down SARIMAX(1, 1, 1)(1, 1, 0)[7]
1. **$p=1$ (Autoregressive Order):** Predicts today's value based on yesterday's value: $\phi_1 Q_{t-1}$.
2. **$d=1$ (Differencing):** Replaces raw counts with daily changes ($Q_t - Q_{t-1}$) to remove long-term trends and make the series stationary.
3. **$q=1$ (Moving Average Order):** Incorporates yesterday's unexpected shock: $\theta_1 \epsilon_{t-1}$.
4. **$P=1, D=1, s=7$ (Weekly Seasonality):** Differences values across a 7-day cycle ($Q_t - Q_{t-7}$) to explicitly capture the drop on Sundays.

### Forecast Evaluation Metrics
Let $y_t$ be the actual call volume and $\hat{y}_t$ be the model forecast on test day $t$:

1. **Mean Absolute Error (MAE):**
   $$\text{MAE} = \frac{1}{N} \sum_{t=1}^N |y_t - \hat{y}_t|$$
   *Meaning:* On average, our prediction is off by $\pm \text{MAE}$ calls.
2. **Root Mean Squared Error (RMSE):**
   $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{t=1}^N (y_t - \hat{y}_t)^2}$$
   *Meaning:* Because errors are squared, RMSE penalizes large misses much more severely than small misses.
3. **Zero-Safe MAPE (%):**
   $$\text{MAPE} = \frac{1}{N} \sum_{t=1}^N \frac{|y_t - \hat{y}_t|}{\max(y_t, 1)} \times 100\%$$
   *Meaning:* Average percentage error. Using $\max(y_t, 1)$ prevents division by zero when calls are 0 on Sundays.

---

## 4. Advisory Stress Classification Formula

Implemented in [classify_advisory_stress](file:///d:/python-capstone/app/forecasting.py#L36).

We compute the historical baseline mean $\mu_{\text{hist}}$ and standard deviation $\sigma_{\text{hist}}$ across all observed days:

$$\text{Elevated Cutoff} = \mu_{\text{hist}} + 0.75 \cdot \sigma_{\text{hist}}$$
$$\text{High Cutoff} = \mu_{\text{hist}} + 1.75 \cdot \sigma_{\text{hist}}$$

```
                      Normal                  Elevated                 High
          |---------------------------|-----------------------|---------------------->
       0 calls                     +0.75σ                  +1.75σ
                                  (Elevated)               (High)
```

- If $\hat{Q}_{\text{future}} < \text{Elevated Cutoff} \implies$ **Normal**
- If $\text{Elevated Cutoff} \le \hat{Q}_{\text{future}} < \text{High Cutoff} \implies$ **Elevated**
- If $\hat{Q}_{\text{future}} \ge \text{High Cutoff} \implies$ **High**

---

*For complete architecture and code walkthrough, see [docs/PROJECT_EXPLANATION_FOR_TEAM.md](file:///d:/python-capstone/docs/PROJECT_EXPLANATION_FOR_TEAM.md).*
