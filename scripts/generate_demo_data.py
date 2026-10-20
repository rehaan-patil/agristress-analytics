"""
Generates deterministic synthetic demo datasets (seed=42) for local demonstration.
POLICY: Strictly fictional development data for offline demonstration.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import DATA_DIR


def generate_synthetic_data(seed: int = 42, days: int = 730):
    np.random.seed(seed)
    synthetic_dir = DATA_DIR / "synthetic"
    synthetic_dir.mkdir(parents=True, exist_ok=True)

    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(days)]
    regions = [
        {"state": "Maharashtra", "district": "Nashik", "market": "Pimpalgaon"},
        {"state": "Punjab", "district": "Ludhiana", "market": "Khanna"},
        {"state": "Uttar Pradesh", "district": "Varanasi", "market": "Varanasi Mandi"},
        {"state": "Madhya Pradesh", "district": "Indore", "market": "Indore Mandi"},
    ]
    commodities = ["Onion", "Wheat", "Tomato"]
    categories = ["Weather", "Plant Protection", "Market Information", "Fertilizer"]

    # 3. Fuel Prices (Diesel INR/Litre) — generate realistic price revision shocks
    fuel_rows = []
    diesel = 90.0
    shock_dates = set()
    for d in dates:
        if np.random.rand() < 0.06:  # Intermittent price revisions (~40 across 2 years)
            revision = np.random.choice([-2.5, -2.0, 2.0, 2.5, 3.0])
            diesel = max(75.0, min(110.0, diesel + revision))
            shock_dates.add(d.strftime("%Y-%m-%d"))
        for reg in regions:
            fuel_rows.append({
                "observation_date": d.strftime("%Y-%m-%d"),
                "state": reg["state"],
                "diesel_price": round(diesel + (2.0 if reg["state"] == "Maharashtra" else 0.0), 2)
            })
    pd.DataFrame(fuel_rows).to_csv(synthetic_dir / "synthetic_fuel_prices.csv", index=False)

    # 1. KCC Queries (incorporating seasonal monsoon, weekly cycle, and subtle shock responsiveness)
    kcc_rows = []
    for d in dates:
        d_str = d.strftime("%Y-%m-%d")
        day_of_week = d.weekday()
        monsoon = 1.0 + 0.4 * np.sin(2 * np.pi * (d.timetuple().tm_yday - 120) / 365)
        dow_factor = 0.35 if day_of_week == 6 else 1.0
        # Fuel/market shock days prompt additional farmer advisory inquiries (+15%)
        shock_bump = 1.15 if d_str in shock_dates else 1.0
        for reg in regions:
            base = 80 if reg["state"] == "Maharashtra" else 60
            for cat in categories:
                mean_calls = max(2.0, base * monsoon * dow_factor * shock_bump / 4.0)
                kcc_rows.append({
                    "observation_date": d_str,
                    "state": reg["state"],
                    "district": reg["district"],
                    "query_type": cat,
                    "query_count": int(np.random.poisson(mean_calls))
                })
    pd.DataFrame(kcc_rows).to_csv(synthetic_dir / "synthetic_kcc_queries.csv", index=False)

    print(f"Generated synthetic demo files in {synthetic_dir}")


if __name__ == "__main__":
    generate_synthetic_data()
