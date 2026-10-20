# AgriStress Analytics — Graph Presentation & Slide Deck Guide

> **Document Purpose:** Presentation script, visual reading guide, and slide-by-slide defense notes for all 10 generated analytical figures.  
> **Target Audience:** First-Year Engineering Students presenting AgriStress Analytics during a project review, symposium, or final viva voce.  
> **All Charts Located In:** `outputs/charts/`

---

## Recommended Presentation Narrative & Slide Order

When presenting this project to an evaluation committee, do not present graphs randomly. Present them in this logical **5-Act Research Narrative**:

```mermaid
flowchart LR
    ACT1["Act 1: The Problem<br/>Graph 1: Demand Over Time<br/>Graph 2: Weekly Seasonality"] --> ACT2["Act 2: Market Shocks<br/>Graph 3: Wholesale & Volatility<br/>Graph 4: Diesel Revisions<br/>Graph 5: Price Spreads"]
    ACT2 --> ACT3["Act 3: Econometric Link<br/>Graph 6: Demand vs Price<br/>Graph 7: Correlation Heatmap"]
    ACT3 --> ACT4["Act 4: Spatial Context<br/>Graph 8: Regional Queries"]
    ACT4 --> ACT5["Act 5: Operational Solution<br/>Graph 9: Forecast Evaluation<br/>Graph 10: Holdout Test Zoom"]
```

### Why This Order Tells a Coherent Story:
1. **Act 1 (Graphs 1 & 2):** Establishes the phenomenon: farmer helpline call volume fluctuates widely and follows a strong 7-day weekly cycle.
2. **Act 2 (Graphs 3, 4 & 5):** Establishes the economic context: wholesale prices crash, volatility spikes, fuel revisions occur in steps, and the wholesale-retail spread expands.
3. **Act 3 (Graphs 6 & 7):** Connects the two sides: proves that inquiry surges coincide with market price collapses and expanding marketing margins.
4. **Act 4 (Graph 8):** Shows geographical distribution to identify which state bears the largest operational load.
5. **Act 5 (Graphs 9 & 10):** Delivers the operational solution: demonstrates out-of-sample holdout validation and provides a 14-day proactive capacity forecast for call-centre administrators.

---

## Detailed Breakdown of Every Individual Chart

---

### Figure 1: `query_demand_over_time.png`

```text
+-----------------------------------------------------------------------+
|          Kisan Call Centre (KCC) Query Influx Over Time               |
|                                                                       |
|  250 |           /\                                                   |
|      |          /  \      /\                  --- Raw Daily (Blue)    |
|  150 |   /\    /    \    /  \      /\         --- 14D Mean (Red)      |
|      |  /  \  /      \  /    \    /  \                                |
|   50 | /    \/        \/      \  /    \                               |
|    0 +--------------------------------------+                         |
|     2023-01         2023-03         2023-06                           |
+-----------------------------------------------------------------------+
```

- **Filename:** `outputs/charts/query_demand_over_time.png`
- **Research Question:** How does farmer information demand evolve over time, and can we distinguish between daily high-frequency noise and underlying seasonal trends?
- **Why We Created It:** To visualize the raw time series of farmer inquiries and verify whether inquiry volume is stationary or exhibits macro-level drift and surges.
- **Axes, Units & Variables:**
  - **X-Axis:** Date (Daily continuous calendar time, from January 2023 to June 2023).
  - **Y-Axis:** Inquiry Volume (Number of calls logged per day, ranging from 69 to 246 calls).
  - **Legend & Lines:**
    - Semi-transparent Blue Line (`alpha=0.5`): Raw daily call counts ($y_t$).
    - Solid Red Line (`linewidth=2`): 14-day rolling moving average ($\bar{y}_{14d, t}$).
- **Data Source & Frequency:** KCC observation database (`kcc_observations`), aggregated at Daily (`'D'`) frequency.
- **Plotting Function:** `app/analysis.py:plot_query_demand_over_time()` (lines 331–345).
- **What a Viewer Should Notice:** Notice the intense day-to-day fluctuations in the blue line (driven by day-of-week cycles) and the smooth, rising wave in the red 14-day rolling average, which peaks during periods of agricultural market stress.
- **What Can Reasonably Be Concluded:**
  - Daily call volume is non-stationary and exhibits significant volatility.
  - A 14-day smoothing window successfully removes weekly cycles, exposing a macro-level seasonal surge.
- **What CANNOT Be Concluded:**
  - Does not reveal the specific cause of any spike (e.g., whether calls were about market prices, pest attacks, or diesel hikes).
- **Common Presenter Trap:** Saying *"Farmers suddenly started calling on this specific day because of a price crash."* You cannot attribute causality from a single univariate time-series plot.
- **3 Likely Evaluator Questions & Answers:**
  1. *Q: Why did you choose a 14-day rolling window rather than 7 days?*
     - *A:* A 14-day window smooths out two complete 7-day weekly cycles, ensuring that weekend troughs and weekday surges are completely neutralized to reveal the true macro trend.
  2. *Q: What does the minimum value of 69 calls represent?*
     - *A:* It represents the baseline weekend/holiday inquiry floor across the monitored state.
  3. *Q: How does this chart inform your forecasting model?*
     - *A:* The non-constant mean over time confirms non-stationarity, justifying the first-differencing ($d=1$) order in our SARIMAX model.
- **Natural Spoken Script (25–30 Seconds):**
  > *"Respected evaluators, this first figure establishes our target variable: daily farmer inquiry volume to the Kisan Call Centre network. The semi-transparent blue line shows raw daily calls, which fluctuate between 69 and 246 calls due to weekly cycles. To identify the underlying trend, we overlaid a 14-day rolling moving average in red. Notice that farmer inquiries build up into a sustained surge between March and May, indicating an accumulation of operational stress on the helpline."*

---

### Figure 2: `seasonality_patterns.png`

```text
+-----------------------------------------------------------------------+
|               Average KCC Query Volume by Day of Week                 |
|                                                                       |
|  160 |  +---+   +---+   +---+   +---+   +---+                         |
|      |  |   |   |   |   |   |   |   |   |   |                         |
|  100 |  |   |   |   |   |   |   |   |   |   |   +---+                 |
|      |  |   |   |   |   |   |   |   |   |   |   |   |   +---+         |
|    0 +--+---+---+---+---+---+---+---+---+---+---+---+---+---+---+     |
|          Mon     Tue     Wed     Thu     Fri     Sat     Sun          |
+-----------------------------------------------------------------------+
```

- **Filename:** `outputs/charts/seasonality_patterns.png`
- **Research Question:** Does farmer information demand follow a predictable weekly cyclical pattern across the days of the week?
- **Why We Created It:** To test for calendar seasonality and determine whether a seasonal parameter ($s=7$) is mathematically necessary in our forecasting model.
- **Axes, Units & Variables:**
  - **X-Axis:** Day of the Week (Ordered from Monday through Sunday).
  - **Y-Axis:** Mean Inquiries (Average calls logged per day).
  - **Green Bars:** Categorical bar plot displaying mean inquiries per weekday.
- **Data Source & Frequency:** KCC observation database, grouped by day name over the 180-day sample.
- **Plotting Function:** `app/analysis.py:plot_seasonality()` (lines 347–364).
- **What a Viewer Should Notice:** Weekdays (Monday through Friday) maintain consistently high call volumes (~150–160 calls/day), Saturday shows a moderate decline, and Sunday drops drastically to ~50 calls/day.
- **What Can Reasonably Be Concluded:**
  - Farmer inquiry demand exhibits strong, statistically undeniable 7-day cyclicality ($s=7$).
  - Helpline administrators must schedule maximum staffing on weekdays and can operate with reduced skeleton crews on Sundays.
- **What CANNOT Be Concluded:**
  - Does not mean farmers have no agronomic problems on Sundays; rather, mandis are closed, and farmers are less likely to initiate formal inquiries on weekends.
- **Common Presenter Trap:** Claiming that *"Farmers never work on Sundays."* Farmers work daily, but official markets and extension administrative offices operate at reduced weekend capacity.
- **3 Likely Evaluator Questions & Answers:**
  1. *Q: How does this chart directly impact your time-series model?*
     - *A:* It provides visual and empirical justification for setting the seasonal lag parameter to $s=7$ and including seasonal autoregression $P=1$ in SARIMAX.
  2. *Q: What would happen to forecast accuracy if you used a non-seasonal ARIMA(1,1,1) model?*
     - *A:* A non-seasonal model would consistently overpredict Sunday calls by ~100 calls and underpredict Monday calls, drastically inflating MAE and RMSE.
  3. *Q: Are calls zero on Sundays?*
     - *A:* No, calls drop to approximately 40–50 calls/day, confirming that automated lines and emergency services remain operational.
- **Natural Spoken Script (25–30 Seconds):**
  > *"Moving to Figure 2, we investigate calendar seasonality by grouping inquiries by day of the week. The green bars reveal a distinct, recurring pattern: Monday through Friday experience high inquiry volumes averaging over 150 calls daily, whereas Sunday inquiries collapse to roughly 50 calls. This empirical proof of a 7-day cycle is critical: it directly justifies configuring our SARIMAX forecasting model with a seasonal period of $s=7$."*

---

### Figure 3: `commodity_price_trends.png`

```text
+-----------------------------------------------------------------------+
|  A. Agricultural Commodity Wholesale Price Movement                   |
|  3000 | \                                                             |
|  2000 |  \______                                  Wholesale (Green)   |
|  1000 |         \_______                                              |
|       +------------------------------------+                          |
|  B. 7-Day Rolling Price Volatility                                    |
|   300 |            /\                                                 |
|   150 |           /  \                            Volatility (Amber)  |
|     0 +----------/----\--------------------+                          |
|         2023-01         2023-03         2023-06                       |
+-----------------------------------------------------------------------+
```

- **Filename:** `outputs/charts/commodity_price_trends.png`
- **Research Question:** How did wholesale commodity prices move over the sample period, and when did the market experience peak price turbulence?
- **Why We Created It:** To track the primary economic driver of farmer income and quantify periods of rapid price instability.
- **Axes, Units & Variables (2 Stacked Subplots):**
  - **Shared X-Axis:** Date (January 2023 to June 2023).
  - **Panel A (Top):** Wholesale Mandi Price in INR/Quintal (Green line, ranging from ₹3,044 down to ₹579/qtl).
  - **Panel B (Bottom):** 7-Day Rolling Price Volatility in INR (Amber line, sample standard deviation $\sigma_{7d}$ over a 7-day window, reaching peaks over ₹350).
- **Data Source & Frequency:** Mandi commodity price records (`commodity_observations`), aggregated daily.
- **Plotting Function:** `app/analysis.py:plot_commodity_trends()` (lines 366–387).
- **What a Viewer Should Notice:** In Panel A, wholesale prices experienced a persistent, multi-month crash from over ₹3,000/qtl in January down to under ₹1,000/qtl by May. In Panel B, notice that during the steepest price drop, rolling volatility spiked above ₹350.
- **What Can Reasonably Be Concluded:**
  - The market experienced severe price erosion and acute short-term volatility during the spring harvest season.
  - Mandi closures on Sundays do not cause gaps in the curve because our pipeline applies forward-fill price continuity.
- **What CANNOT Be Concluded:**
  - Does not prove whether the price drop was caused by nationwide overproduction, bumper local arrivals, or import policy changes.
- **Common Presenter Trap:** Confusing price level with price volatility. High volatility means prices are fluctuating rapidly; low volatility can occur even when prices are depressed at a flat low level.
- **3 Likely Evaluator Questions & Answers:**
  1. *Q: Why plot price and volatility in separate subplots instead of a single dual-axis plot?*
     - *A:* Stacked subplots provide a cleaner comparison without visual line crossing, and separate Y-axes prevent the volatility curve from being vertically compressed.
  2. *Q: How is the 7-day rolling volatility calculated mathematically?*
     - *A:* As the rolling sample standard deviation of wholesale prices over a 7-day sliding window with `min_periods=2`.
  3. *Q: How does this chart correlate with our inquiry demand in Figure 1?*
     - *A:* Comparing the two shows that as wholesale prices collapsed in Panel A, farmer call volume in Figure 1 rose to its highest levels.
- **Natural Spoken Script (30 Seconds):**
  > *"In Figure 3, we turn to the economic pressures facing farmers. Panel A plots the wholesale mandi price in green, showing a steep price collapse from over ₹3,000 per quintal down to ₹600 per quintal. Panel B plots the 7-day rolling price volatility in amber. Notice the dramatic spike in volatility in early spring, marking a period of extreme market turbulence where day-to-day prices swung wildly. This severe price erosion forms the economic backdrop of farmer stress."*

---

### Figure 4: `diesel_price_trends.png`

```text
+-----------------------------------------------------------------------+
|  A. Retail Diesel Price Trajectory                                    |
|   100 |         -----------------           Diesel Level (Magenta)    |
|    95 | ________/                                                     |
|       +------------------------------------+                          |
|  B. Daily Diesel Price Shocks (%)                                     |
|    +2 |         |                 --- Threshold (+1.5%) (Red Dotted)  |
|     0 +---------+------------------+ Revision Bars (Purple)           |
|    -2 |                           --- Threshold (-1.5%)               |
|         2023-01         2023-03         2023-06                       |
+-----------------------------------------------------------------------+
```

- **Filename:** `outputs/charts/diesel_price_trends.png`
- **Research Question:** How did retail diesel prices change over time, and how many official fuel revision shocks occurred in the sample?
- **Why We Created It:** To visualize tractor and transport input cost dynamics and identify shock days for Hypothesis B testing.
- **Axes, Units & Variables (2 Stacked Subplots):**
  - **Shared X-Axis:** Date (Daily timeline).
  - **Panel A (Top):** Retail Diesel Price in INR/Litre (Magenta line, ranging from ₹94.50 to ₹100.78/L).
  - **Panel B (Bottom):** Daily Percentage Change in Diesel Price (Purple vertical bars, with red dotted horizontal threshold lines at $+1.5\%$ and $-1.5\%$).
- **Data Source & Frequency:** Retail fuel records (`fuel_observations`), aggregated daily.
- **Plotting Function:** `app/analysis.py:plot_diesel_trends()` (lines 389–412).
- **What a Viewer Should Notice:** Panel A shows long flat horizontal lines followed by sudden upward steps. Panel B shows mostly zero change on almost all days, with only a few isolated vertical bars.
- **What Can Reasonably Be Concluded:**
  - Retail diesel operates under administered pricing in India, where prices remain frozen for extended periods rather than adjusting daily.
  - Significant price shocks ($|\% \Delta D_t| \ge 1.0\%$) are rare events in this historical window.
- **What CANNOT Be Concluded:**
  - Does not mean fuel price does not matter to farmers; rather, daily price revisions are too infrequent to detect same-day statistical effects in a 180-day window.
- **Common Presenter Trap:** Claiming that diesel prices fluctuated daily. As the plot clearly shows, diesel prices remained flat for weeks at a time.
- **3 Likely Evaluator Questions & Answers:**
  1. *Q: Why are there so few bars in Panel B?*
     - *A:* In India, oil marketing companies adjust fuel prices periodically in discrete steps rather than through continuous floating changes.
  2. *Q: What do the red dotted lines indicate?*
     - *A:* They mark the shock threshold ($\pm 1.5\%$) used to isolate shock days for the Mann-Whitney U test in Hypothesis B.
  3. *Q: How does this chart explain the outcome of Hypothesis B?*
     - *A:* It visually explains why HYP-B failed to reject the null hypothesis: with only 3 shock days detected, the sample size was too small to draw statistically valid conclusions.
- **Natural Spoken Script (25–30 Seconds):**
  > *"Figure 4 illustrates retail diesel fuel dynamics. Panel A displays the retail diesel price in magenta, which moved from ₹94.50 to over ₹100 per litre in step-wise revisions. Panel B isolates the daily percentage revisions in purple, with red dotted lines marking our shock threshold. This visualization clearly demonstrates the nature of administered fuel pricing: long plateaus of zero revision punctuated by rare adjustments, explaining why our statistical test detected only 3 shock days."*

---

### Figure 5: `price_spreads.png`

```text
+-----------------------------------------------------------------------+
|         Wholesale Mandi vs Consumer Retail Price Spread               |
|                                                                       |
|  3500 |  -----------------------------   Retail Price (Purple)        |
|       |  /////////////////////////////   Shaded Spread Margin         |
|  1500 |  \________                       Wholesale Price (Green)      |
|       |           \___________________                                |
|     0 +------------------------------------+                          |
|         2023-01         2023-03         2023-06                       |
+-----------------------------------------------------------------------+
```

- **Filename:** `outputs/charts/price_spreads.png`
- **Research Question:** How does the margin between farmgate wholesale prices and consumer retail prices behave over time?
- **Why We Created It:** To visualize the marketing margin captured by intermediaries and distribution logistics, providing empirical context for Hypothesis C.
- **Axes, Units & Variables:**
  - **X-Axis:** Date (Daily timeline).
  - **Y-Axis:** Price in INR/Quintal (from ₹0 to ₹3,800/qtl).
  - **Top Purple Line:** Consumer Retail Price ($R_t$).
  - **Bottom Green Line:** Wholesale Mandi Price ($W_t$).
  - **Shaded Purple Band:** The marketing spread ($R_t - W_t$).
- **Data Source & Frequency:** Matched wholesale and retail commodity records, daily frequency.
- **Plotting Function:** `app/analysis.py:plot_price_spread()` (lines 414–432).
- **What a Viewer Should Notice:** Notice the massive asymmetry: while the bottom green wholesale price drops steeply, the top purple retail price remains flat and sticky around ₹3,000–₹3,200/qtl. As a result, the shaded purple band widens dramatically.
- **What Can Reasonably Be Concluded:**
  - Retail prices exhibit downward price stickiness: consumers do not benefit when farmgate prices crash.
  - The marketing margin expanded from ₹573/qtl to over ₹2,700/qtl.
- **What CANNOT Be Concluded:**
  - Does not prove intentional cartel price-fixing; transport, handling, packaging, and retailer operating margins also make up this gap.
- **Common Presenter Trap:** Calling the entire shaded area *"trader profit"*. It is the gross marketing spread; net profit is only a portion after deducting transport, spoilage, labor, and packaging.
- **3 Likely Evaluator Questions & Answers:**
  1. *Q: What was the average price spread over the sample?*
     - *A:* ₹1,299.04 per quintal, with a maximum of ₹2,728.31 per quintal.
  2. *Q: How does this chart relate to Hypothesis C?*
     - *A:* This shaded spread is the exact independent variable tested in HYP-C, where we found a strong rank correlation ($\rho = 0.9093$) with farmer call volume.
  3. *Q: Why do retail prices remain sticky when wholesale prices crash?*
     - *A:* Because urban retail markets have fixed costs (shop rent, electricity, transport) and retailers resist cutting consumer prices unless supply surpluses persist for months.
- **Natural Spoken Script (30 Seconds):**
  > *"Figure 5 is one of our most important economic exhibits. The upper purple curve represents the consumer retail price, the lower green curve represents the farmgate wholesale price, and the shaded purple region highlights the marketing spread. Notice the striking divergence: while wholesale prices collapsed by over 70%, urban retail prices remained completely sticky. This ballooning marketing margin coincided with peak farmer call volumes, as confirmed by our Spearman test in Hypothesis C."*

---

### Figure 6: `query_vs_economic.png`

```text
+-----------------------------------------------------------------------+
|    Farmer Information Demand vs Wholesale Commodity Movements         |
|                                                                       |
|  (Calls)                                                    (INR/Qtl) |
|   200 |           /------\                                   | 3000   |
|       |          /        \         ---- Queries (7D MA)     |        |
|   150 |         /          \             (Blue Solid)        | 2000   |
|       |  ------/            \--     ---- Wholesale Price     |        |
|   100 |                        \         (Orange Dashed)     | 1000   |
|       +------------------------------------------------------+        |
|         2023-01               2023-03              2023-06            |
+-----------------------------------------------------------------------+
```

- **Filename:** `outputs/charts/query_vs_economic.png`
- **Research Question:** Is there visible co-movement between smoothed farmer inquiry volume and wholesale commodity price trajectories?
- **Why We Created It:** Dual-axis visual comparison allowing direct trajectory inspection between query demand and wholesale prices.
- **Axes, Units & Variables:**
  - **X-Axis:** Date (Daily timeline).
  - **Left Y-Axis (Blue):** Daily Inquiries (7-Day Moving Average of KCC calls, ranging from 80 to 220 calls).
  - **Right Y-Axis (Orange):** Wholesale Price in INR/Quintal (from ₹600 to ₹3,000/qtl).
  - **Solid Blue Line:** 7-day moving average of farmer inquiries.
  - **Dashed Orange Line:** Wholesale mandi commodity price.
- **Data Source & Frequency:** Aligned analytical dataset (`analytical_dataset.csv`), daily frequency.
- **Plotting Function:** `app/analysis.py:plot_query_vs_economic()` (lines 434–451).
- **What a Viewer Should Notice:** Notice the pronounced scissor-like inverse movement: as the dashed orange price line slopes downward from February through April, the solid blue inquiry line slopes upward, reaching peak call volume at the exact bottom of the price slump.
- **What Can Reasonably Be Concluded:**
  - There is a strong visual inverse association between wholesale price trends and farmer call volume.
  - Confirms the negative correlation coefficient ($r = -0.8329$) found in our correlation table.
- **What CANNOT Be Concluded:**
  - Does not establish causation on its own; dual-axis visual alignment can be influenced by axis scaling.
- **Common Presenter Trap:** Saying *"This proves that the price crash caused the calls."* Always remind evaluators that correlation indicates empirical association, not direct economic causation.
- **3 Likely Evaluator Questions & Answers:**
  1. *Q: Why use a 7-day moving average for queries on this plot?*
     - *A:* To smooth out the weekly Sunday troughs so that the macro-level trend can be compared cleanly with commodity price movements.
  2. *Q: What is the correlation coefficient between these two series?*
     - *A:* Pearson $r = -0.8329$ and Spearman $\rho = -0.8840$, indicating strong inverse association.
  3. *Q: What potential confounding factors could explain this co-movement?*
     - *A:* Peak harvest season brings both high market arrivals (which depress prices) and complex harvest logistics/marketing decisions (which prompt farmer calls).
- **Natural Spoken Script (25–30 Seconds):**
  > *"Figure 6 brings the two sides of our research together on a dual-axis plot. The solid blue curve traces the 7-day moving average of farmer inquiries on the left axis, while the dashed orange curve traces wholesale commodity price on the right axis. Notice the pronounced inverse relationship: as wholesale prices slump between February and May, farmer inquiry volume surges to its peak, visually illustrating our Pearson correlation coefficient of -0.83."*

---

### Figure 7: `correlation_heatmap.png`

```text
+-----------------------------------------------------------------------+
|                     Econometric Correlation Heatmap                   |
|                                                                       |
|  KCC Queries      | +1.00  -0.83  +0.52  +0.49  +0.93  +0.35 |        |
|  Wholesale Price  | -0.83  +1.00  -0.34  -0.54  -0.88  -0.38 |        |
|  Retail Price     | +0.52  -0.34  +1.00  +0.21  +0.65  +0.28 |        |
|  Diesel Price     | +0.49  -0.54  +0.21  +1.00  +0.51  +0.19 |        |
|  Price Spread     | +0.93  -0.88  +0.65  +0.51  +1.00  +0.44 |        |
|  7D Volatility    | +0.35  -0.38  +0.28  +0.19  +0.44  +1.00 |        |
|                   +------------------------------------------+        |
|                      [ Coolwarm Palette: -1.0 Blue to +1.0 Red ]      |
+-----------------------------------------------------------------------+
```

- **Filename:** `outputs/charts/correlation_heatmap.png`
- **Research Question:** What are the pairwise linear associations across all key variables in the system?
- **Why We Created It:** To provide a comprehensive, single-glance matrix of Pearson correlation coefficients across all modeled indicators.
- **Axes, Units & Variables:**
  - **Rows & Columns:** `KCC Queries`, `Wholesale Price`, `Retail Price`, `Diesel Price`, `Price Spread`, and `7D Volatility`.
  - **Color Scale (`coolwarm`):** Dark blue ($-1.0$, strong inverse) to white ($0.0$, no correlation) to dark red ($+1.0$, strong positive).
  - **Cell Labels:** Numeric Pearson $r$ values rounded to two decimal places.
- **Data Source & Frequency:** Analytical dataset, pairwise clean observations ($N = 180$).
- **Plotting Function:** `app/analysis.py:plot_correlation_heatmap()` (lines 471–490).
- **What a Viewer Should Notice:** Look at the top row (`KCC Queries`): it is deep red with `Price Spread` ($+0.93$), deep blue with `Wholesale Price` ($-0.83$), and moderately red with `Diesel Price` ($+0.49$) and `7D Volatility` ($+0.35$).
- **What Can Reasonably Be Concluded:**
  - Wholesale price and wholesale-retail spread exhibit the strongest linear relationships with farmer call volume.
  - Price volatility and fuel prices show moderate positive associations.
- **What CANNOT Be Concluded:**
  - Does not capture non-linear relationships or multi-day lagged effects.
- **Common Presenter Trap:** Stating that a correlation of $+0.49$ with diesel proves that diesel hikes cause calls. Correlation indicates statistical co-movement, not direct causation.
- **3 Likely Evaluator Questions & Answers:**
  1. *Q: Why is the diagonal equal to 1.00?*
     - *A:* Every variable has a perfect positive correlation with itself.
  2. *Q: Why does the correlation between Queries and Wholesale Price show -0.83 here, but in HYP-A it was -0.11?*
     - *A:* Excellent observation. The heatmap tests price **level** (₹/quintal), which is strongly correlated ($-0.83$). HYP-A tests day-to-day **percentage change** ($\% \Delta W_t$), which has a weak correlation ($-0.11$).
  3. *Q: What does the +0.35 correlation with 7D Volatility tell us?*
     - *A:* It indicates that as market price turbulence increases, farmer inquiries moderately increase as well.
- **Natural Spoken Script (30 Seconds):**
  > *"Figure 7 synthesizes our econometric findings in a correlation heatmap. The top row illustrates associations with farmer call inquiries: we observe a strong positive correlation of +0.93 with the wholesale-retail price spread, and a strong negative correlation of -0.83 with wholesale price levels. Diesel price and rolling volatility also show moderate positive correlations of +0.49 and +0.35, confirming that market turbulence and margin compression co-occur with peak helpline demand."*

---

### Figure 8: `regional_queries.png`

```text
+-----------------------------------------------------------------------+
|             Cumulative Farmer Information Inquiries by State          |
|                                                                       |
|  Maharashtra    | ==============================================      |
|  Punjab         | =========================                           |
|  Uttar Pradesh  | ==================                                  |
|  Madhya Pradesh | =============                                       |
|                 +-----------------------------------------------+     |
|                 0           10,000         20,000        30,000       |
|                                Total Inquiries                        |
+-----------------------------------------------------------------------+
```

- **Filename:** `outputs/charts/regional_queries.png`
- **Research Question:** How is cumulative inquiry demand distributed geographically across states?
- **Why We Created It:** To identify regional operational demand hotspots for call-centre infrastructure planning.
- **Axes, Units & Variables:**
  - **Y-Axis:** State name (e.g., Maharashtra, Punjab, Uttar Pradesh, Madhya Pradesh).
  - **X-Axis:** Total cumulative inquiries logged across the observation period.
  - **Bars:** Horizontal bars styled in an ordered blue palette (`Blues_r`).
- **Data Source & Frequency:** KCC database table, aggregated cumulatively across the sample period.
- **Plotting Function:** `app/analysis.py:plot_regional_comparison()` (lines 453–469).
- **What a Viewer Should Notice:** Maharashtra accounts for the largest share of inquiry volume in this dataset (over 25,000 inquiries).
- **What Can Reasonably Be Concluded:**
  - Helpline operational burden is geographically concentrated in major agricultural and horticultural states.
- **What CANNOT Be Concluded:**
  - Does not mean Maharashtra farmers are more stressed per capita; Maharashtra has a larger agricultural population and more intense horticultural production (e.g., Nashik onion).
- **Common Presenter Trap:** Assuming higher bar means higher farmer distress without acknowledging differences in state population or mobile phone connectivity.
- **3 Likely Evaluator Questions & Answers:**
  1. *Q: Why is this chart useful for administrative decision-makers?*
     - *A:* It determines where to allocate regional language tele-advisors (e.g., Marathi-speaking advisors for Maharashtra) and crop-specific experts.
  2. *Q: How could this metric be normalized for academic research?*
     - *A:* By dividing total queries by the number of operational agricultural landholdings per state to calculate query rate per 1,000 farmers.
  3. *Q: Does the pipeline allow filtering the analysis to a single state?*
     - *A:* Yes, via the `--state Maharashtra` command-line argument.
- **Natural Spoken Script (20 Seconds):**
  > *"Figure 8 provides a geographical overview of cumulative inquiry demand by state. In our dataset, Maharashtra represents the largest operational volume. For administrative planning, this informs the regional allocation of call-centre infrastructure, tele-advisor staffing, and localized Marathi agronomic advisory support."*

---

### Figure 9: `forecast_evaluation.png`

```text
+-----------------------------------------------------------------------+
|      AgriStress Analytics — Time-Series Forecasting & Advisory Stress |
|                                                                       |
|  A. Holdout Validation (Test Split)   B. Future 14-Day Horizon        |
|  200 |    /\                          250 |                           |
|      |   /  \    Actual (Charcoal)        |  --- High Stress (229)    |
|  150 |  /    \   SARIMAX (Blue)       180 |  ... Elevated (179)       |
|      | /      \  Baseline (Grey)          |  === Forecast (Orange)    |
|  100 +----------+                     140 |  [::] 95% Conf Band       |
|       Holdout Dates                        Future 14 Days             |
+-----------------------------------------------------------------------+
```

- **Filename:** `outputs/charts/forecast_evaluation.png`
- **Research Question:** How accurately does our SARIMAX model forecast out-of-sample inquiry demand, and what is the projected operational advisory stress level for the next 14 days?
- **Why We Created It:** The primary technical validation figure combining **out-of-sample holdout validation** (Panel A) with **future horizon operational forecasting** (Panel B).
- **Axes, Units & Variables (2 Side-by-Side Panels):**
  - **Panel A (Left — Holdout Validation):**
    - **X-Axis:** Date across the 30-day holdout test split.
    - **Y-Axis:** Inquiries (Calls/day).
    - **Dark Charcoal Line with Markers:** Actual observed inquiries ($y_{\text{test}}$).
    - **Solid Blue Line:** SARIMAX(1,1,1)(1,1,0)[7] predictions (MAE = 10.5 calls).
    - **Dashed Grey Line:** Seasonal Naive baseline predictions (MAE = 9.8 calls).
  - **Panel B (Right — Future Horizon Forecast & Stress):**
    - **X-Axis:** Date across recent historical 30 days and the future 14-day forecast horizon.
    - **Y-Axis:** Inquiries.
    - **Solid Orange Line:** Future 14-day predicted mean inquiries (~154 calls/day).
    - **Peach Shaded Band:** 95% statistical confidence interval.
    - **Amber Dotted Line:** Elevated Stress Threshold ($\mu + 0.75\sigma = 179.1$ calls).
    - **Red Dashed Line:** High Stress Threshold ($\mu + 1.75\sigma = 229.0$ calls).
- **Data Source & Frequency:** Fitted `SARIMAX` model from `app/forecasting.py`, daily frequency.
- **Plotting Function:** `app/forecasting.py:generate_forecast()` (lines 165–195).
- **What a Viewer Should Notice:**
  - In Panel A, the blue SARIMAX line closely tracks actual inquiry peaks and weekend troughs on unseen test data.
  - In Panel B, the orange forecast stays at ~154 calls, safely below the amber line (179.1), placing future demand in the `NORMAL` stress category.
- **What Can Reasonably Be Concluded:**
  - The model captures weekly seasonal dynamics without future data leakage.
  - Future operational call demand is expected to remain within normal historical capacity limits.
- **What CANNOT Be Concluded:**
  - Does not guarantee zero surprises; an unexpected extreme weather event or sudden policy shift would cause actual calls to diverge from the forecast.
- **Common Presenter Trap:** Claiming that SARIMAX beat the baseline on this holdout set. Be honest: Seasonal Naive achieved an MAE of 9.83 vs SARIMAX's 10.46 on this synthetic split. Explain why SARIMAX is retained (confidence intervals, shock decay).
- **3 Likely Evaluator Questions & Answers:**
  1. *Q: Why did Seasonal Naive have a slightly lower MAE than SARIMAX?*
     - *A:* On synthetic data with deterministic weekly patterns, copying last week's exact same-day observation ($y_{t-7}$) is an exceptionally strong baseline. SARIMAX estimates additional moving-average parameters, introducing slight variance. On real-world data with non-periodic shocks, SARIMAX provides superior flexibility and confidence intervals.
  2. *Q: What does the peach shaded band represent in Panel B?*
     - *A:* The 95% confidence interval derived from statespace forecast error variance. It widens over time to reflect increasing uncertainty.
  3. *Q: How is the stress category determined?*
     - *A:* By comparing the predicted mean against historical standard deviation thresholds: 154 calls is below the elevated threshold of 179.1, categorizing demand as Normal.
- **Natural Spoken Script (35–40 Seconds):**
  > *"Respected panel, Figure 9 is the central exhibit of our forecasting pipeline. Panel A shows out-of-sample holdout validation on 30 days of unseen test data. The blue SARIMAX line closely tracks the charcoal actual line, capturing weekly peaks and weekend troughs with an MAE of approximately 10 calls. Panel B projects future demand 14 days ahead in orange, surrounded by a 95% confidence band. The horizontal dashed lines represent our operational stress thresholds. Because forecasted demand averages 154 calls, it remains below our elevated threshold of 179, categorizing expected operational advisory stress as Normal."*

---

### Figure 10: `actual_vs_predicted.png`

```text
+-----------------------------------------------------------------------+
|         Holdout Validation: Out-of-Sample Actual vs Predicted         |
|                                                                       |
|  220 |           /\                                                   |
|      |          /  \           Actual Observed (Charcoal w/ Circles)  |
|  160 |   /\    /    \    /\    SARIMAX Pred (Blue Solid, MAE=10.5)    |
|      |  /  \  /      \  /  \   Baseline (Grey Dashed, MAE=9.8)        |
|  100 | /    \/        \/    \                                         |
|      +-------------------------------------------------------+        |
|                             Holdout Test Dates                        |
+-----------------------------------------------------------------------+
```

- **Filename:** `outputs/charts/actual_vs_predicted.png`
- **Research Question:** How well do individual daily predictions align with actual observed inquiry numbers during the out-of-sample validation period?
- **Why We Created It:** To provide a dedicated, high-resolution single-focus view of holdout test performance for slide presentations and metric discussions.
- **Axes, Units & Variables:**
  - **X-Axis:** Date across the holdout validation period (30 days).
  - **Y-Axis:** KCC Inquiries (Calls/day).
  - **Charcoal Line with Circles:** Actual observed daily call count.
  - **Solid Blue Line:** SARIMAX model prediction.
  - **Dashed Slate Grey Line:** 7-Day Seasonal Naive baseline prediction.
- **Data Source & Frequency:** Holdout test split (`test`), daily frequency.
- **Plotting Function:** `app/forecasting.py:generate_forecast()` (lines 149–163).
- **What a Viewer Should Notice:** Notice how accurately the blue curve captures the steep Sunday drops and the subsequent Monday-Tuesday rebounds on completely unseen data.
- **What Can Reasonably Be Concluded:**
  - Out-of-sample error is low (MAPE $\approx 7.3\%$).
  - The model does not suffer from lookahead bias or future data leakage.
- **What CANNOT Be Concluded:**
  - Does not prove that the model will maintain this exact accuracy 6 months into the future without periodic retraining.
- **Common Presenter Trap:** Assuming holdout testing is the same as training accuracy. Emphasize that these points were completely withheld during model fitting.
- **3 Likely Evaluator Questions & Answers:**
  1. *Q: How was this test split created?*
     - *A:* Using a chronological split: the last 30 days were completely withheld while fitting the model on the preceding 150 days.
  2. *Q: What is the zero-safe MAPE on this test split?*
     - *A:* 7.32%, indicating that average forecast error is approximately 7% of actual call volume.
  3. *Q: Why is holdout validation superior to in-sample R-squared?*
     - *A:* In time series, in-sample $R^2$ can easily be inflated by overfitting to past noise. Evaluating on unseen future data is the only true test of forecasting validity.
- **Natural Spoken Script (25 Seconds):**
  > *"Finally, Figure 10 provides a detailed view of our holdout validation window. The charcoal markers represent actual observed inquiries, while the solid blue line shows SARIMAX predictions. Notice how closely the model tracks turning points and weekly troughs on completely unseen data, achieving a zero-safe mean absolute percentage error of just 7.3%, proving that our pipeline generalizes effectively to future periods."*
