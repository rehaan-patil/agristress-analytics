"""
CLI script to import KCC, Commodity, and Fuel CSV datasets into the database.
"""
import sys
import argparse
from pathlib import Path

# Add project root directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.config import DATA_DIR
from app.data_processing import (
    import_kcc_csv,
    import_commodity_csv,
    import_fuel_csv,
    get_dataset_status,
)


def run_imports(args):
    db = SessionLocal()
    try:
        # Check status flag
        if args.status:
            status = get_dataset_status(db)
            print("\n=== CURRENT DATASET STATUS ===")
            print(f"Overall Status: {status['status']}")
            for k, v in status["datasets"].items():
                print(f"  [{k.upper()}] Records: {v['total_records']}, Range: {v['min_date']} to {v['max_date']}, States: {v['states_count']}, Synthetic: {v['is_synthetic']}")
            for note in status["notes"]:
                print(f"  * Note: {note}")
            return

        # Import all synthetic demo files
        if args.all:
            synthetic_dir = DATA_DIR / "synthetic"
            kcc_path = synthetic_dir / "synthetic_kcc_queries.csv"
            comm_path = synthetic_dir / "synthetic_commodity_prices.csv"
            fuel_path = synthetic_dir / "synthetic_fuel_prices.csv"

            if not kcc_path.exists():
                print("Synthetic files not found! Please run 'python scripts/generate_demo_data.py' first.")
                return

            print(f"Importing synthetic KCC dataset: {kcc_path.name}")
            res_kcc = import_kcc_csv(kcc_path, db, filename=kcc_path.name, is_synthetic=True)
            print(f"  Accepted: {res_kcc['accepted_rows']}, Rejected: {res_kcc['rejected_rows']}, Duplicates: {res_kcc['duplicate_rows']}")

            print(f"Importing synthetic Commodity dataset: {comm_path.name}")
            res_comm = import_commodity_csv(comm_path, db, filename=comm_path.name, is_synthetic=True)
            print(f"  Accepted: {res_comm['accepted_rows']}, Rejected: {res_comm['rejected_rows']}, Duplicates: {res_comm['duplicate_rows']}")

            print(f"Importing synthetic Fuel dataset: {fuel_path.name}")
            res_fuel = import_fuel_csv(fuel_path, db, filename=fuel_path.name, is_synthetic=True)
            print(f"  Accepted: {res_fuel['accepted_rows']}, Rejected: {res_fuel['rejected_rows']}, Duplicates: {res_fuel['duplicate_rows']}")

            print("\n[SUCCESS] All demo datasets imported successfully!")
            return

        # Specific file imports
        if args.kcc:
            path = Path(args.kcc)
            print(f"Importing KCC file: {path}")
            res = import_kcc_csv(path, db, filename=path.name, is_synthetic=args.synthetic)
            print(f"Result: {res['status']} | Accepted: {res['accepted_rows']} | Rejected: {res['rejected_rows']}")

        if args.commodity:
            path = Path(args.commodity)
            print(f"Importing Commodity file: {path}")
            res = import_commodity_csv(path, db, filename=path.name, is_synthetic=args.synthetic)
            print(f"Result: {res['status']} | Accepted: {res['accepted_rows']} | Rejected: {res['rejected_rows']}")

        if args.fuel:
            path = Path(args.fuel)
            print(f"Importing Fuel file: {path}")
            res = import_fuel_csv(path, db, filename=path.name, is_synthetic=args.synthetic)
            print(f"Result: {res['status']} | Accepted: {res['accepted_rows']} | Rejected: {res['rejected_rows']}")

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="AgriStress Analytics CSV Importer")
    parser.add_argument("--all", action="store_true", help="Import all demo synthetic CSVs from data/synthetic/")
    parser.add_argument("--kcc", type=str, help="Path to KCC query CSV file")
    parser.add_argument("--commodity", type=str, help="Path to Mandi commodity price CSV file")
    parser.add_argument("--fuel", type=str, help="Path to Diesel fuel price CSV file")
    parser.add_argument("--synthetic", action="store_true", help="Mark imported records as synthetic")
    parser.add_argument("--status", action="store_true", help="Print current database summary status")

    args = parser.parse_args()
    if not (args.all or args.kcc or args.commodity or args.fuel or args.status):
        parser.print_help()
        sys.exit(1)

    run_imports(args)


if __name__ == "__main__":
    main()
