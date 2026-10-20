# Farmer Decision-Support Advisory Engine — Architecture, Rules & Trust Guidelines

**Module:** `app/recommendations.py`  
**Purpose:** Translates econometric analytics and time-series forecasts into transparent, trustworthy, and actionable decision support for ordinary farmers and agricultural extension officers.  
**Audience:** Farmers, Farmer Producer Organizations (FPOs), Krishi Vigyan Kendra (KVK) extension officers, and academic viva voce evaluators.

---

## 1. Core Principles: Actionable Decision Support & Farmer Comprehension

Agricultural econometric models produce technical diagnostics—$p$-values, Pearson/Spearman correlation coefficients, Seasonal Naive benchmarks, and SARIMAX error metrics. While vital for research validation, these metrics do not answer a farmer's practical questions:

1. **What has changed?** (State the important observation in familiar language using actual computed numbers and dates).
2. **What does it mean for my decision?** (Explain practical market implications without exaggeration or alarming language).
3. **What should I do next?** (Provide concrete, reasonable actions directly connected to available empirical evidence).
4. **What should I check before acting?** (Identify missing information, transportation quotes, crop perishability, and safe storage).
5. **Where can I get verified help?** (Provide verified official channels: Kisan Call Centre Toll-Free `1800-180-1551`).

### Jargon Elimination & Translation Matrix

| Technical Metric | Internal Analytical Meaning | Farmer-Facing Plain Translation |
| :--- | :--- | :--- |
| **Commodity Price Window ($\Delta \% \le -5.0\%$)** | Negative 7-day average percentage change | *"Recorded wholesale onion prices dropped by 12% over the latest 7-day period (from ₹2,200 to ₹1,936/qtl). Before dispatching, confirm today's spot rate and arrival volume at the specific mandi you plan to visit."* |
| **Wholesale-Retail Spread Expansion** | Spread widens by $>20\%$ and $>₹500/\text{qtl}$ | *"City consumers are paying substantially more than mandi wholesale rates. This spread covers transport, packaging, storage loss, and retail overheads; it does not indicate higher farmer profit. Consider collective selling through an FPO."* |
| **Fuel Inflation Shock ($\ge 1.0\%$)** | Retail diesel revision detected | *"Retail diesel prices have increased recently. Tractor and truck operators often raise freight quotes. Obtain a firm hiring quote in advance and consider pooling loads with neighbours."* |
| **SARIMAX Demand Influx ($>1.75\ \sigma$)** | Advisory query stress classified as `HIGH` | *"A higher volume of farmer inquiries is anticipated in this region. Advisory phone lines may experience heavier mid-day traffic. Contact KCC at 1800-180-1551 (6:00 AM to 10:00 PM) for localized advice."* |

---

## 2. Recommendation Priority & Explainable Uncertainty

The advisory implements three explainable priority categories based on verified data recency and market movement:

1. **Action to consider now:**
   - Triggered when sufficiently recent observations (within 7 days of analysis date) show significant price movement ($\ge \pm 5.0\%$) or fuel inflation.
   - Represents an immediate, empirical next step (e.g. verifying today's spot rate or securing freight quotes).
2. **Check before deciding:**
   - Triggered when observations show potential concern (e.g., wide price spread, elevated query influx) OR when market movement is observed in historical/older datasets (> 7 days old).
   - Informs the farmer that baseline data is informative, but local spot conditions must be confirmed before taking action.
3. **No clear signal:**
   - Triggered when prices, fuel rates, and inquiry volumes remain steady within normal historical parameters.
   - Advises following customary harvesting schedules without unneeded market disruption.

---

## 3. APMC Market Comparison Table (Empirical, Not Fabricated)

When the dataset contains records from multiple distinct APMC mandis (e.g. Pimpalgaon, Lasalgaon, Pune, Varanasi, Indore):
- A structured comparison table is generated comparing each mandi's latest available price against the group average:

| Market (APMC) | Location | Latest Price (₹/Quintal) | As Of Date | Difference vs Avg (₹/Quintal) |
| :--- | :--- | :--- | :--- | :--- |
| Indore Mandi | Indore | ₹2,568 | 2025-12-30 | +₹29 |
| Pimpalgaon | Nashik | ₹2,512 | 2025-12-30 | -₹27 |

- **Explicit Transportation Caution:** Every table is accompanied by a mandatory caveat:
  > *"Differences reflect gross mandi quotes. They do not account for transport freight, octroi/toll, or transit shrinkage. A higher quoted price at a distant market may not yield higher profit after deducting freight."*

- **Single Market / State Aggregate Safeguard:** If only 1 market or state-level averages exist, the engine does **not** invent nearby mandis. It clearly states:
  > *"Market-level comparison across neighbouring mandis is not available in this dataset. The figures represent regional or state-level aggregates. Local APMC records are required before deciding between mandis."*

---

## 4. Input Provenance & Data Quality Categories

To preserve academic integrity and research safety, data provenance is strictly segregated into three distinct categories:

1. **`SYNTHETIC` — Synthetic Demonstration Data:**
   - Generated deterministically by `scripts/generate_demo_data.py` for testing and development.
   - Explicitly flagged in both Markdown and text reports:
     *"Notice: These figures reflect synthetic demonstration data created for offline testing. They illustrate analytical methods and should not be used for real-world financial commitments."*
2. **`VERIFIED_REAL` — Verified Real-World Observations:**
   - Imported from verified government open portals (e.g. Agmarknet, data.gov.in) with `--verified-real` flag.
3. **`UNVERIFIED` — Unverified / User-Supplied Data:**
   - Custom CSV files supplied by users without external API verification.
   - Strictly labeled: *"Unverified / User-Supplied Data (provided via local CSV without independent verification)."* Never misclassified as "Real".

---

## 5. What We Do NOT Prescribe (Safety Boundaries)

1. **No Chemical or Fertilizer Prescriptions:** The system analyzes economic and inquiry time series, not plant soil or leaf tissue. It strictly never prescribes chemical pesticide dosages, fungicide brands, or fertilizer rates. Farmers needing crop protection are referred to qualified agronomists at Krishi Vigyan Kendras (KVKs).
2. **No Rigid "Sell Now / Hold" Commands:** Individual selling choices depend on crop perishability, moisture content, debt obligations, on-farm storage, and household cash needs. The tool provides decision support, not universal commands.
3. **No Fabricated Costs or Distance Numbers:** We do not claim diesel hikes added "₹45 per quintal" unless the farmer's vehicle type, mileage, distance, and load size are provided.
4. **No Unverified Call Timing Claims:** We remove unverified claims such as "call early morning between 7-9 AM for faster connection". We cite official Government of India operational hours (6:00 AM to 10:00 PM, all 7 days of the week).

---

## 6. Verified Government Support Contacts

Official Government of India details verified against official portals (`mkisan.gov.in`, `dackkms.gov.in`):

- **Helpline:** Kisan Call Centre (KCC)
- **Toll-Free Number:** `1800-180-1551`
- **Operating Hours:** `6:00 AM to 10:00 PM`, all 7 days of the week (365 days a year).
- **In-Person Extension:** Gram Panchayat Krishi Sahayak (Kisan Salahkar) and nearest ICAR Krishi Vigyan Kendra (KVK).
- **Verification Date:** October 2026.

---

## 7. Multilingual Support (English, Hindi, Marathi)

The advisory engine supports transparent multilingual reporting without external AI or translation API dependencies:

- **English (`en`):** Default baseline (`outputs/reports/farmer_advisory.md` & `outputs/reports/farmer_advisory.txt`).
- **Hindi (`hi`):** Flag `--lang hi`. Generates `farmer_advisory_hi.md` and `farmer_advisory_hi.txt` using reviewed terminology (`किसान बाज़ार एवं सूचना सलाह`).
- **Marathi (`mr`):** Flag `--lang mr`. Generates `farmer_advisory_mr.md` and `farmer_advisory_mr.txt` using reviewed terminology (`शेतकरी बाज़ार व माहिती सल्ला`).

---

## 8. CLI Usage Examples

```powershell
# 1. Run pipeline on default synthetic demonstration data
python main.py --generate-data

# 2. Run pipeline for Maharashtra Onion with 21-day forecast horizon
python main.py --state Maharashtra --commodity Onion --horizon 21

# 3. Run pipeline on user-supplied CSV files (properly tagged as Unverified)
python main.py --kcc data/my_kcc.csv --commodity-file data/my_commodity.csv --fuel data/my_fuel.csv --replace

# 4. Generate advisory in Hindi
python main.py --lang hi

# 5. Generate advisory in Marathi
python main.py --lang mr
```
