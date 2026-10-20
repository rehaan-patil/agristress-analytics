"""
Generates an independent test dataset for functional verification of AgriStress Analytics.
Scenario: Summer 2023 Karnataka Tomato Price Collapse & Advisory Influx Crisis.
Clearly labeled as SYNTHETIC TEST DATA.
"""
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

def generate_independent_test_dataset():
    out_dir = Path(__file__).resolve().parent / "test_data"
    out_dir.mkdir(parents=True, exist_ok=True)

    np.random.seed(999)  # Distinct seed
    start_date = datetime(2023, 5, 1)
    n_days = 100
    dates = [start_date + timedelta(days=i) for i in range(n_days)]

    state = "Karnataka"
    district = "Kolar"
    market = "Kolar APMC"
    commodity = "Tomato"

    # 1. Fuel Prices (Diesel in Karnataka)
    fuel_records = []
    base_diesel = 86.50
    shock_dates = set()
    for d in dates:
        d_str = d.strftime("%Y-%m-%d")
        # Specific price shocks in late June and July
        if d_str in ["2023-06-15", "2023-07-02", "2023-07-20"]:
            base_diesel += 2.80
            shock_dates.add(d_str)
        elif d_str in ["2023-06-25", "2023-07-12"]:
            base_diesel -= 1.50
            shock_dates.add(d_str)

        fuel_records.append({
            "observation_date": d_str,
            "state": state,
            "diesel_price": round(base_diesel + np.random.normal(0, 0.05), 2)
        })

    df_fuel = pd.DataFrame(fuel_records)
    fuel_path = out_dir / "independent_test_fuel.csv"
    df_fuel.to_csv(fuel_path, index=False)

    # 2. Mandi Commodity Prices (Tomato Price Collapse)
    comm_records = []
    w_price = 3000.0
    for idx, d in enumerate(dates):
        d_str = d.strftime("%Y-%m-%d")
        if d.weekday() == 6:  # Sunday Mandi closed
            continue

        if idx < 40:
            # Stable pre-crisis period
            w_price = max(2600.0, min(3300.0, w_price + np.random.normal(-5, 40)))
            r_price = round(w_price * 1.25, 2)
            arrivals = round(float(np.random.gamma(4.0, 15.0)), 2)
        else:
            # Crisis period: severe collapse in wholesale farmgate price
            w_price = max(450.0, w_price - np.random.uniform(30.0, 75.0))
            # Retail price remains sticky downwards
            r_price = round(max(1800.0, 2400.0 + np.random.normal(0, 50)), 2)
            # Glut of arrivals
            arrivals = round(float(np.random.gamma(8.0, 25.0)), 2)

        comm_records.append({
            "observation_date": d_str,
            "state": state,
            "district": district,
            "market": market,
            "commodity": commodity,
            "wholesale_price": round(w_price, 2),
            "retail_price": r_price,
            "arrival_quantity": arrivals
        })

    df_comm = pd.DataFrame(comm_records)
    comm_path = out_dir / "independent_test_commodity.csv"
    df_comm.to_csv(comm_path, index=False)

    # 3. KCC Queries (Inquiries surge during price collapse)
    kcc_records = []
    categories = ["Market Information", "Plant Protection", "Weather", "Government Schemes"]
    for idx, d in enumerate(dates):
        d_str = d.strftime("%Y-%m-%d")
        dow = d.weekday()
        dow_factor = 0.25 if dow == 6 else 1.0

        if idx < 40:
            # Normal baseline call volume
            base_calls = 25.0 * dow_factor
        else:
            # Massive call influx due to distressed tomato farmers
            # Call volume escalates as price drops deeper
            crisis_severity = (idx - 40) / 60.0
            base_calls = (35.0 + 190.0 * crisis_severity) * dow_factor

        for cat in categories:
            cat_mult = 1.6 if cat in ["Market Information", "Government Schemes"] else 0.8
            mean_q = max(1.0, (base_calls * cat_mult) / len(categories))
            calls = int(np.random.poisson(mean_q))
            kcc_records.append({
                "observation_date": d_str,
                "state": state,
                "district": district,
                "query_type": cat,
                "query_count": calls
            })

    df_kcc = pd.DataFrame(kcc_records)
    kcc_path = out_dir / "independent_test_kcc.csv"
    df_kcc.to_csv(kcc_path, index=False)

    print(f"[OK] Generated Independent Test Dataset in {out_dir}:")
    print(f"  - KCC Queries:   {len(df_kcc):,} rows ({kcc_path.name})")
    print(f"  - Commodity:     {len(df_comm):,} rows ({comm_path.name})")
    print(f"  - Fuel:          {len(df_fuel):,} rows ({fuel_path.name})")

if __name__ == "__main__":
    generate_independent_test_dataset()
