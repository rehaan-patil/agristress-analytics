# Farmer-Friendly Recommendation Engine — Architecture & Guide

**Module:** `app/recommendations.py`  
**Purpose:** Translates econometric analytics and time-series forecasts into clear, understandable, and actionable market guidance for ordinary farmers in plain English.  
**Audience:** Farmers, agricultural extension officers, and academic viva voce evaluators.

---

## 1. Core Philosophy: Conclusions, Not Mathematics

Technical researchers require $p$-values, Spearman correlation coefficients, Seasonal Naive benchmarks, and SARIMAX error metrics. Farmers, however, need clear answers to practical everyday questions:

1. **What is happening?** (Is the mandi price rising or falling? Has diesel increased? Is call center traffic heavy?)
2. **What does this mean for me?** (Will I get lower returns? Will hired transport cost more? Are lines busy?)
3. **What should I do next?** (Specific, realistic actions: compare nearby mandis, check MSP centres, verify freight quotes, dial KCC early).
4. **Who can I contact for help?** (Kisan Call Centre Toll-Free `1800-180-1551`, Gram Panchayat Krishi Sahayak, or nearest Krishi Vigyan Kendra).

### Jargon Elimination Table

| Technical Indicator | Internal Analytical Meaning | Plain-English Farmer Translation |
| :--- | :--- | :--- |
| **$p < 0.05$ on HYP-A** | Rejection of null hypothesis on price percentage changes vs KCC volume | *"Mandi prices have declined noticeably over recent weeks. Checking local rates before loading produce helps avoid taking lower returns."* |
| **Wholesale-Retail Spread Expansion** | Spread widens by $>20\%$ ($>Rs\ 500/Qtl$) | *"City consumers are currently paying substantially more than what farmers receive at the mandi gate. Consider collective marketing through an FPO or local farmers' market."* |
| **Diesel Shock ($> 1.0\%$)** | Intermittent fuel revision shock detected | *"Retail diesel fuel prices have increased recently. Confirm your vehicle hiring quote before traveling to distant mandis."* |
| **SARIMAX Demand Influx ($>1.75\ \sigma$)**| Advisory stress classified as `HIGH` | *"Our demand model projects unusually high farmer inquiry volume in this region. Call Kisan Call Centre early in the morning (7:00 AM – 9:00 AM) to connect faster."* |

---

## 2. Decision Logic & Rule Catalog

The engine implements deterministic, reproducible intermediate-level Python logic without external language models, third-party AI APIs, or black-box classifiers.

### Rule 1: Commodity Price Trajectory (Window: 7 Observed Days)
- **Falling Trend ($\le -5.0\%$):**
  - Explains the drop in rupees per quintal.
  - Warns against rushing to sell at the first available market.
  - Suggests comparing 2–3 nearby APMC yards and checking government MSP procurement centres.
  - For non-perishable crops (e.g., dry onions or grains), suggests evaluating safe storage feasibility.
- **Rising Trend ($\ge +5.0\%$):**
  - Explains the price improvement.
  - Cautions that sharp price rises attract heavy incoming arrivals, which can soften spot prices by afternoon.
  - Suggests confirming morning arrivals and grading lots to secure the top price band.
- **Stable Trend (within $\pm 5.0\%$):**
  - Confirms steady market conditions.
  - Recommends following standard harvesting and dispatch schedules.
- **Data Absent:**
  - Omitted cleanly with a note that mandi price data was not included.

### Rule 2: Wholesale-to-Retail Margin Spread
- **Wide Spread (Spread $> Rs\ 500/Qtl$ AND $> 1.20 \times$ historical mean):**
  - Clarifies that a wide spread does not automatically mean higher profit for the farmer.
  - Suggests exploring direct-to-consumer alternatives (e.g., weekly Shetkari/Apni mandis) or Farmer Producer Organizations (FPOs).
- **Typical Spread:**
  - Explains margins align with normal transportation and retail handling costs.
- **Retail Data Absent:**
  - Omitted cleanly without inventing synthetic consumer prices.

### Rule 3: Diesel Fuel & Transport Expense
- **Recent Fuel Increase ($\ge 1.0\%$ or recent shock):**
  - Notes that hired tractor/truck freight rates are likely to increase.
  - Recommends securing firm transport quotes before choosing between local and distant markets.
  - Suggests pooling loads with neighbouring farmers.
- **Stable Fuel:**
  - Confirms diesel prices have not experienced sudden changes.

### Rule 4: Advisory Call Centre Load
- **HIGH Stress:**
  - Warns of busy phone lines and suggests calling early morning (7:00 AM – 9:00 AM) or contacting local Krishi Sahayaks.
- **ELEVATED Stress:**
  - Advises contacting KCC ahead of scheduled field operations.
- **NORMAL Stress:**
  - Informs that toll-free helpline lines are operating normally.

### Rule 5: Combined Market Conditions Alert
- If commodity prices are **FALLING** while diesel costs are **INCREASING**:
  - Triggers a prominent **Special Caution Alert**:
    *"Do NOT dispatch produce to distant city mandis without confirming in advance that the price difference easily covers higher transport freight charges."*

---

## 3. Strict Boundary: What We Do NOT Prescribe

The recommendation engine strictly adheres to safe, evidence-based boundaries:

1. **No Chemical or Fertilizer Prescriptions:** The system analyzes economic and inquiry data, not plant tissue or soil chemistry. It does **not** prescribe pesticide dosages, fungicide brands, or fertilizer quantities. Farmers needing pest/disease guidance are referred directly to qualified KVK agronomists or KCC (`1800-180-1551`).
2. **No Rigid "Sell Now / Hold" Commands:** Individual selling decisions depend on perishable shelf-life, on-farm storage, household debt, and liquidity constraints. The system provides market awareness, not financial mandates.
3. **No Fabricated Data:** If fuel or retail data is missing, the corresponding section is skipped rather than simulated.

---

## 4. Generated Artifacts

On every pipeline run, two complementary advisory documents are generated in `outputs/reports/`:

| Artifact | Format | Purpose |
| :--- | :--- | :--- |
| **`outputs/reports/farmer_advisory.md`** | Markdown | Formatted document with headers, alerts, and detailed explanations for computer screens or extension offices. |
| **`outputs/reports/farmer_advisory.txt`** | Plain Text | Clean, lightweight text format ready for SMS broadcast, WhatsApp distribution, or printing. |
| **Terminal Summary** | Console Output | Concise 8-line executive summary displayed directly at the end of `python main.py`. |

---

## 5. College Viva Defense Cheatsheet

1. **Why not use ChatGPT or an LLM to generate recommendations?**
   - *Answer:* LLMs can hallucinate agricultural recommendations, invent chemical recipes, or introduce non-reproducible answers. Our rule-based engine is 100% deterministic, auditable, and grounded strictly in the verified numbers of the current dataset.
2. **How are the thresholds determined?**
   - *Answer:* We use standard agricultural operational thresholds ($\pm 5\%$ for short-term wholesale price direction, $+1.0\%$ for diesel revisions, and $>1.75$ standard deviations for High advisory stress), which can be tuned in `app/recommendations.py`.
3. **How does the system distinguish synthetic demo data from real operational data?**
   - *Answer:* In Section 4 ("How Certain is This Information?"), the report explicitly flags synthetic demonstration provenance so testing data is never mistaken for real financial advice.
