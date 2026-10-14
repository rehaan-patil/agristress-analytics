# AgriStress Analytics — Quick Start Guide for Teammates

This guide provides the shortest practical path to set up, run, and demonstrate the AgriStress Analytics backend locally.

---

## 1. Setup in 3 Commands

### Windows (PowerShell):
```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies & configure environment
pip install -r requirements.txt
copy .env.example .env

# 3. Initialize SQLite database tables
python scripts/init_db.py
```

### Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 scripts/init_db.py
```

---

## 2. Complete Local Demonstration (4 Steps)

```bash
# Step 1: Generate reproducible demo data (seed=42, 730 days, 4 states)
python scripts/generate_demo_data.py

# Step 2: Ingest the CSV datasets into SQLite
python scripts/import_data.py --all

# Step 3: Run the end-to-end analytical pipeline (generates 9 charts & summary report)
python scripts/run_analysis.py

# Step 4: Start the FastAPI local server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 3. Where to View Outputs in VS Code

- **Interactive Swagger API Docs:** Open browser to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Visualizations (PNGs):** Open the [outputs/charts/](file:///d:/python-capstone/outputs/charts) folder in the VS Code file explorer.
- **Markdown Research Report:** Open [outputs/reports/summary_report.md](file:///d:/python-capstone/outputs/reports/summary_report.md) and press `Ctrl + Shift + V`.
- **Harmonized Dataset:** Inspect [data/processed/analytical_dataset.csv](file:///d:/python-capstone/data/processed/analytical_dataset.csv).

---

## 4. Run the Test Suite

```bash
python -m pytest -v
```
All **26 tests** will execute and report passing in ~6 seconds.

---

*For detailed explanations of the mathematics, database schema, and architecture, refer to the full handover report: [docs/PROJECT_EXPLANATION_FOR_TEAM.md](file:///d:/python-capstone/docs/PROJECT_EXPLANATION_FOR_TEAM.md).*
