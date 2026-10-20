# AgriStress Analytics — Quick Start Guide for Teammates

This guide provides the shortest practical path to set up, run, and demonstrate the AgriStress Analytics local research project.

---

## 1. Setup in 3 Commands

### Windows (PowerShell):
```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the complete analysis pipeline in one command
python main.py
```

### Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

---

## 2. One-Command Complete Demonstration

```bash
# Run the entire pipeline end-to-end
python main.py
```

*This command automatically initializes the SQLite database, validates the data, computes descriptive statistics, saves CSV tables, generates 10 exploratory charts, runs econometric hypothesis tests, executes holdout-validated SARIMAX forecasting, and generates the complete markdown report.*

Optional flags:
```bash
# Force regenerate synthetic demo data and re-import into a clean database:
python main.py --generate-data

# Filter by state or commodity:
python main.py --state Maharashtra --commodity Onion --horizon 21
```

---

## 3. Where to View Outputs

- **Markdown Research Report:** Open [outputs/reports/summary_report.md](file:///d:/python-capstone/outputs/reports/summary_report.md) and press `Ctrl + Shift + V`.
- **Visualizations (PNGs):** View all 10 figures in [outputs/charts/](file:///d:/python-capstone/outputs/charts).
- **Tabular Results (CSVs):** Inspect result tables in [outputs/tables/](file:///d:/python-capstone/outputs/tables).
- **Forecast Predictions & Metrics:** Inspect predictions in [outputs/forecasts/](file:///d:/python-capstone/outputs/forecasts).
- **Harmonized Dataset:** Inspect [data/processed/analytical_dataset.csv](file:///d:/python-capstone/data/processed/analytical_dataset.csv).

---

## 4. Run the Test Suite

```bash
python -m pytest
```
All **19 tests** will execute and report passing in ~5 seconds with zero warnings.

---

*For detailed explanations of the mathematics, database schema, and methodology, refer to [docs/PROJECT_EXPLANATION_FOR_TEAM.md](file:///d:/python-capstone/docs/PROJECT_EXPLANATION_FOR_TEAM.md) and [docs/METHODOLOGY.md](file:///d:/python-capstone/docs/METHODOLOGY.md).*
