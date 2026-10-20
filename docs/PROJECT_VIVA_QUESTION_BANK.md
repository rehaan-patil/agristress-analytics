# AgriStress Analytics — Comprehensive Viva Voce Question Bank (100+ Questions)

> **Document Purpose:** Complete, categorized examination and technical review defense guide.  
> **Target Audience:** First-Year Engineering Students defending AgriStress Analytics before college professors, external examiners, and technical evaluators.  
> **Student Voice:** Natural, confident, technically precise, and grounded in actual code, formulas, outputs, and limitations.

---

## Category 1: Project Introduction & Problem Statement

### Q1. What is AgriStress Analytics in simple words?
- **Suggested Answer:** "AgriStress Analytics is an offline Python application that studies how agricultural market pressures—like crashing crop prices, wide wholesale-retail margins, and diesel price hikes—drive farmers to call government helplines like the Kisan Call Centre. We clean and align the data, test economic hypotheses, forecast call volume 14 days ahead using SARIMAX time-series models to predict call centre stress, and translate these findings into simple, actionable advisories for farmers in English, Hindi, and Marathi."
- **Technical Justification:** Implemented in `main.py`, `run_pipeline.py`, `app/forecasting.py`, and `app/recommendations.py`.
- **Likely Follow-up:** *Is it a live web application?*
  - **Short Answer:** "No, it is an offline, reproducible research and decision-support pipeline designed for local execution without web server dependencies."

### Q2. What exact problem does your project solve for call centre administrators?
- **Suggested Answer:** "Helpline administrators typically operate reactively, getting overwhelmed after market crises occur. Our project provides a 14-day advance forecast of inquiry volume and classifies expected operational load into Normal, Elevated, or High stress, allowing administrators to allocate tele-advisors proactively."
- **Technical Justification:** `app/forecasting.py:classify_advisory_stress()` calculates cutoffs at $\mu + 0.75\sigma$ and $\mu + 1.75\sigma$.
- **Likely Follow-up:** *How do you define 'stress' mathematically?*
  - **Short Answer:** "It is a quantitative proxy: forecasted mean calls exceeding historical baseline mean plus standard deviation thresholds."

### Q3. What problem does it solve for smallholder farmers?
- **Suggested Answer:** "Farmers often face sudden price crashes and lack transparent information on whether to sell immediately or store, how to account for transport costs, or what other mandis are paying. Our recommendation engine provides clear, plain-language guidance on these decisions without confusing technical jargon."
- **Technical Justification:** `app/recommendations.py:generate_farmer_recommendations()` outputs Markdown and text advisories.
- **Likely Follow-up:** *Do you tell the farmer exact pesticide chemicals to buy?*
  - **Short Answer:** "No, we strictly avoid chemical prescriptions and refer farmers to verified KVK agronomists and toll-free helpline 1800-180-1551."

### Q4. Why is studying farmer call inquiries valuable?
- **Suggested Answer:** "Call inquiries provide high-frequency, real-time indicators of grassroots farmer concerns. Unlike delayed annual yield surveys, daily helpline call volumes reflect immediate problems like pest outbreaks, price collapses, or diesel inflation shocks."
- **Technical Justification:** KCC inquiry data records date, state, query type, and daily call counts in `kcc_observations`.
- **Likely Follow-up:** *Are call volumes representative of all farmers?*
  - **Short Answer:** "They represent farmers with mobile phone access who know the toll-free number, which is a useful proxy but not a complete census."

### Q5. What is the difference between your project's technical report and farmer advisory?
- **Suggested Answer:** "The technical report (`summary_report.md`) is for economists and engineers, containing p-values, correlations, MAE, and SARIMAX parameters. The farmer advisory (`farmer_advisory.md`) strips away all jargon and gives practical steps on freight costs, storage checks, and verified helpline numbers."
- **Technical Justification:** Separate generation in `app/analysis.py` (line 530) vs `app/recommendations.py` (line 224).
- **Likely Follow-up:** *Why not just give farmers the charts?*
  - **Short Answer:** "Most farmers cannot make immediate marketing decisions from dual-axis plots or heatmap matrices; they need clear, actionable steps."

---

## Category 2: Research Motivation & Domain Understanding

### Q6. Why did you choose commodity prices, retail spreads, and diesel prices as your predictors?
- **Suggested Answer:** "These represent the three primary financial pressures on farmers: wholesale price dictates gross revenue; the wholesale-retail spread reflects intermediary margin extraction; and diesel price represents immediate variable operational cost for tractors and transport."
- **Technical Justification:** Extracted and aligned in `app/data_processing.py:build_analytical_dataset()`.
- **Likely Follow-up:** *What about weather data like rainfall?*
  - **Short Answer:** "Weather is a crucial driver. We included weather as a KCC query category, but focused our econometric model on price and fuel shocks as our core research scope."

### Q7. What is an APMC Mandi?
- **Suggested Answer:** "An Agricultural Produce Market Committee (APMC) is a state-regulated wholesale physical market yard in India where farmers bring harvest to sell via open auction to licensed traders."
- **Technical Justification:** Handled in `CommodityObservation` model with fields `market`, `wholesale_price`, and `arrival_quantity`.
- **Likely Follow-up:** *Why do mandi prices vary between districts?*
  - **Short Answer:** "Due to localized harvest arrival volumes, transport distance to urban consumption centres, and local trader bidding competition."

### Q8. What does "wholesale-to-retail price spread" mean economically?
- **Suggested Answer:** "It is the difference between what urban consumers pay in retail shops and what farmers receive at the wholesale mandi ($R_t - W_t$). A wide spread indicates that supply chain intermediaries, transport, and retailers capture most of the crop's final value."
- **Technical Justification:** Formula `df['retail_price'] - df['wholesale_price']` in `app/data_processing.py` line 482.
- **Likely Follow-up:** *Does a widening spread always mean trader exploitation?*
  - **Short Answer:** "Not necessarily; it can also reflect rising transportation costs, packaging expenses, or spoilage during transit."

### Q9. Why are diesel prices relevant to agricultural inquiries?
- **Suggested Answer:** "Diesel powers tractor tillage, irrigation pump sets, harvest combines, and freight trucks. When diesel prices jump, farmers' variable operating costs rise immediately, prompting inquiries about fuel subsidies, government support, or alternative marketing options."
- **Technical Justification:** Modeled as `diesel_price`, `diesel_pct_change`, and lagged changes in `app/data_processing.py`.
- **Likely Follow-up:** *Are diesel prices market-driven in India?*
  - **Short Answer:** "They are set by oil marketing companies under administered pricing guidelines, leading to infrequent step-wise revisions."

### Q10. What is the Kisan Call Centre network?
- **Suggested Answer:** "It is a government toll-free agricultural advisory service (`1800-180-1551`) operating across India from 6:00 AM to 10:00 PM every day, answering queries in local languages on crop management, pests, weather, and market prices."
- **Technical Justification:** Documented and verified in `app/recommendations.py:VERIFIED_ASSISTANCE`.
- **Likely Follow-up:** *How do you verify this toll-free number?*
  - **Short Answer:** "It is the official toll-free helpline published by the Department of Agriculture & Farmers Welfare on `mkisan.gov.in`."

---

## Category 3: Architecture & Pipeline Execution

### Q11. Can you trace the execution flow when you run `python main.py`?
- **Suggested Answer:** "Yes. Execution starts in `main.py`, which sets UTF-8 console encoding and calls `run_pipeline.py:main()`. The pipeline runs 6 sequential phases: Phase 1 initializes SQLite tables and imports CSV data; Phase 2 builds and harmonizes the continuous daily time-series with forward-fill imputation; Phase 3 computes descriptive stats and saves CSV tables; Phase 4 generates 8 exploratory PNG charts and runs hypothesis tests; Phase 5 fits SARIMAX and Seasonal Naive models, saves evaluation charts, and writes the summary report; and Phase 6 generates multilingual farmer advisories in English, Hindi, and Marathi."
- **Technical Justification:** Detailed in `run_pipeline.py:run_full_pipeline()` lines 50–263.
- **Likely Follow-up:** *How long does the entire pipeline take to run?*
  - **Short Answer:** "Typically between 5 and 10 seconds on a standard student laptop."

### Q12. Why did you remove FastAPI and not build a web interface?
- **Suggested Answer:** "Our mentor and project scope required pure Python data logic. Web frameworks like FastAPI or Streamlit introduce networking dependencies, port conflicts, browser issues, and UI bloat without adding any statistical value. A clean CLI script ensures 100% reproducibility and instant offline execution."
- **Technical Justification:** `requirements.txt` contains only scientific libraries; all FastAPI code was cleanly removed.
- **Likely Follow-up:** *How does a non-technical person see your results?*
  - **Short Answer:** "They read the formatted terminal output banner and the plain-text/Markdown advisory files generated in `outputs/reports/`."

### Q13. How are command-line arguments handled in the pipeline?
- **Suggested Answer:** "We use Python's built-in `argparse` module in `run_pipeline.py`. It parses flags like `--generate-data`, `--kcc`, `--commodity-file`, `--fuel`, `--replace`, `--state`, `--commodity`, `--horizon`, and `--lang`, passing them as typed arguments to `run_full_pipeline()`."
- **Technical Justification:** Configured in `run_pipeline.py:main()` lines 266–314.
- **Likely Follow-up:** *What happens if a user passes a non-existent CSV path?*
  - **Short Answer:** "`import_*_csv()` catches the file error, logs a failure message in `import_history`, and aborts gracefully without crashing."

### Q14. What are the directories inside `outputs/` and what goes into each?
- **Suggested Answer:** "We have 4 dedicated output folders: `outputs/charts/` stores 10 generated PNG visualization figures; `outputs/tables/` stores 4 statistical CSV tables; `outputs/forecasts/` stores predictions and evaluation metrics CSVs; and `outputs/reports/` stores technical and multilingual farmer advisory reports."
- **Technical Justification:** Configured in `app/config.py` lines 24–31.
- **Likely Follow-up:** *Are these folders created automatically?*
  - **Short Answer:** "Yes, `app/config.py` creates them on module load via `mkdir(parents=True, exist_ok=True)`."

### Q15. How does your pipeline ensure that old results do not mix with new runs?
- **Suggested Answer:** "Whenever charts or reports are generated, files are overwritten in place with fresh timestamps. In the database, passing `--replace` clears existing table records before inserting new observations."
- **Technical Justification:** Table deletion via `db.query(Model).delete()` in `app/data_processing.py` when `replace=True`.
- **Likely Follow-up:** *What if I want to keep a history of past imports?*
  - **Short Answer:** "The `import_history` and `forecast_history` tables maintain persistent historical logs across all runs."

---

## Category 4: Source Files & Code Logic

### Q16. What is the role of `app/config.py`?
- **Suggested Answer:** "It centralizes project paths (`BASE_DIR`, `DATA_DIR`, `OUTPUTS_DIR`, `TABLES_DIR`, `FORECASTS_DIR`), loads `.env` variables via `python-dotenv`, ensures essential directories exist, and configures the SQLite database URL."
- **Technical Justification:** `app/config.py` lines 1–32.
- **Likely Follow-up:** *Can the database URL be overridden?*
  - **Short Answer:** "Yes, via the `DATABASE_URL` environment variable."

### Q17. What does `app/database.py` do?
- **Suggested Answer:** "It initializes the SQLAlchemy engine with `check_same_thread: False` for SQLite compatibility, creates `SessionLocal`, defines declarative `Base`, and provides the `get_db()` context generator."
- **Technical Justification:** `app/database.py` lines 1–30.
- **Likely Follow-up:** *Why is `check_same_thread: False` needed for SQLite?*
  - **Short Answer:** "SQLite by default prevents objects created in one thread from being shared with another; disabling it prevents threading exceptions during pipeline execution."

### Q18. What are the database models defined in `app/models.py`?
- **Suggested Answer:** "There are 5 models: `KCCObservation` for inquiry calls, `CommodityObservation` for mandi wholesale/retail prices and arrivals, `FuelObservation` for diesel rates, `ImportHistory` for tracking CSV imports, and `ForecastHistory` for logging forecast runs and stress categories."
- **Technical Justification:** `app/models.py` lines 10–157.
- **Likely Follow-up:** *Which table has the most columns?*
  - **Short Answer:** "`CommodityObservation` with 11 columns, including market, district, commodity, wholesale/retail prices, and arrival quantity."

### Q19. What is the most critical function in `app/data_processing.py`?
- **Suggested Answer:** "`build_analytical_dataset()`. It queries separate tables, computes daily aggregates, performs date-based left joins, reindexes onto a continuous 365-day calendar grid, applies forward-fill price imputation, and calculates all engineered features."
- **Technical Justification:** `app/data_processing.py` lines 394–502.
- **Likely Follow-up:** *Why is reindexing necessary?*
  - **Short Answer:** "Because time-series models require an unbroken frequency ('D') without missing calendar dates."

### Q20. What is the role of `app/analysis.py`?
- **Suggested Answer:** "It computes descriptive statistics, calculates Pearson and Spearman correlations, executes formal hypothesis tests for HYP-A, HYP-B, and HYP-C, renders 8 Matplotlib/Seaborn charts, and compiles the comprehensive research summary report."
- **Technical Justification:** `app/analysis.py` lines 1–746.
- **Likely Follow-up:** *What Matplotlib backend does it use?*
  - **Short Answer:** "`matplotlib.use('Agg')` for headless file generation without a GUI window."

### Q21. What does `app/forecasting.py` do?
- **Suggested Answer:** "It performs chronological holdout splitting, fits a 7-day Seasonal Naive baseline, fits a `SARIMAX(1,1,1)(1,1,0)[7]` model, evaluates MAE, RMSE, and MAPE, forecasts future 14-day demand with 95% confidence intervals, and classifies advisory stress."
- **Technical Justification:** `app/forecasting.py` lines 1–259.
- **Likely Follow-up:** *What happens if data has fewer than 30 rows?*
  - **Short Answer:** "It aborts fitting and returns an 'Insufficient data' status with zeroed metrics."

### Q22. What does `app/recommendations.py` do?
- **Suggested Answer:** "It inspects the analytical state, evaluates price drops and call surges, checks data freshness, and generates plain-language, evidence-backed advisories in English, Hindi, and Marathi, with transport cost checks and verified toll-free helplines."
- **Technical Justification:** `app/recommendations.py` lines 1–1302.
- **Likely Follow-up:** *How is Hindi and Marathi text generated?*
  - **Short Answer:** "Using deterministic localized template dictionaries in `UI_STRINGS` to prevent translation hallucinations."

---

## Category 5: Data Sources, Schemas & Ingestion

### Q23. What are the required columns for importing a KCC CSV?
- **Suggested Answer:** "The required columns are `observation_date` and `state`. If `query_count` is missing, each row defaults to 1 call (treating the file as a raw call log) and groups them by date."
- **Technical Justification:** `app/data_processing.py:import_kcc_csv()` lines 117–130.
- **Likely Follow-up:** *What if the date column is named 'call_date'?*
  - **Short Answer:** "`COLUMN_SYNONYMS` maps `call_date` to `observation_date` automatically."

### Q24. What are the required columns for a commodity price CSV?
- **Suggested Answer:** "`observation_date`, `state`, `commodity`, and `wholesale_price`. Optional columns include `district`, `market`, `retail_price`, and `arrival_quantity`."
- **Technical Justification:** `app/data_processing.py:import_commodity_csv()` lines 187–198.
- **Likely Follow-up:** *What if wholesale price is 0 or negative?*
  - **Short Answer:** "It is treated as invalid and filtered out during the cleaning stage."

### Q25. How do you handle duplicate rows during import?
- **Suggested Answer:** "For KCC, we deduplicate by date, state, district, and query type. For commodity data, we deduplicate by date, state, commodity, and market. Preserving the market column ensures that multiple mandis operating on the same day in the same state are not discarded."
- **Technical Justification:** Lines 202–206 in `app/data_processing.py`.
- **Likely Follow-up:** *Where are duplicate counts recorded?*
  - **Short Answer:** "In the `duplicate_records` column of the `import_history` table."

### Q26. Why do mandis have missing price records on Sundays and holidays?
- **Suggested Answer:** "APMC physical mandis are officially closed on Sundays and gazetted holidays, so no auctions take place and no prices are recorded."
- **Technical Justification:** Addressed in `build_analytical_dataset()` line 471 via `.ffill()`.
- **Likely Follow-up:** *Why forward-fill instead of dropping those dates?*
  - **Short Answer:** "Dropping dates creates irregular time gaps that break SARIMAX; forward-filling reflects real-world market reality where Saturday's closing rate remains the reference price until Monday."

### Q27. What is the difference between raw transaction logs and aggregated daily data?
- **Suggested Answer:** "A raw transaction log records each individual farmer call or each truckload sold at an auction. Aggregated daily data sums all calls on that date into a single count and averages the commodity prices."
- **Technical Justification:** Demonstrated in Chapter 5 with the illustrative fictional example.
- **Likely Follow-up:** *Does your importer handle both?*
  - **Short Answer:** "Yes, if KCC lacks a count column, it treats rows as individual logs and sums them; if already aggregated, it reads the count column directly."

### Q28. What happens if a fuel CSV has no state column?
- **Suggested Answer:** "Our importer checks if `state` is present. If missing, it deduplicates purely by `observation_date`, treating the fuel rates as national or regional baseline prices."
- **Technical Justification:** `app/data_processing.py:import_fuel_csv()` line 260.
- **Likely Follow-up:** *Is diesel price uniform across India?*
  - **Short Answer:** "No, state VAT causes slight variations, but price movements and shock revisions are highly synchronized nationally."

### Q29. How does `--replace` work in CLI imports?
- **Suggested Answer:** "When `--replace` is provided, the importer executes `db.query(Model).delete()` to empty the target table before bulk inserting new records, preventing duplicate record buildup."
- **Technical Justification:** `app/data_processing.py` lines 150, 208, and 264.
- **Likely Follow-up:** *Does `--replace` delete the import history?*
  - **Short Answer:** "No, `import_history` is an append-only audit log."

### Q30. How do you distinguish between real and synthetic data?
- **Suggested Answer:** "Every observation table has an `is_synthetic` boolean column. If demo data is generated, `is_synthetic` is True. In reports, provenance is classified as `SYNTHETIC`, `UNVERIFIED` (custom user CSV), or `VERIFIED_REAL` (certified official data via `--verified-real`)."
- **Technical Justification:** `app/data_processing.py:get_data_quality_report()` lines 329–350.
- **Likely Follow-up:** *Why is provenance tracking so important?*
  - **Short Answer:** "To ensure academic honesty so evaluators and users never confuse synthetic demonstration data with real-world official records."

---

## Category 6: Database & Data Models

### Q31. Why use an ORM like SQLAlchemy instead of writing raw SQL queries?
- **Suggested Answer:** "SQLAlchemy provides type safety, automatically handles schema migrations via `Base.metadata.create_all()`, prevents SQL injection vulnerabilities, and allows database portability between SQLite for local testing and PostgreSQL for production."
- **Technical Justification:** Defined in `app/database.py` and `app/models.py`.
- **Likely Follow-up:** *Does SQLAlchemy slow down bulk imports?*
  - **Short Answer:** "Not when using `db.bulk_save_objects()`, which executes batched insertions in fractions of a second."

### Q32. What indexes are created in your SQLite tables?
- **Suggested Answer:** "We index `id` as primary key, `observation_date` for fast date-based time-series joining, and `state` and `commodity` for rapid query filtering."
- **Technical Justification:** Specified via `index=True` on columns in `app/models.py` (e.g., lines 15, 16, 41, 42).
- **Likely Follow-up:** *Why index `observation_date`?*
  - **Short Answer:** "Because our core operations involve joining tables on date and grouping by date ranges."

### Q33. What is stored in the `import_history` table?
- **Suggested Answer:** "It logs every import attempt with dataset type, filename, UTC timestamp, total rows, accepted rows, rejected rows, duplicate rows, status (`SUCCESS` or `FAILED`), and error notes."
- **Technical Justification:** `app/models.py:ImportHistory` lines 94–121.
- **Likely Follow-up:** *Can you inspect this table from Python?*
  - **Short Answer:** "Yes, via `db.query(ImportHistory).all()` or by querying SQLite directly."

### Q34. What is stored in the `forecast_history` table?
- **Suggested Answer:** "It logs each forecast execution: model name, target variable, state, forecast start/end dates, horizon days, MAE, RMSE, MAPE, advisory stress category, and serialized JSON prediction details."
- **Technical Justification:** `app/models.py:ForecastHistory` lines 124–156.
- **Likely Follow-up:** *Why store details as JSON?*
  - **Short Answer:** "To store full arrays of future daily predictions and confidence bounds in a single flexible text field."

### Q35. What is the database file name and where is it located?
- **Suggested Answer:** "It is named `agristress.db`, located directly in the project root directory (`d:\python-capstone\agristress.db`)."
- **Technical Justification:** Configured in `app/config.py` line 12.
- **Likely Follow-up:** *Can you open it in external tools?*
  - **Short Answer:** "Yes, in any standard SQLite viewer like DB Browser for SQLite or VS Code SQLite extensions."

---

## Category 7: Feature Engineering & Mathematical Formulas

### Q36. What is the exact formula for `commodity_price_change`?
- **Suggested Answer:** "$\Delta W_t = W_t - W_{t-1}$. It represents the first difference: today's wholesale price minus yesterday's wholesale price in rupees per quintal."
- **Technical Justification:** `merged['wholesale_price'].diff()` in `app/data_processing.py` line 477.
- **Likely Follow-up:** *What is the value on the very first day of the dataset?*
  - **Short Answer:** "`NaN`, because there is no preceding day."

### Q37. What is the formula for `commodity_pct_change`?
- **Suggested Answer:** "$\% \Delta W_t = \left(\frac{W_t - W_{t-1}}{W_{t-1}}\right) \times 100$. It normalizes price movement as a percentage of yesterday's price."
- **Technical Justification:** `merged['wholesale_price'].pct_change(fill_method=None) * 100.0` in line 478.
- **Likely Follow-up:** *Why is percentage change better than absolute price change?*
  - **Short Answer:** "It allows fair comparison across crops with different price scales, such as ₹1,000 onion versus ₹6,000 cumin."

### Q38. How is 7-day rolling price volatility calculated?
- **Suggested Answer:** "It is the rolling sample standard deviation of wholesale price over a 7-day window: $\sigma_{7d, t} = \sqrt{\frac{1}{k-1} \sum (W_{t-i} - \bar{W})^2}$, where $k \le 7$."
- **Technical Justification:** `merged['wholesale_price'].rolling(7, min_periods=2).std()` in line 479.
- **Likely Follow-up:** *Why set `min_periods=2`?*
  - **Short Answer:** "To compute volatility as soon as two observations are available, avoiding 6 days of missing values at the start."

### Q39. What is the formula for wholesale-retail price spread?
- **Suggested Answer:** "$\text{Spread}_t = R_t - W_t$, where $R_t$ is retail price and $W_t$ is wholesale price in INR per quintal."
- **Technical Justification:** `merged['retail_price'] - merged['wholesale_price']` in line 482.
- **Likely Follow-up:** *What happens if retail price is missing in the data?*
  - **Short Answer:** "The spread is assigned `NaN`, and subsequent functions handle missing spreads safely."

### Q40. What is `retail_margin_pct` and how is it calculated?
- **Suggested Answer:** "It expresses the spread as a percentage of wholesale price: $\left(\frac{R_t - W_t}{W_t}\right) \times 100$. It shows the retail markup relative to what the farmer received."
- **Technical Justification:** Calculated in `app/data_processing.py` line 483.
- **Likely Follow-up:** *What does a margin of 100% mean?*
  - **Short Answer:** "It means retail price is double the farmgate wholesale price."

### Q41. What is the formula for `diesel_pct_change`?
- **Suggested Answer:** "$\% \Delta D_t = \left(\frac{D_t - D_{t-1}}{D_{t-1}}\right) \times 100$. It measures daily percentage adjustments in retail diesel price."
- **Technical Justification:** `merged['diesel_price'].pct_change(fill_method=None) * 100.0` in line 489.
- **Likely Follow-up:** *Why do you use this for shock detection?*
  - **Short Answer:** "Because days where $|\% \Delta D_t| \ge 1.0\%$ represent significant official price revisions."

### Q42. Why do you calculate lagged diesel changes (`diesel_change_lag1`, `diesel_change_lag7`)?
- **Suggested Answer:** "Farmers rarely react to a diesel hike on the exact day it is announced. Lagged features capture delayed behavioral responses, such as when weekly tractor fuel or transport hiring bills are paid."
- **Technical Justification:** `merged['diesel_price_change'].shift(1)` and `.shift(7)` in lines 490–491.
- **Likely Follow-up:** *Did lagged diesel changes show strong correlation in your results?*
  - **Short Answer:** "No, correlations remained weak ($r \approx 0.065$), showing that fuel price alone is not the primary driver of call volume."

---

## Category 8: Descriptive Statistics

### Q43. What descriptive statistics does your project compute?
- **Suggested Answer:** "For every numeric variable, we compute count, arithmetic mean, standard deviation, minimum, median, and maximum."
- **Technical Justification:** Computed in `app/analysis.py:get_descriptive_summary()` and saved in `descriptive_statistics.csv`.
- **Likely Follow-up:** *Why compute both mean and median?*
  - **Short Answer:** "Mean shows the overall average but is sensitive to extreme outliers; median gives the 50th percentile, which is robust against skewed price spikes."

### Q44. What was the mean daily query count in your reported run?
- **Suggested Answer:** "The mean daily query count was **141.56 calls per day**, with a standard deviation of **49.99**, a minimum of 69, and a maximum of 246 calls."
- **Technical Justification:** Saved in `outputs/tables/descriptive_statistics.csv` line 2.
- **Likely Follow-up:** *What was the median?*
  - **Short Answer:** "132.50 calls per day, close to the mean, indicating a relatively symmetric distribution."

### Q45. What was the average wholesale price in your sample?
- **Suggested Answer:** "The average wholesale price was **₹1,755.94 per quintal**, ranging from ₹579.45 to ₹3,044.04 with a standard deviation of ₹994.25."
- **Technical Justification:** `outputs/tables/descriptive_statistics.csv` line 3.
- **Likely Follow-up:** *Why is standard deviation so large (₹994)?*
  - **Short Answer:** "Because commodity prices experienced a major trend decline from over ₹3,000 down to ₹600 across the 180-day sample period."

### Q46. What was the average wholesale-retail spread?
- **Suggested Answer:** "The average spread was **₹1,299.04 per quintal**, with retail prices averaging ₹3,054.98 and wholesale averaging ₹1,755.94."
- **Technical Justification:** `outputs/tables/descriptive_statistics.csv` line 6.
- **Likely Follow-up:** *What was the maximum observed spread?*
  - **Short Answer:** "₹2,728.31 per quintal, occurring during peak wholesale price slumps."

---

## Category 9: Pearson & Spearman Correlation

### Q47. What is Pearson correlation ($r$)?
- **Suggested Answer:** "Pearson correlation measures the strength and direction of a linear relationship between two continuous variables on a scale from $-1.0$ to $+1.0$. An $r = +1$ means perfect direct linearity; $r = -1$ means perfect inverse linearity; and $r = 0$ means no linear association."
- **Technical Justification:** Computed via `scipy.stats.pearsonr` in `app/analysis.py`.
- **Likely Follow-up:** *What is a key assumption of Pearson correlation?*
  - **Short Answer:** "It assumes bivariate normality and linearity between the variables."

### Q48. What is Spearman rank correlation ($\rho$)?
- **Suggested Answer:** "Spearman correlation measures the monotonic association between two variables by calculating Pearson's correlation on their rank values rather than raw numbers. It evaluates whether variables increase together, even if non-linearly."
- **Technical Justification:** Computed via `scipy.stats.spearmanr` in `app/analysis.py`.
- **Likely Follow-up:** *Why is Spearman less sensitive to outliers?*
  - **Short Answer:** "Because converting extreme values to ranks (e.g., 1st, 2nd, 3rd) bounds their mathematical leverage."

### Q49. What correlation did you find between KCC demand and wholesale price?
- **Suggested Answer:** "We found a strong negative correlation: Pearson $r = -0.8329$ and Spearman $\rho = -0.8840$ across 180 observations."
- **Technical Justification:** `outputs/tables/correlations.csv` line 2.
- **Likely Follow-up:** *What does this negative correlation mean in plain English?*
  - **Short Answer:** "As wholesale mandi prices drop, farmer helpline call volume increases substantially."

### Q50. What correlation did you find with daily price changes?
- **Suggested Answer:** "A weak correlation: Pearson $r = -0.1232$ and Spearman $\rho = -0.0398$."
- **Technical Justification:** `outputs/tables/correlations.csv` line 3.
- **Likely Follow-up:** *Why is daily price change weakly correlated while price level is strongly correlated?*
  - **Short Answer:** "Farmers do not panic over minor daily price wiggles; they react when the cumulative price level drops below production cost over weeks."

### Q51. What correlation did you find with wholesale-retail spread?
- **Suggested Answer:** "A very strong positive correlation: Pearson $r = +0.9265$ and Spearman $\rho = +0.9093$ across 180 observations."
- **Technical Justification:** `outputs/tables/correlations.csv` line 5.
- **Likely Follow-up:** *Does this prove that price spread causes farmers to call?*
  - **Short Answer:** "No, correlation proves strong co-movement, but both could be influenced by harvest arrival volumes."

---

## Category 10: Hypothesis Testing (HYP-A, HYP-B, HYP-C)

### Q52. What is Hypothesis A (HYP-A)?
- **Suggested Answer:** "HYP-A tests: 'Do day-to-day percentage changes in wholesale commodity prices linearly correlate with KCC advisory query volume?' The null hypothesis is no linear correlation ($r = 0$), and the alternative is linear correlation exists ($r \neq 0$)."
- **Technical Justification:** Defined in `app/analysis.py` lines 144–181.
- **Likely Follow-up:** *What was the test outcome?*
  - **Short Answer:** "Fail to reject null hypothesis ($r = -0.1127$, $p = 0.1330 > 0.05$)."

### Q53. Why did HYP-A fail to reject the null hypothesis?
- **Suggested Answer:** "Because $p = 0.1330$ is greater than our significance threshold $\alpha = 0.05$. Daily price percentage noise does not have a statistically significant contemporaneous linear relationship with call volume."
- **Technical Justification:** Saved in `outputs/tables/hypothesis_tests.csv` line 2.
- **Likely Follow-up:** *Does this mean price has no effect on farmers?*
  - **Short Answer:** "No, price levels have a huge effect ($r = -0.83$); only same-day percentage fluctuations showed no linear correlation."

### Q54. What is Hypothesis B (HYP-B)?
- **Suggested Answer:** "HYP-B asks: 'Do retail diesel price shocks trigger significant shifts in advisory query demand?' The null hypothesis is that query volume distributions on shock and normal fuel days are identical."
- **Technical Justification:** Defined in `app/analysis.py` lines 186–229.
- **Likely Follow-up:** *Which statistical test was selected for HYP-B?*
  - **Short Answer:** "The two-sided Mann-Whitney U non-parametric rank sum test."

### Q55. Why use the Mann-Whitney U test instead of Student's t-test for HYP-B?
- **Suggested Answer:** "Fuel shock days are rare, producing small, skewed sample sizes. Student's t-test assumes a normal distribution, which shock days violate. The Mann-Whitney U test evaluates rank sums without distributional assumptions."
- **Technical Justification:** Executed via `scipy.stats.mannwhitneyu(shock_q, norm_q, alternative='two-sided')`.
- **Likely Follow-up:** *What was the result of HYP-B on your data?*
  - **Short Answer:** "Fail to reject null hypothesis due to inadequate sample size: only 3 shock days were detected, below our minimum requirement of 5."

### Q56. What is Hypothesis C (HYP-C)?
- **Suggested Answer:** "HYP-C tests: 'Is the wholesale-to-retail price spread monotonically associated with farmer query demand?' The null hypothesis is $\rho = 0$, and the alternative is $\rho \neq 0$."
- **Technical Justification:** Defined in `app/analysis.py` lines 233–270.
- **Likely Follow-up:** *What was the outcome of HYP-C?*
  - **Short Answer:** "Reject null hypothesis ($\rho = +0.9093$, $p < 0.0001$). We confirm a strong, statistically significant monotonic association."

### Q57. In your output table, HYP-C shows `p_value: 0.0`. Is the probability literally zero?
- **Suggested Answer:** "No, in SciPy floating-point computation, values smaller than $10^{-16}$ round to $0.0$. Mathematically, it means $p < 0.0001$, indicating statistical significance well below $\alpha = 0.05$."
- **Technical Justification:** Discussed in Chapter 8 and documented in `outputs/reports/summary_report.md`.
- **Likely Follow-up:** *What is the effect size in HYP-C?*
  - **Short Answer:** "The effect size is the rank correlation coefficient itself, $\rho = +0.9093$."

### Q58. What is the biggest econometric limitation of your hypothesis tests?
- **Suggested Answer:** "Daily time-series observations exhibit serial autocorrelation. Ordinary Pearson and Spearman tests assume independent and identically distributed (i.i.d.) observations. Serial dependence narrows standard errors, making p-values appear artificially small. We explicitly report this limitation."
- **Technical Justification:** Documented in `app/analysis.py` line 164 and in `summary_report.md`.
- **Likely Follow-up:** *How would you fix this in an advanced implementation?*
  - **Short Answer:** "By applying Newey-West HAC standard error corrections or pre-whitening the series via ARIMA residuals."

---

## Category 11: Individual Visualizations

### Q59. How many charts does the system generate?
- **Suggested Answer:** "10 charts in total: 8 exploratory analysis charts generated by `app/analysis.py` and 2 forecasting validation charts generated by `app/forecasting.py`."
- **Technical Justification:** All 10 PNG files verified in `outputs/charts/`.
- **Likely Follow-up:** *Are they saved as vector graphics or raster?*
  - **Short Answer:** "As 120–130 DPI PNG raster images using Matplotlib."

### Q60. What does `query_demand_over_time.png` show?
- **Suggested Answer:** "It shows raw daily KCC inquiry counts in semi-transparent blue and a 14-day rolling moving average in solid red over the entire sample period."
- **Technical Justification:** `app/analysis.py:plot_query_demand_over_time()`.
- **Likely Follow-up:** *Why plot both lines?*
  - **Short Answer:** "The blue line shows daily volatility, while the red line reveals macro-seasonal trends by smoothing out two 7-day weekly cycles."

### Q61. What does `seasonality_patterns.png` prove?
- **Suggested Answer:** "It proves a strong 7-day weekly cycle: Monday through Friday maintain high inquiry volumes (~150 calls/day), while Sunday drops sharply (~50 calls/day)."
- **Technical Justification:** `app/analysis.py:plot_seasonality()`.
- **Likely Follow-up:** *How did this influence model selection?*
  - **Short Answer:** "It justified configuring a seasonal period of $s=7$ in our SARIMAX model."

### Q62. What is shown in `commodity_price_trends.png`?
- **Suggested Answer:** "Panel A shows wholesale mandi prices in green, and Panel B shows 7-day rolling price volatility in amber, illustrating market turbulence during price drops."
- **Technical Justification:** `app/analysis.py:plot_commodity_trends()`.
- **Likely Follow-up:** *Why not put them on a single panel with dual axes?*
  - **Short Answer:** "Two stacked panels make it cleaner to visually inspect when price declines trigger volatility spikes without visual clutter."

### Q63. What is shown in `diesel_price_trends.png`?
- **Suggested Answer:** "Panel A shows the retail diesel price level in magenta, and Panel B shows daily percentage revisions in purple bars with red dashed lines at $\pm 1.5\%$ marking shock thresholds."
- **Technical Justification:** `app/analysis.py:plot_diesel_trends()`.
- **Likely Follow-up:** *What does Panel B reveal about fuel pricing in India?*
  - **Short Answer:** "That price revisions are infrequent, resulting in mostly zero-change days separated by rare adjustment steps."

### Q64. What is shown in `price_spreads.png`?
- **Suggested Answer:** "The consumer retail price in purple, wholesale mandi price in green, and the shaded purple margin between them representing the marketing spread ($R_t - W_t$)."
- **Technical Justification:** `app/analysis.py:plot_price_spread()`.
- **Likely Follow-up:** *What happens to the shaded band when wholesale price crashes?*
  - **Short Answer:** "The shaded band widens, visually confirming sticky retail prices and expanding marketing margins."

### Q65. What is shown in `query_vs_economic.png`?
- **Suggested Answer:** "A dual-axis chart showing 7-day moving average of farmer inquiries on the left blue axis against wholesale mandi price on the right orange dashed axis."
- **Technical Justification:** `app/analysis.py:plot_query_vs_economic()`.
- **Likely Follow-up:** *What visual trend is apparent?*
  - **Short Answer:** "A clear inverse relationship: when wholesale prices slump, farmer inquiries trend upward."

### Q66. What does `correlation_heatmap.png` display?
- **Suggested Answer:** "A $6 \times 6$ matrix showing Pearson correlation coefficients between KCC queries, wholesale price, retail price, diesel price, spread, and volatility, colored with a coolwarm palette."
- **Technical Justification:** `app/analysis.py:plot_correlation_heatmap()`.
- **Likely Follow-up:** *What is the strongest correlation on the heatmap?*
  - **Short Answer:** "Queries vs Price Spread at $+0.93$."

### Q67. What is shown in `regional_queries.png`?
- **Suggested Answer:** "A horizontal bar chart comparing cumulative inquiry volume by state, with Maharashtra having the highest volume in our demo dataset."
- **Technical Justification:** `app/analysis.py:plot_regional_comparison()`.
- **Likely Follow-up:** *How does this help call centre planners?*
  - **Short Answer:** "It guides geographical allocation of tele-advisors and regional agronomic experts."

### Q68. What are the two panels in `forecast_evaluation.png`?
- **Suggested Answer:** "Panel A shows out-of-sample holdout test validation comparing actual queries against Seasonal Naive and SARIMAX. Panel B shows the 14-day future forecast in orange with a 95% confidence interval and horizontal stress thresholds."
- **Technical Justification:** `app/forecasting.py` lines 165–195.
- **Likely Follow-up:** *What does the orange line represent in Panel B?*
  - **Short Answer:** "The predicted mean call volume for the next 14 days."

### Q69. What is shown in `actual_vs_predicted.png`?
- **Suggested Answer:** "A dedicated high-resolution plot of the holdout test period, comparing actual calls against Seasonal Naive and SARIMAX predictions."
- **Technical Justification:** `app/forecasting.py` lines 149–163.
- **Likely Follow-up:** *Why have both this plot and Panel A of `forecast_evaluation.png`?*
  - **Short Answer:** "`actual_vs_predicted.png` provides an uncluttered, single-focus view for slide decks and detailed inspection of turning points."

---

## Category 12: Forecasting & SARIMAX Model

### Q70. What is your forecasting target variable?
- **Suggested Answer:** "`query_count`, the daily total number of agricultural advisory inquiries logged across the target state or region."
- **Technical Justification:** `app/forecasting.py:generate_forecast()` line 78.
- **Likely Follow-up:** *Why not forecast commodity price instead?*
  - **Short Answer:** "Because our core mission is modeling call-centre operational stress; market prices serve as explanatory inputs rather than our target."

### Q71. What is your train/test split methodology?
- **Suggested Answer:** "We use a strict chronological holdout split. The holdout test set is the last $T_{\text{test}} = \min(30, \max(7, \text{int}(0.2 \times N)))$ days. For our 180-day series, the test set is 30 days."
- **Technical Justification:** `app/forecasting.py` line 86.
- **Likely Follow-up:** *Why not use random k-fold cross validation?*
  - **Short Answer:** "Random splitting in time series causes future data leakage into the past. Chronological splitting strictly tests forecasting future unseen days."

### Q72. What is your benchmark baseline model?
- **Suggested Answer:** "A 7-Day Seasonal Naive baseline, where today's predicted calls equal the actual calls from exactly 7 days ago: $\hat{y}_t = y_{t-7}$."
- **Technical Justification:** `app/forecasting.py` line 90.
- **Likely Follow-up:** *Why is this a good baseline?*
  - **Short Answer:** "Because agricultural calls have strong weekly seasonality; last week's same-day observation captures both day-of-week and level effects simply."

### Q73. What is your chosen SARIMAX order?
- **Suggested Answer:** "$\text{SARIMAX}(1,1,1)(1,1,0)[7]$. Non-seasonal $p=1, d=1, q=1$ and seasonal $P=1, D=1, Q=0$ with periodicity $s=7$."
- **Technical Justification:** `statsmodels.tsa.statespace.sarimax.SARIMAX` in `app/forecasting.py` lines 101 and 114.
- **Likely Follow-up:** *What does $d=1$ and $D=1$ do?*
  - **Short Answer:** "$d=1$ eliminates non-stationary baseline trend; $D=1$ eliminates weekly seasonal baseline shifts."

### Q74. How does SARIMAX perform against the baseline on holdout data?
- **Suggested Answer:** "On our holdout test set, Seasonal Naive achieved an MAE of 9.83 calls (MAPE 7.08%), while SARIMAX achieved an MAE of 10.46 calls (MAPE 7.32%)."
- **Technical Justification:** Saved in `outputs/forecasts/forecast_evaluation_metrics.csv`.
- **Likely Follow-up:** *Why keep SARIMAX if its MAE is slightly higher?*
  - **Short Answer:** "SARIMAX computes 95% statistical confidence intervals and models error shock decay, which naive models cannot do. On real-world non-periodic data, SARIMAX provides superior flexibility."

### Q75. How are the 95% confidence intervals calculated?
- **Suggested Answer:** "They are calculated from the forecast error variance of the statespace model via `fc.conf_int(alpha=0.05)`, representing $[\hat{y}_t - 1.96\sigma_t, \hat{y}_t + 1.96\sigma_t]$."
- **Technical Justification:** `app/forecasting.py` line 117.
- **Likely Follow-up:** *Why does the confidence interval widen over the 14-day horizon?*
  - **Short Answer:** "Forecast uncertainty compounds as you predict further into the future."

### Q76. How does your code prevent negative call predictions?
- **Suggested Answer:** "We apply `np.clip(predictions, 0, None)` to ensure that neither predicted means nor lower confidence bounds can fall below zero."
- **Technical Justification:** `app/forecasting.py` lines 102 and 116.
- **Likely Follow-up:** *Can SARIMAX produce negative numbers naturally?*
  - **Short Answer:** "Yes, linear differenced equations can produce negative numbers, which is why clipping to zero is necessary for call counts."

---

## Category 13: Stress Classification & Recommendations

### Q77. How is the operational advisory stress category computed?
- **Suggested Answer:** "By comparing forecasted mean demand against historical baseline mean ($\mu$) and standard deviation ($\sigma$): Elevated is $\mu + 0.75\sigma$ (179.1 calls) and High is $\mu + 1.75\sigma$ (229.0 calls)."
- **Technical Justification:** `app/forecasting.py:classify_advisory_stress()` lines 38–63.
- **Likely Follow-up:** *What category was assigned in your reported run?*
  - **Short Answer:** "`NORMAL`, because the forecast averaged 154.0 calls, which is below 179.1."

### Q78. What does "Advisory Stress" mean in this project?
- **Suggested Answer:** "It is a project-defined quantitative proxy for call centre operational load. It indicates whether inquiry volumes are expected to exceed normal capacity, requiring staffing adjustments."
- **Technical Justification:** Documented with an explicit disclaimer in `app/forecasting.py` line 62.
- **Likely Follow-up:** *Is it an official government standard?*
  - **Short Answer:** "No, it is an engineering research proxy based on standard statistical process control principles."

### Q79. What are the three priority categories in your farmer advisory?
- **Suggested Answer:** "1. `Action to consider now` (price drops $\ge 5\%$ or High stress); 2. `Check before deciding` (moderate price drops $2\text{--}5\%$ or Elevated stress); and 3. `No clear signal` (stable prices and Normal demand)."
- **Technical Justification:** Defined in `app/recommendations.py` lines 61–63 and 440–460.
- **Likely Follow-up:** *What priority was assigned in your latest run?*
  - **Short Answer:** "`Check before deciding`, because wholesale prices declined 6.1% over the past 7 days."

### Q80. How does the recommendation engine handle data freshness?
- **Suggested Answer:** "It checks the date of the latest observation against today's date. If data is more than 30 days old, it prints a prominent warning banner stating that figures represent historical data and local spot prices must be verified before acting."
- **Technical Justification:** `app/recommendations.py:get_freshness_assessment()` lines 136–188.
- **Likely Follow-up:** *Why is freshness so important for farmers?*
  - **Short Answer:** "Because acting on months-old price records could cause significant financial losses in volatile agricultural markets."

### Q81. What practical factors does the advisory tell farmers to check before selling?
- **Suggested Answer:** "Four key factors: 1. Transport and handling expenses; 2. Crop perishability and on-farm storage viability; 3. Cleaning, sorting, and moisture grading premiums; and 4. Immediate personal cash needs for debts or wages."
- **Technical Justification:** `app/recommendations.py:UI_STRINGS` lines 70–73.
- **Likely Follow-up:** *Does your system do multi-mandi comparisons?*
  - **Short Answer:** "Yes, if multi-mandi records exist, it outputs an APMC comparison table comparing prices and estimated transport costs."

### Q82. What official contact channels are provided in the advisory?
- **Suggested Answer:** "The Kisan Call Centre toll-free number **1800-180-1551**, operational from **6:00 AM to 10:00 PM every day**, plus guidance to consult local Gram Panchayat Krishi Sahayaks or KVK agronomists."
- **Technical Justification:** `app/recommendations.py:VERIFIED_ASSISTANCE` lines 33–39.
- **Likely Follow-up:** *What disclaimer is printed regarding chemical recommendations?*
  - **Short Answer:** "An explicit statement that the advisory analyzes market trends and does NOT prescribe chemical pesticide or fertilizer dosages."

---

## Category 14: Python Libraries & Technology Choices

### Q83. Why use pure Python instead of R for this econometric project?
- **Suggested Answer:** "While R is popular in statistics, Python provides an end-to-end software engineering ecosystem: SQLAlchemy ORM for database modeling, Pytest for automated testing, and clean modular scripting, all in one language."
- **Technical Justification:** Implemented using Pandas, SciPy, and Statsmodels in Python 3.10.
- **Likely Follow-up:** *Does Python's Statsmodels have the same SARIMAX accuracy as R's `forecast` package?*
  - **Short Answer:** "Yes, Statsmodels statespace SARIMAX uses exact Kalman filter maximum likelihood estimation matching R's algorithms."

### Q84. What is the role of `matplotlib.use('Agg')`?
- **Suggested Answer:** "It configures Matplotlib to use the headless Anti-Grain Geometry backend, enabling figure generation directly to disk without requiring an active graphical desktop window or display server."
- **Technical Justification:** `app/analysis.py` line 15 and `app/forecasting.py` line 15.
- **Likely Follow-up:** *What happens if you omit this line on a Linux server?*
  - **Short Answer:** "Matplotlib can crash with a `no display name and no $DISPLAY environment variable` error."

### Q85. Why use Seaborn alongside Matplotlib?
- **Suggested Answer:** "Seaborn provides high-level statistical plotting abstractions, such as `sns.heatmap()` with automated numeric annotation and continuous colormaps, which would require extensive manual code in pure Matplotlib."
- **Technical Justification:** `app/analysis.py:plot_correlation_heatmap()` line 485.
- **Likely Follow-up:** *Is Seaborn a replacement for Matplotlib?*
  - **Short Answer:** "No, Seaborn sits directly on top of Matplotlib and uses its canvas."

### Q86. Why is SQLite sufficient for this project?
- **Suggested Answer:** "SQLite is serverless, zero-configuration, and stores the entire database in a single local file (`agristress.db`). For our dataset sizes (tens of thousands of rows), SQLite queries execute in milliseconds without external server overhead."
- **Technical Justification:** Configured in `app/database.py`.
- **Likely Follow-up:** *Can the system scale to PostgreSQL?*
  - **Short Answer:** "Yes, by simply passing a PostgreSQL connection string in the `DATABASE_URL` environment variable."

### Q87. Why use `python-dotenv`?
- **Suggested Answer:** "It allows environment variables (like `DATABASE_URL`, `DATA_DIR`, `OUTPUTS_DIR`) to be defined in a local `.env` file without hardcoding environment paths in Python code."
- **Technical Justification:** Loaded in `app/config.py` lines 3–6.
- **Likely Follow-up:** *Is `.env` committed to Git?*
  - **Short Answer:** "No, `.env` is listed in `.gitignore`; only `.env.example` is committed."

---

## Category 15: Tests & Verification Suite

### Q88. How many automated tests exist in the project?
- **Suggested Answer:** "**35 tests**, organized across 4 test modules: `test_data_processing.py` (11 tests), `test_analysis.py` (6 tests), `test_forecasting.py` (5 tests), and `test_recommendations.py` (13 tests)."
- **Technical Justification:** Verified by running `python -m pytest -v` (35 passed in ~6.9s).
- **Likely Follow-up:** *How do you run the tests?*
  - **Short Answer:** "`python -m pytest -v` from the project root."

### Q89. Can you give an example of a unit test in `test_analysis.py`?
- **Suggested Answer:** "`test_descriptive_summary_known_values` feeds a small DataFrame with known values [10, 20, 30] and asserts that the calculated mean is exactly 20.0 and standard deviation is 10.0."
- **Technical Justification:** `tests/test_analysis.py` lines 10–25.
- **Likely Follow-up:** *Why test basic math?*
  - **Short Answer:** "To ensure that Pandas aggregation wrappers do not introduce unexpected rounding errors or drop values."

### Q90. How do you test hypothesis test logic?
- **Suggested Answer:** "`test_hypothesis_a_perfect_correlation` constructs two series with perfect correlation ($y = 2x$) and verifies that $r = 1.0$, $p < 0.001$, and `reject_null` is True."
- **Technical Justification:** `tests/test_analysis.py` lines 27–43.
- **Likely Follow-up:** *Do you test insufficient sample handling?*
  - **Short Answer:** "Yes, `test_hypothesis_insufficient_sample` verifies that fewer than 15 rows returns `reject_null=False` with an informative error message."

### Q91. What does `test_scenario_11_changing_dataset_recalculates` prove?
- **Suggested Answer:** "It proves that our recommendation engine dynamically recalculates new metrics, trends, and advisory texts when input data changes, rather than returning hardcoded static advice."
- **Technical Justification:** `tests/test_recommendations.py` lines 340–390.
- **Likely Follow-up:** *Why is this test critical for evaluators?*
  - **Short Answer:** "It provides automated proof that the system is genuinely dynamic and responsive to new input datasets."

### Q92. What is an integration test in your suite?
- **Suggested Answer:** "`test_data_alignment_pipeline` in `test_data_processing.py`. It imports sample KCC, mandi, and fuel CSVs into a temporary SQLite database, calls `build_analytical_dataset()`, and asserts that the merged dataset contains all aligned columns."
- **Technical Justification:** `tests/test_data_processing.py` lines 85–130.
- **Likely Follow-up:** *Do tests use the production database?*
  - **Short Answer:** "No, tests create isolated temporary SQLite databases or rollback transactions to prevent data pollution."

---

## Category 16: Errors, Edge Cases & Debugging

### Q93. What happens if a user provides a CSV with missing required columns?
- **Suggested Answer:** "`check_missing_columns()` catches the missing fields, records an error message in the `import_history` table, returns `status='FAILED'`, and halts import without throwing an unhandled exception."
- **Technical Justification:** `app/data_processing.py` lines 17–21 and 117–123.
- **Likely Follow-up:** *Does the program crash?*
  - **Short Answer:** "No, the error is caught, reported clearly in the console, and logged in the database."

### Q94. What happens if a CSV contains corrupted date strings like "invalid-date"?
- **Suggested Answer:** "`safe_parse_dates()` uses `pd.to_datetime(series, errors='coerce')`, converting corrupted strings to `NaT`. The cleaning filter then drops rows with `NaT` and reports them in `rejected_rows`."
- **Technical Justification:** `app/data_processing.py` line 101.
- **Likely Follow-up:** *Where can the user see how many rows were rejected?*
  - **Short Answer:** "In the terminal import summary and in the `rejected_records` column of `import_history`."

### Q95. How does the code handle division by zero when calculating MAPE?
- **Suggested Answer:** "In `calculate_metrics()`, we use `denom = np.where(actual == 0, 1.0, actual)` so that days with zero calls use a denominator of 1.0, preventing `ZeroDivisionError`."
- **Technical Justification:** `app/forecasting.py` lines 32–33.
- **Likely Follow-up:** *Is this standard practice?*
  - **Short Answer:** "Yes, it is the standard zero-safe MAPE adjustment widely used in operational forecasting."

### Q96. What happens if SARIMAX fails to converge during optimization?
- **Suggested Answer:** "The fitting block is wrapped in a `try...except` block. If Statsmodels encounters an optimization error, it logs a warning and automatically falls back to the 7-day Seasonal Naive baseline."
- **Technical Justification:** `app/forecasting.py` lines 100–108.
- **Likely Follow-up:** *Does the user still get a forecast?*
  - **Short Answer:** "Yes, they receive the Seasonal Naive baseline forecast with an explicit warning note."

### Q97. What causes `UnicodeEncodeError` on Windows consoles and how did you prevent it?
- **Suggested Answer:** "Windows PowerShell and Command Prompt often default to legacy code page CP1252, which crashes when printing Unicode symbols or Hindi/Marathi text. We resolved this in `main.py` and `run_pipeline.py` via `sys.stdout.reconfigure(encoding='utf-8', errors='replace')`."
- **Technical Justification:** `main.py` lines 15–19 and `run_pipeline.py` lines 17–21.
- **Likely Follow-up:** *Does this affect Linux or macOS?*
  - **Short Answer:** "No, Unix consoles default to UTF-8, but our reconfigure call is guarded so it works safely across all operating systems."

---

## Category 17: Limitations, Ethics & Real-World Deployment

### Q98. Can a farmer make a guaranteed financial profit using this tool?
- **Suggested Answer:** "No. Agricultural markets are subject to sudden localized supply surges, weather disasters, and transport breakdowns. Our tool provides structured decision support to evaluate risks; it cannot guarantee future selling prices."
- **Technical Justification:** Explicit disclaimer in `app/recommendations.py:UI_STRINGS['limits_hdr']`.
- **Likely Follow-up:** *Is this disclaimer visible to the farmer?*
  - **Short Answer:** "Yes, every generated advisory includes an explicit 'Limits of this advisory' section."

### Q99. Why didn't you incorporate machine learning classification like Random Forest?
- **Suggested Answer:** "For time-series count data with strong weekly periodicity, statespace models like SARIMAX provide explicit seasonal differencing, statistical confidence intervals, and parameter interpretability. Standard Random Forest models cannot extrapolate linear trends or naturally handle temporal autocorrelation without extensive lag engineering."
- **Technical Justification:** Documented in Chapter 2 of the Deep Dive Guide.
- **Likely Follow-up:** *Could Random Forest be used in the future?*
  - **Short Answer:** "Yes, as an ensemble component alongside SARIMAX if hundreds of external tabular features were added."

### Q100. How would you deploy this project for real-world nationwide use?
- **Suggested Answer:** "We would connect the ingestion engine directly to government open APIs (like `data.gov.in` and Agmarknet) for automated daily data pulls, run the pipeline on an automated daily cron schedule, and distribute generated Hindi, Marathi, and regional advisories via WhatsApp or SMS to registered farmer cooperatives."
- **Technical Justification:** Roadmap outlined in Chapter 15 of the Deep Dive Guide.
- **Likely Follow-up:** *What is the biggest operational challenge in real-world deployment?*
  - **Short Answer:** "Ensuring timely daily data reporting from remote rural APMC mandis, which often experience multi-day upload delays."

---

## Category 18: Difficult Cross-Questioning & Novelty

### Q101. What is genuinely novel about this project? Isn't it just basic data analysis?
- **Suggested Answer:** "Basic academic analysis usually stops at p-values and regression tables that farmers cannot use. Our novelty lies in bridging the complete loop: from raw multi-source ingestion and time-series forecasting of call-centre operational stress to an automated, plain-language translation engine that converts econometric stress into actionable, freight-adjusted marketing decisions in regional languages."
- **Technical Justification:** The dual pipeline architecture connecting `app/analysis.py` to `app/recommendations.py`.
- **Likely Follow-up:** *Did you create new mathematical algorithms?*
  - **Short Answer:** "No, we applied established, mathematically rigorous algorithms (SARIMAX, Mann-Whitney U, Spearman) to solve a real-world agricultural systems integration problem."

### Q102. If your demo data is synthetic, how can you claim your results are valid?
- **Suggested Answer:** "We make no claim that synthetic numbers describe real-world market reality. Synthetic data was generated deterministically to test software architecture, pipeline resilience, and edge cases. When real CSV data is supplied, the exact same pipeline recalculates authentic results, as verified by our automated test suite."
- **Technical Justification:** Tested in `tests/test_recommendations.py:test_scenario_11_changing_dataset_recalculates`.
- **Likely Follow-up:** *How do you prove that to me right now?*
  - **Short Answer:** "By running `python main.py --kcc <path> --commodity-file <path> --fuel <path>` on any custom dataset and observing that metrics and advisory text recalculate dynamically."

### Q103. Why does your pipeline perform univariate forecasting instead of multivariate forecasting with commodity prices?
- **Suggested Answer:** "Because in practical forecasting, future commodity prices 14 days ahead are themselves unknown. Feeding predicted commodity prices into a call-demand model introduces compounded forecasting error. A univariate seasonal SARIMAX model evaluated against a Seasonal Naive benchmark provides reliable, audit-proof operational forecasts without unverified assumptions about future market trends."
- **Technical Justification:** Analyzed in Chapter 10 of the Deep Dive Guide.
- **Likely Follow-up:** *Under what conditions would multivariate SARIMAX be appropriate?*
  - **Short Answer:** "If we were modeling contemporaneous nowcasting (estimating today's calls from today's known morning mandi prices) rather than 14-day advance forecasting."

### Q104. What was the most difficult technical bug you solved during development?
- **Suggested Answer:** "Handling mandi calendar mismatches. Mandis close on Sundays and holidays while call centres operate daily. Performing a naive inner join dropped all Sunday records, breaking the weekly 7-day cyclicality required by SARIMAX. We solved this by creating a continuous date grid and forward-filling commodity prices while zero-filling unrecorded queries, preserving both price continuity and the weekly seasonal cycle."
- **Technical Justification:** Implemented in `app/data_processing.py` lines 465–474.
- **Likely Follow-up:** *Did forward-filling distort the correlation analysis?*
  - **Short Answer:** "No, because forward-filling simply reflects market reality: Saturday's closing price remains the benchmark until Monday's market opens."

### Q105. What is your closing defense statement for AgriStress Analytics?
- **Suggested Answer:** "AgriStress Analytics demonstrates how data engineering, applied econometrics, and human-centred design can come together. By taking messy agricultural records and transforming them into both proactive operational capacity forecasts for public infrastructure and actionable, freight-aware decision support for smallholder farmers, our project shows that engineering is not just about complex algorithms—it is about making data useful and trustworthy for the people who need it most."
