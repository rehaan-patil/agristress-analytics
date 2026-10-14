"""
Complete local analysis workflow runner for AgriStress Analytics.
Runs exploratory data analysis, generates charts, executes hypothesis tests,
fits SARIMAX, evaluates advisory stress, and compiles the research summary report.
"""
import sys
from pathlib import Path

# Add project root directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.data_processing import build_analytical_dataset, get_dataset_status
from app.analysis import generate_all_charts, run_hypothesis_tests, generate_summary_report, get_descriptive_summary
from app.forecasting import generate_forecast


def main():
    print("=================================================================")
    print("       AGRISTRESS ANALYTICS — LOCAL RESEARCH PIPELINE")
    print("=================================================================")

    db = SessionLocal()
    try:
        # Step 1: Data Status
        print("\n[STEP 1/6] Verifying Database Ingestion & Quality...")
        status = get_dataset_status(db)
        print(f"  Overall Readiness: {status['status']}")
        for name, info in status["datasets"].items():
            print(f"  - {name.upper()}: {info['total_records']:,} rows ({info['min_date']} to {info['max_date']})")
        if not status["ready_for_analysis"]:
            print("\n[ERROR] Database has insufficient data. Run:")
            print("  python scripts/generate_demo_data.py")
            print("  python scripts/import_data.py --all")
            return

        # Step 2: Build Analytical Dataset
        print("\n[STEP 2/6] Building Harmonized Analytical Time-Series...")
        df = build_analytical_dataset(db, export_csv=True)
        print(f"  Constructed dataset with {len(df):,} daily records across columns:")
        print(f"  {', '.join(df.columns)}")
        print("  Exported -> data/processed/analytical_dataset.csv")

        # Step 3: Descriptive Statistics
        print("\n[STEP 3/6] Computing Descriptive Statistics...")
        summary = get_descriptive_summary(df)
        for stat in summary["descriptive_statistics"]:
            print(f"  * {stat['variable']:<25}: Mean = {stat['mean']:<8} Std = {stat['std']:<8} [Min: {stat['min']}, Max: {stat['max']}]")

        # Step 4: Exploratory Visualizations
        print("\n[STEP 4/6] Generating Analytical Visualizations...")
        charts = generate_all_charts(db)
        print(f"  Generated {len(charts)} charts in outputs/charts/:")
        for c in charts:
            print(f"  - {Path(c).name}")

        # Step 5: Econometric Hypothesis Tests
        print("\n[STEP 5/6] Executing Hypothesis Tests (SciPy / Statsmodels)...")
        hyp = run_hypothesis_tests(df, diesel_shock_threshold_pct=2.0)
        for res in hyp["results"]:
            status_str = "REJECT H0" if res["reject_null"] else "FAIL TO REJECT H0"
            print(f"\n  [{res['hypothesis_code']}] {res['title']}")
            print(f"    Test: {res['test_used']} (N={res['sample_size']})")
            print(f"    Test Stat: {res['test_statistic']} | P-value: {res['p_value']}")
            print(f"    Outcome: {status_str} (alpha={res['significance_level']})")
            print(f"    Plain English: {res['verdict_plain_english']}")

        # Step 6: SARIMAX Forecasting & Advisory-Stress Classification
        print("\n[STEP 6/6] Fitting SARIMAX Model & Forecasting Advisory Stress...")
        fc = generate_forecast(db, horizon_days=14, use_sarimax=True)
        print(f"  Model Selected: {fc['model_name']}")
        print(f"  Evaluation Metrics: MAE = {fc['mae']}, RMSE = {fc['rmse']}, MAPE = {fc['mape']}%")
        stress = fc["stress_assessment"]
        print(f"  Advisory Stress Classification: [{stress['category'].upper()}]")
        print(f"  Details: {stress['explanation']}")
        print(f"  Forecast Chart Saved -> outputs/charts/forecast_evaluation.png")

        # Step 7: Research Summary Report
        rep = generate_summary_report(db)
        print(f"\n[REPORT] Full research summary generated: {rep['report_path']}")
        print("\n=================================================================")
        print("          PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        print("=================================================================")

    finally:
        db.close()


if __name__ == "__main__":
    main()
