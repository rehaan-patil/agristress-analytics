# Data Sources and Empirical Specification

This document details the primary data sources targeted for the AgriStress Analytics project, their empirical characteristics, schema requirements, geographic resolutions, temporal frequencies, and documented limitations.

---

## 1. Kisan Call Centre (KCC) Query Influx

- **Source Name:** Kisan Call Centre Data Portal / Open Government Data (OGD) Platform India
- **URL:** [https://www.data.gov.in/](https://www.data.gov.in/)
- **Publisher:** Department of Agriculture & Farmers Welfare, Government of India
- **Access / Licensing:** Government Open Data License - India (GODL)
- **Target Schema & Columns:**
  - `observation_date` (Date, `YYYY-MM-DD`): Date on which queries were logged.
  - `state` (String): State or Union Territory name (e.g., "Maharashtra", "Punjab").
  - `district` (String, Optional): District name when granular logs are available.
  - `query_type` (String, Optional): Category of inquiry (e.g., "Weather", "Plant Protection", "Market Information", "Fertilizer").
  - `query_count` (Integer): Total incoming calls / advisory requests for that day and region.
- **Observation Frequency:** Daily logging, with aggregated reporting available weekly or monthly.
- **Geographic Coverage:** National, State-level, and selected District-level centers.
- **Known Data Limitations:**
  - Publicly accessible releases on OGD are often partitioned by month or state rather than unified streaming feeds.
  - In some periods, call logs reflect answered calls rather than total attempted calls (unmet demand cannot be directly observed from answered call metrics).
  - Sundays and national holidays frequently show zero or minimal query volume due to shift scheduling, creating artificial intra-week seasonality.

---

## 2. Agricultural Commodity Prices and Mandi Arrivals

- **Source Name:** Agricultural Marketing Information Network (Agmarknet)
- **URL:** [https://agmarknet.gov.in/](https://agmarknet.gov.in/)
- **Publisher:** Directorate of Marketing & Inspection (DMI), Ministry of Agriculture & Farmers Welfare
- **Access / Licensing:** Public Domain / Indian Agricultural Research Information
- **Target Schema & Columns:**
  - `observation_date` (Date, `YYYY-MM-DD`): Market transaction date.
  - `state` (String): State where APMC Mandi is located.
  - `district` (String, Optional): Mandi district.
  - `market` (String, Optional): APMC Mandi name (e.g., "Lasalgaon", "Nashik", "Khanna").
  - `commodity` (String): Commodity name (e.g., "Onion", "Wheat", "Tomato", "Cotton").
  - `wholesale_price` (Float): Modal wholesale trading price in INR per Quintal (100 kg).
  - `arrival_quantity` (Float, Optional): Physical arrivals at market in metric tonnes or quintals.
- **Observation Frequency:** Daily (Monday through Saturday; closed on Mandi holidays).
- **Geographic Coverage:** Mandi-level across registered APMCs in India.
- **Known Data Limitations:**
  - Agmarknet primarily records **wholesale** mandi prices. Retail prices are monitored separately by the Department of Consumer Affairs (Price Monitoring Cell) for only 22 essential commodities.
  - Wholesale-to-retail price spreads can only be computed when matched retail observations for the same commodity, quality, date, and consumption center exist.
  - Missing records occur on local festival holidays and non-trading days.

---

## 3. Fuel and Diesel Price Statistics

- **Source Name:** Petroleum Planning & Analysis Cell (PPAC)
- **URL:** [https://ppac.gov.in/](https://ppac.gov.in/)
- **Publisher:** Ministry of Petroleum and Natural Gas, Government of India
- **Access / Licensing:** Official Government Statistics (Public Access)
- **Target Schema & Columns:**
  - `observation_date` (Date, `YYYY-MM-DD`): Price observation date.
  - `state` (String, Optional): State / Union Territory or metro region.
  - `diesel_price` (Float): Retail Selling Price (RSP) of High Speed Diesel (HSD) in INR per Litre.
  - `currency` (String): Indian Rupee (`INR`).
- **Observation Frequency:** Daily retail price tracking (revised at 06:00 AM daily by Oil Marketing Companies).
- **Geographic Coverage:** State capitals and major consumption hubs (Delhi, Mumbai, Kolkata, Chennai, state headquarter districts).
- **Known Data Limitations:**
  - Fuel prices are monitored at metro or state levels, not for individual rural revenue blocks.
  - Merging diesel prices with district-level mandi records requires state-level broadcast alignment to avoid invalid one-to-one geographic assumptions.

---

## 4. Synthetic Development Dataset Policy

When live API access keys or massive multi-gigabyte historical dumps are unavailable during offline development or viva demonstration:
1. Synthetic datasets are generated using a deterministic random seed (`seed = 42`) in `scripts/generate_demo_data.py`.
2. All synthetic data files are explicitly stored under `data/synthetic/` and prefixed with `synthetic_`.
3. The application explicitly flags synthetic data in reports, API outputs, and database logs.
4. Synthetic patterns are realistic in seasonality and distribution (e.g., harvesting price dips, monsoon advisory spikes) but are **strictly pedagogical** and do not represent empirical verification of economic hypotheses.
