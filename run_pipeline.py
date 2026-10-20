"""
========================================================================================
AGRISTRESS ANALYTICS — MAIN PIPELINE RUNNER
========================================================================================

Complete end-to-end reproducible research pipeline.
One simple command reproduces the entire analytical workflow:
    python run_pipeline.py

Designed for intermediate engineering student understanding and academic viva defense.
"""
import sys
import argparse
from pathlib import Path

# Ensure root directory is on Python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from app.database import engine, Base, SessionLocal
from app.config import OUTPUTS_DIR, DATA_DIR, TABLES_DIR, FORECASTS_DIR
import app.models  # Register models with SQLAlchemy Base
from app.data_processing import (
    build_analytical_dataset,
    get_dataset_status,
    get_data_quality_report,
    import_kcc_csv,
    import_commodity_csv,
    import_fuel_csv
)
from app.analysis import (
    generate_all_charts,
    run_hypothesis_tests,
    generate_summary_report,
    get_descriptive_summary,
    save_analysis_tables
)
from app.forecasting import generate_forecast
from scripts.generate_demo_data import generate_synthetic_data


def run_full_pipeline(
    state: str = None,
    commodity: str = None,
    horizon_days: int = 14,
    shock_threshold: float = 1.0,
    force_generate: bool = False
):
    print("=" * 72)
    print("       AGRISTRESS ANALYTICS — END-TO-END RESEARCH PIPELINE")
    print("=" * 72)
    print(f"Working Directory: {ROOT_DIR}")
    print(f"Outputs Folder:    {OUTPUTS_DIR}")

    # -------------------------------------------------------------
    # Step 1: Database Initialization
    # -------------------------------------------------------------
    print("\n[PHASE 1/5] Database Verification & Table Initialization...")
    if force_generate:
        print("  -> Dropping existing tables for clean re-import...")
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        status = get_dataset_status(db)
        needs_import = (
            force_generate
            or not status["ready_for_analysis"]
            or status["datasets"]["kcc"]["total_records"] < 30
        )

        if needs_import:
            print("  -> Generating deterministic synthetic demonstration dataset...")
            generate_synthetic_data(seed=42, days=730)

            synthetic_dir = DATA_DIR / "synthetic"
            print("  -> Importing synthetic KCC queries...")
            res_kcc = import_kcc_csv(synthetic_dir / "synthetic_kcc_queries.csv", db, filename="synthetic_kcc_queries.csv", is_synthetic=True)
            print(f"     Accepted: {res_kcc['accepted_rows']:,} | Duplicates: {res_kcc['duplicate_rows']:,}")

            print("  -> Importing synthetic Mandi commodity prices...")
            res_comm = import_commodity_csv(synthetic_dir / "synthetic_commodity_prices.csv", db, filename="synthetic_commodity_prices.csv", is_synthetic=True)
            print(f"     Accepted: {res_comm['accepted_rows']:,} | Duplicates: {res_comm['duplicate_rows']:,}")

            print("  -> Importing synthetic Retail diesel fuel prices...")
            res_fuel = import_fuel_csv(synthetic_dir / "synthetic_fuel_prices.csv", db, filename="synthetic_fuel_prices.csv", is_synthetic=True)
            print(f"     Accepted: {res_fuel['accepted_rows']:,} | Duplicates: {res_fuel['duplicate_rows']:,}")

            status = get_dataset_status(db)

        print(f"  [OK] Database Ready: {status['status']}")
        for name, info in status["datasets"].items():
            print(f"       - {name.upper():<10}: {info['total_records']:,} rows ({info['min_date']} to {info['max_date']})")

        # -------------------------------------------------------------
        # Step 2: Harmonize Analytical Dataset & Quality Audit
        # -------------------------------------------------------------
        print("\n[PHASE 2/5] Building Aligned Analytical Time-Series & Quality Audit...")
        df = build_analytical_dataset(db, state=state, commodity=commodity, export_csv=True)
        quality = get_data_quality_report(db, df)
        print(f"  [OK] Constructed {len(df):,} harmonized daily records.")
        print(f"       Sample Range: {quality['sample_start']} to {quality['sample_end']}")
        print(f"       Observed Days: {quality['observed_query_days']} | Missing/Zero Query Days: {quality['zero_or_unrecorded_days']} ({quality['missingness_percentage']}%)")
        print(f"       Data Quality: {quality['quality_status']} | Provenance: {'Synthetic' if quality['is_synthetic'] else 'Real'}")
        print("       Exported -> data/processed/analytical_dataset.csv")

        # -------------------------------------------------------------
        # Step 3: Descriptive Statistics & Exporting Result Tables
        # -------------------------------------------------------------
        print("\n[PHASE 3/5] Computing Descriptive Statistics & Saving CSV Tables...")
        summary = get_descriptive_summary(df)
        for stat in summary["descriptive_statistics"]:
            print(f"  * {stat['variable']:<25}: Mean = {stat['mean']:<8} Std = {stat['std']:<8} [Min: {stat['min']}, Max: {stat['max']}]")

        tables = save_analysis_tables(df, db)
        print(f"  [OK] Exported {len(tables)} result tables to outputs/tables/:")
        for k, v in tables.items():
            print(f"       - {Path(v).name}")

        # -------------------------------------------------------------
        # Step 4: Exploratory Visualizations & Econometric Hypothesis Testing
        # -------------------------------------------------------------
        print("\n[PHASE 4/5] Generating Visualizations & Running Hypothesis Tests...")
        charts = generate_all_charts(db)
        print(f"  [OK] Generated {len(charts)} exploratory charts in outputs/charts/:")
        for c in charts:
            print(f"       - {Path(c).name}")

        hyp = run_hypothesis_tests(df, diesel_shock_threshold_pct=shock_threshold)
        print("\n  Econometric Hypothesis Outcomes:")
        for res in hyp["results"]:
            badge = "[REJECT H0]" if res["reject_null"] else "[FAIL TO REJECT]"
            print(f"    * {res['hypothesis_code']} ({res['title']}): {badge}")
            print(f"      Test: {res['test_used']} | Stat: {res['test_statistic']} | p-value: {res['p_value']}")
            print(f"      Verdict: {res['verdict_plain_english']}")

        # -------------------------------------------------------------
        # Step 5: Time-Series Forecasting & Summary Report Compilation
        # -------------------------------------------------------------
        print("\n[PHASE 5/5] Fitting Forecast Models, Evaluating Holdout, & Compiling Report...")
        fc = generate_forecast(db, state=state, commodity=commodity, horizon_days=horizon_days, use_sarimax=True)
        stress = fc["stress_assessment"]

        base_m = fc.get("baseline_metrics", {})
        print(f"  [OK] Forecasting Complete:")
        print(f"       - Selected Model: {fc['model_name']}")
        print(f"       - Baseline (7D Seasonal Naive): MAE = {base_m.get('mae')} | RMSE = {base_m.get('rmse')}")
        print(f"       - Selected Model Evaluation:    MAE = {fc.get('mae')} | RMSE = {fc.get('rmse')} | MAPE = {fc.get('mape')}%")
        print(f"       - Advisory Stress Category:     [{stress['category'].upper()}] ({stress['explanation']})")
        print("       - Charts Saved: outputs/charts/forecast_evaluation.png & actual_vs_predicted.png")
        print("       - Tables Saved: outputs/forecasts/forecast_predictions.csv & forecast_evaluation_metrics.csv")

        rep = generate_summary_report(db)
        print(f"\n  [OK] Full Research Summary Report Generated:")
        print(f"       -> {rep['report_path']}")

        print("\n" + "=" * 72)
        print("          ALL PIPELINE STAGES COMPLETED SUCCESSFULLY!")
        print("=" * 72)
        print(f"Review the markdown summary report at: {rep['report_path']}\n")

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="AgriStress Analytics — Automated Research Pipeline Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python run_pipeline.py
  python run_pipeline.py --generate-data
  python run_pipeline.py --state Maharashtra --commodity Onion --horizon 21
"""
    )
    parser.add_argument("--generate-data", action="store_true", help="Force regenerate synthetic demo data and re-import into database")
    parser.add_argument("--state", type=str, default=None, help="Filter by state (e.g., 'Maharashtra', 'Punjab')")
    parser.add_argument("--commodity", type=str, default=None, help="Filter by commodity (e.g., 'Onion', 'Wheat', 'Tomato')")
    parser.add_argument("--horizon", type=int, default=14, help="Forecast horizon in days (default: 14)")
    parser.add_argument("--shock-threshold", type=float, default=1.0, help="Diesel percentage shock threshold (default: 1.0%%)")

    args = parser.parse_args()
    run_full_pipeline(
        state=args.state,
        commodity=args.commodity,
        horizon_days=args.horizon,
        shock_threshold=args.shock_threshold,
        force_generate=args.generate_data
    )


if __name__ == "__main__":
    main()
