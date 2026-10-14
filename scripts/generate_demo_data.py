"""
Generate realistic synthetic datasets for AgriStress Analytics local demonstration.

POLICY AND DISCLAIMER:
These datasets are explicitly fictional and generated using a fixed random seed.
They are provided solely for demonstrating database import, statistical analysis,
time-series forecasting, and API endpoints when offline or without live API keys.
They DO NOT represent official government statistics or validate empirical hypotheses.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Add project root directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import DATA_DIR


def generate_synthetic_data(seed: int = 42, days: int = 730):
    """
    Generates synthetic KCC queries, commodity mandi prices, and diesel fuel prices
    covering two calendar years (e.g., 2024-01-01 to 2025-12-31).
    """
    np.random.seed(seed)
    synthetic_folder = DATA_DIR / "synthetic"
    synthetic_folder.mkdir(parents=True, exist_ok=True)

    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(days)]

    regions = [
        {"state": "Maharashtra", "district": "Nashik", "market": "Pimpalgaon"},
        {"state": "Punjab", "district": "Ludhiana", "market": "Khanna"},
        {"state": "Uttar Pradesh", "district": "Varanasi", "market": "Varanasi Mandi"},
        {"state": "Madhya Pradesh", "district": "Indore", "market": "Indore Mandi"},
    ]

    commodities = ["Onion", "Wheat", "Tomato"]
    query_categories = ["Weather", "Plant Protection", "Market Information", "Fertilizer"]

    print(f"Generating synthetic data for {days} days across {len(regions)} regions...")

    # -------------------------------------------------------------
    # 1. Synthetic KCC Queries
    # -------------------------------------------------------------
    kcc_rows = []
    for d_idx, current_date in enumerate(dates):
        day_of_week = current_date.weekday()  # 0=Monday, 6=Sunday
        day_of_year = current_date.timetuple().tm_yday
        date_str = current_date.strftime("%Y-%m-%d")

        # Annual monsoon seasonality: query peak during July-August (monsoon & sowing)
        monsoon_seasonal_factor = 1.0 + 0.4 * np.sin(2 * np.pi * (day_of_year - 120) / 365)

        # Weekly cycle: fewer queries on Sundays due to call centre schedule
        day_factor = 0.35 if day_of_week == 6 else (0.75 if day_of_week == 5 else 1.1)

        for reg in regions:
            # Base query volume varies by state agricultural area
            base_state_demand = 85 if reg["state"] == "Maharashtra" else (
                70 if reg["state"] == "Uttar Pradesh" else 55
            )

            for cat in query_categories:
                # Category weighting
                cat_weight = 1.3 if cat in ["Plant Protection", "Market Information"] else 0.8
                mean_queries = base_state_demand * monsoon_seasonal_factor * day_factor * cat_weight / 4.0
                
                # Poisson distributed call count
                count = int(np.random.poisson(max(2.0, mean_queries)))

                kcc_rows.append({
                    "observation_date": date_str,
                    "state": reg["state"],
                    "district": reg["district"],
                    "query_type": cat,
                    "query_count": count
                })

    df_kcc = pd.DataFrame(kcc_rows)
    kcc_path = synthetic_folder / "synthetic_kcc_queries.csv"
    df_kcc.to_csv(kcc_path, index=False)
    print(f"  Saved {len(df_kcc):,} KCC records -> {kcc_path}")

    # -------------------------------------------------------------
    # 2. Synthetic Agricultural Commodity Mandi Prices
    # -------------------------------------------------------------
    commodity_rows = []
    # Initialize base prices (wholesale INR/Quintal)
    current_prices = {
        "Onion": 2200.0,
        "Wheat": 2400.0,
        "Tomato": 1800.0
    }

    for current_date in dates:
        day_of_week = current_date.weekday()
        # APMC mandis are closed on Sundays
        if day_of_week == 6:
            continue

        date_str = current_date.strftime("%Y-%m-%d")

        for comm in commodities:
            # Random walk with mean reversion for wholesale price
            drift = np.random.normal(0, 35.0)
            current_prices[comm] = max(800.0, current_prices[comm] + drift)
            wholesale = round(current_prices[comm], 2)

            # Retail price per quintal (wholesale + retail margin + transportation)
            # Retail margin is typically 25% - 40% above wholesale
            retail_margin_pct = np.random.uniform(0.25, 0.45)
            retail = round(wholesale * (1.0 + retail_margin_pct), 2)

            # Mandi arrivals (metric tonnes)
            arrival_tonnes = round(float(np.random.gamma(shape=5.0, scale=20.0)), 2)

            for reg in regions:
                # Add regional price variation
                regional_diff = np.random.uniform(-80.0, 80.0)
                reg_wholesale = round(max(500.0, wholesale + regional_diff), 2)
                reg_retail = round(reg_wholesale * (1.0 + retail_margin_pct), 2)

                commodity_rows.append({
                    "observation_date": date_str,
                    "state": reg["state"],
                    "district": reg["district"],
                    "market": reg["market"],
                    "commodity": comm,
                    "wholesale_price": reg_wholesale,
                    "retail_price": reg_retail,
                    "arrival_quantity": arrival_tonnes
                })

    df_comm = pd.DataFrame(commodity_rows)
    comm_path = synthetic_folder / "synthetic_commodity_prices.csv"
    df_comm.to_csv(comm_path, index=False)
    print(f"  Saved {len(df_comm):,} Commodity records -> {comm_path}")

    # -------------------------------------------------------------
    # 3. Synthetic Fuel (Diesel) Prices
    # -------------------------------------------------------------
    fuel_rows = []
    base_diesel = 90.0

    for current_date in dates:
        date_str = current_date.strftime("%Y-%m-%d")

        # Diesel prices remain flat for days, then adjust with occasional policy revisions
        if np.random.rand() < 0.05:  # 5% chance of a fuel price shift
            shock = np.random.choice([-1.5, -0.8, 0.9, 1.8, 2.5])
            base_diesel = max(75.0, min(115.0, base_diesel + shock))

        for reg in regions:
            # State-level VAT produces slight interstate price differences
            state_vat_offset = {
                "Maharashtra": 2.50,
                "Punjab": -1.20,
                "Uttar Pradesh": 0.40,
                "Madhya Pradesh": 3.10
            }.get(reg["state"], 0.0)

            fuel_rows.append({
                "observation_date": date_str,
                "state": reg["state"],
                "diesel_price": round(base_diesel + state_vat_offset, 2)
            })

    df_fuel = pd.DataFrame(fuel_rows)
    fuel_path = synthetic_folder / "synthetic_fuel_prices.csv"
    df_fuel.to_csv(fuel_path, index=False)
    print(f"  Saved {len(df_fuel):,} Fuel records -> {fuel_path}")

    print("\n[SUCCESS] Synthetic demonstration datasets generated successfully!")
    print(f"Directory: {synthetic_folder}")


if __name__ == "__main__":
    generate_synthetic_data(seed=42, days=730)
