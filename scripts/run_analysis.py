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
import argparse
from app.data_processing import build_analytical_dataset, get_dataset_status, get_data_quality_report
from app.analysis import generate_all_charts, run_hypothesis_tests, generate_summary_report, get_descriptive_summary, save_analysis_tables
from app.forecasting import generate_forecast


def run_pipeline(state: str = None, commodity: str = None, horizon_days: int = 14, shock_threshold: float = 1.5):
    print("=================================================================")
    print("       AGRISTRESS ANALYTICS — LOCAL RESEARCH PIPELINE")
    print("=================================================================")

    db = SessionLocal()
    try:
        # Step 1: Data Status & Quality
        print("\n[STEP 1/7] Verifying Database Ingestion & Quality...")
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
        print("\n[STEP 2/7] Building Harmonized Analytical Time-Series...")
        df = build_analytical_dataset(db, state=state, commodity=commodity, export_csv=True)
        quality = get_data_quality_report(db, df)
        print(f"  Constructed dataset with {len(df):,} daily records across columns:")
        print(f"  {', '.join(df.columns)}")
        print(f"  Data Quality Status: {quality['quality_status']} | Missing/Zero Query Rate: {quality['missingness_percentage']}%")
        print("  Exported -> data/processed/analytical_dataset.csv")

        # Step 3: Descriptive Statistics & Result Tables
        print("\n[STEP 3/7] Computing Descriptive Statistics & Saving Tables...")
        summary = get_descriptive_summary(df)
        for stat in summary["descriptive_statistics"]:
            print(f"  * {stat['variable']:<25}: Mean = {stat['mean']:<8} Std = {stat['std']:<8} [Min: {stat['min']}, Max: {stat['max']}]")
        
        tables = save_analysis_tables(df, db)
        print(f"  Exported {len(tables)} result tables into outputs/tables/:")
        for k, v in tables.items():
            print(f"  - {Path(v).name}")

        # Step 4: Exploratory Visualizations
        print("\n[STEP 4/7] Generating Analytical Visualizations...")
        charts = generate_all_charts(db)
        print(f"  Generated {len(charts)} exploratory charts in outputs/charts/:")
        for c in charts:
            print(f"  - {Path(c).name}")

        # Step 5: Econometric Hypothesis Tests
        print("\n[STEP 5/7] Executing Hypothesis Tests (SciPy / Statsmodels)...")
        hyp = run_hypothesis_tests(df, diesel_shock_threshold_pct=shock_threshold)
        for res in hyp["results"]:
            status_str = "REJECT H0" if res["reject_null"] else "FAIL TO REJECT H0"
            print(f"\n  [{res['hypothesis_code']}] {res['title']}")
            print(f"    Test: {res['test_used']} (N={res['sample_size']})")
            print(f"    Test Stat: {res['test_statistic']} | P-value: {res['p_value']}")
            print(f"    Outcome: {status_str} (alpha={res['significance_level']})")
            print(f"    Plain English: {res['verdict_plain_english']}")

        # Step 6: SARIMAX Forecasting & Advisory-Stress Classification
        print("\n[STEP 6/7] Fitting SARIMAX Model & Forecasting Advisory Stress...")
        fc = generate_forecast(db, state=state, commodity=commodity, horizon_days=horizon_days, use_sarimax=True)
        print(f"  Model Selected: {fc['model_name']}")
        print(f"  Evaluation Metrics: MAE = {fc['mae']}, RMSE = {fc['rmse']}, MAPE = {fc['mape']}%")
        stress = fc["stress_assessment"]
        print(f"  Advisory Stress Classification: [{stress['category'].upper()}]")
        print(f"  Details: {stress['explanation']}")
        print(f"  Evaluation Charts Saved -> outputs/charts/forecast_evaluation.png & actual_vs_predicted.png")
        print(f"  Forecast Tables Saved  -> outputs/forecasts/forecast_predictions.csv & forecast_evaluation_metrics.csv")

        # Step 7: Research Summary Report
        print("\n[STEP 7/7] Compiling Comprehensive Research Summary Report...")
        rep = generate_summary_report(db)
        print(f"  Full research report generated: {rep['report_path']}")
        print("\n=================================================================")
        print("          PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        print("=================================================================")

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="AgriStress Analytics Research Pipeline Runner")
    parser.add_argument("--state", type=str, default=None, help="Optional state filter (e.g., 'Maharashtra')")
    parser.add_argument("--commodity", type=str, default=None, help="Optional commodity filter (e.g., 'Onion')")
    parser.add_argument("--horizon", type=int, default=14, help="Forecast horizon in days (default: 14)")
    parser.add_argument("--shock-threshold", type=float, default=1.5, help="Diesel percentage shock threshold (default: 1.5%%)")
    args = parser.parse_args()

    run_pipeline(
        state=args.state,
        commodity=args.commodity,
        horizon_days=args.horizon,
        shock_threshold=args.shock_threshold
    )


if __name__ == "__main__":
    main()
