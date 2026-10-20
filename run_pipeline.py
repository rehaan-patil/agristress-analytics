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

# Configure utf-8 console output for Windows cmd/powershell
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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
from app.recommendations import generate_farmer_recommendations
from scripts.generate_demo_data import generate_synthetic_data


def run_full_pipeline(
    state: str = None,
    commodity: str = None,
    horizon_days: int = 14,
    shock_threshold: float = 1.0,
    force_generate: bool = False,
    kcc_file: str = None,
    commodity_file: str = None,
    fuel_file: str = None,
    replace: bool = False,
    is_synthetic: bool = False,
    verified_real: bool = False,
    lang: str = "en"
):
    print("=" * 72)
    print("       AGRISTRESS ANALYTICS — END-TO-END RESEARCH PIPELINE")
    print("=" * 72)
    print(f"Working Directory: {ROOT_DIR}")
    print(f"Outputs Folder:    {OUTPUTS_DIR}")

    # -------------------------------------------------------------
    # Step 1: Database Initialization & Data Loading
    # -------------------------------------------------------------
    print("\n[PHASE 1/5] Database Verification & Table Initialization...")
    if force_generate or (replace and not (kcc_file or commodity_file or fuel_file)):
        print("  -> Dropping existing tables for clean re-import...")
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        custom_inputs_supplied = bool(kcc_file or commodity_file or fuel_file)
        if is_synthetic or force_generate or not custom_inputs_supplied:
            provenance_type = "SYNTHETIC"
        elif verified_real:
            provenance_type = "VERIFIED_REAL"
        else:
            provenance_type = "UNVERIFIED"

        import_synth_flag = (provenance_type == "SYNTHETIC")

        # 1A. Import custom user-supplied CSV files if specified
        if custom_inputs_supplied:
            print(f"  -> Importing user-supplied custom CSV datasets (Provenance: {provenance_type})...")
            if kcc_file:
                p_kcc = Path(kcc_file)
                print(f"     Loading KCC: {p_kcc} (replace={replace}, synthetic={import_synth_flag})")
                res = import_kcc_csv(p_kcc, db, filename=p_kcc.name, is_synthetic=import_synth_flag, replace=replace)
                print(f"     Result: {res['status']} | Accepted: {res['accepted_rows']:,} | Rejected: {res['rejected_rows']:,}")

            if commodity_file:
                p_comm = Path(commodity_file)
                print(f"     Loading Commodity: {p_comm} (replace={replace}, synthetic={import_synth_flag})")
                res = import_commodity_csv(p_comm, db, filename=p_comm.name, is_synthetic=import_synth_flag, replace=replace)
                print(f"     Result: {res['status']} | Accepted: {res['accepted_rows']:,} | Rejected: {res['rejected_rows']:,}")

            if fuel_file:
                p_fuel = Path(fuel_file)
                print(f"     Loading Fuel: {p_fuel} (replace={replace}, synthetic={import_synth_flag})")
                res = import_fuel_csv(p_fuel, db, filename=p_fuel.name, is_synthetic=import_synth_flag, replace=replace)
                print(f"     Result: {res['status']} | Accepted: {res['accepted_rows']:,} | Rejected: {res['rejected_rows']:,}")

            status = get_dataset_status(db)

        # 1B. Fall back to synthetic demonstration generator only if requested or db is empty
        else:
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
                res_kcc = import_kcc_csv(synthetic_dir / "synthetic_kcc_queries.csv", db, filename="synthetic_kcc_queries.csv", is_synthetic=True, replace=True)
                print(f"     Accepted: {res_kcc['accepted_rows']:,} | Duplicates: {res_kcc['duplicate_rows']:,}")

                print("  -> Importing synthetic Mandi commodity prices...")
                res_comm = import_commodity_csv(synthetic_dir / "synthetic_commodity_prices.csv", db, filename="synthetic_commodity_prices.csv", is_synthetic=True, replace=True)
                print(f"     Accepted: {res_comm['accepted_rows']:,} | Duplicates: {res_comm['duplicate_rows']:,}")

                print("  -> Importing synthetic Retail diesel fuel prices...")
                res_fuel = import_fuel_csv(synthetic_dir / "synthetic_fuel_prices.csv", db, filename="synthetic_fuel_prices.csv", is_synthetic=True, replace=True)
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
        quality = get_data_quality_report(db, df, provenance_type=provenance_type)
        print(f"  [OK] Constructed {len(df):,} harmonized daily records.")
        print(f"       Sample Range: {quality['sample_start']} to {quality['sample_end']}")
        print(f"       Observed Days: {quality['observed_query_days']} | Missing/Zero Query Days: {quality['zero_or_unrecorded_days']} ({quality['missingness_percentage']}%)")
        print(f"       Data Quality: {quality['quality_status']} | Provenance: {quality['provenance_label']}")
        print("       Exported -> data/processed/analytical_dataset.csv")
        print("       Exported -> data/processed/analytical_dataset.csv")

        # -------------------------------------------------------------
        # Step 3: Descriptive Statistics & Exporting Result Tables
        # -------------------------------------------------------------
        print("\n[PHASE 3/5] Computing Descriptive Statistics & Saving CSV Tables...")
        summary = get_descriptive_summary(df)
        for stat in summary["descriptive_statistics"]:
            print(f"  * {stat['variable']:<25}: Mean = {stat['mean']:<8} Std = {stat['std']:<8} [Min: {stat['min']}, Max: {stat['max']}]")

        tables = save_analysis_tables(df, db, diesel_shock_threshold_pct=shock_threshold)
        print(f"  [OK] Exported {len(tables)} result tables to outputs/tables/:")
        for k, v in tables.items():
            print(f"       - {Path(v).name}")

        # -------------------------------------------------------------
        # Step 4: Exploratory Visualizations & Econometric Hypothesis Testing
        # -------------------------------------------------------------
        print("\n[PHASE 4/5] Generating Visualizations & Running Hypothesis Tests...")
        charts = generate_all_charts(db, state=state, commodity=commodity, df=df)
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

        rep = generate_summary_report(
            db,
            state=state,
            commodity=commodity,
            horizon_days=horizon_days,
            shock_threshold=shock_threshold,
            df=df,
            fc=fc,
            hyp_data=hyp,
            charts=charts,
            tables=tables
        )
        print(f"\n  [OK] Full Research Summary Report Generated:")
        print(f"       -> {rep['report_path']}")

        # -------------------------------------------------------------
        # Step 6: Plain-Language Farmer Advisory Generation
        # -------------------------------------------------------------
        print("\n[PHASE 6/6] Generating Plain-Language Farmer Advisory & Action Plan...")
        advisory = generate_farmer_recommendations(
            df=df,
            forecast_res=fc,
            state=state,
            commodity=commodity,
            quality=quality,
            db=db,
            lang=lang
        )
        print(f"  [OK] Farmer Advisory Reports Generated:")
        print(f"       -> Markdown:   {advisory['report_md_path']}")
        print(f"       -> Plain Text: {advisory['report_txt_path']}")

        print("\n" + "=" * 72)
        print("          ALL PIPELINE STAGES COMPLETED SUCCESSFULLY!")
        print("=" * 72)
        print("\n" + "-" * 72)
        print("             FARMER-FRIENDLY ADVISORY SUMMARY")
        print("-" * 72)
        print(f"  Region:            {advisory['region']}")
        print(f"  Commodity:         {advisory['commodity']}")
        print(f"  Data Period:       {advisory['period']}")
        print(f"  Data Freshness:    {advisory['freshness']['statement']}")
        print(f"  Advisory Priority: {advisory['priority']}")
        print(f"\n  Situation:")
        print(f"    {advisory['price_headline']}")
        print(f"\n  Recommended Next Steps:")
        for idx, step in enumerate(advisory["recommended_steps"], start=1):
            print(f"    {idx}. {step}")
        if advisory.get("market_comparison_available"):
            print(f"\n  Market Comparison: {advisory['market_comparison_count']} mandis evaluated in report table.")
        print(f"\n  Assistance: Call Kisan Call Centre (Toll-Free 1800-180-1551, 6:00 AM - 10:00 PM)")
        print(f"  Provenance: {advisory['provenance_label']}")
        print("-" * 72)
        print(f"\nTechnical Report: {rep['report_path']}")
        print(f"Farmer Advisory:  {advisory['report_md_path']}\n")

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
  python run_pipeline.py --kcc my_kcc.csv --commodity-file my_mandi.csv --fuel my_fuel.csv --replace
  python run_pipeline.py --lang hi
"""
    )
    parser.add_argument("--generate-data", action="store_true", help="Force regenerate synthetic demo data and re-import into database")
    parser.add_argument("--kcc", type=str, default=None, help="Path to custom KCC query CSV file")
    parser.add_argument("--commodity-file", "--commodity-csv", dest="commodity_file", type=str, default=None, help="Path to custom Mandi commodity price CSV file")
    parser.add_argument("--fuel", type=str, default=None, help="Path to custom Diesel fuel price CSV file")
    parser.add_argument("--replace", action="store_true", help="Replace existing records in database before importing custom data")
    parser.add_argument("--synthetic", action="store_true", help="Mark custom imported data as synthetic demonstration data")
    parser.add_argument("--verified-real", action="store_true", help="Mark custom imported data as verified real-world operational records")
    parser.add_argument("--state", type=str, default=None, help="Filter by state (e.g., 'Maharashtra', 'Punjab')")
    parser.add_argument("--commodity", type=str, default=None, help="Filter by commodity (e.g., 'Onion', 'Wheat', 'Tomato')")
    parser.add_argument("--horizon", type=int, default=14, help="Forecast horizon in days (default: 14)")
    parser.add_argument("--shock-threshold", type=float, default=1.0, help="Diesel percentage shock threshold (default: 1.0%%)")
    parser.add_argument("--lang", type=str, default="en", choices=["en", "hi", "mr"], help="Language for farmer advisory ('en', 'hi', 'mr')")

    args = parser.parse_args()

    # If user provided a CSV path to --commodity instead of a commodity name, handle gracefully
    commodity_filter = args.commodity
    comm_file = args.commodity_file
    if commodity_filter and commodity_filter.lower().endswith(".csv"):
        if not comm_file:
            comm_file = commodity_filter
            commodity_filter = None

    run_full_pipeline(
        state=args.state,
        commodity=commodity_filter,
        horizon_days=args.horizon,
        shock_threshold=args.shock_threshold,
        force_generate=args.generate_data,
        kcc_file=args.kcc,
        commodity_file=comm_file,
        fuel_file=args.fuel,
        replace=args.replace,
        is_synthetic=args.synthetic,
        verified_real=args.verified_real,
        lang=args.lang
    )


if __name__ == "__main__":
    main()
