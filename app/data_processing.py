"""
Data Processing and Feature Engineering for AgriStress Analytics.

Written in straightforward, student-friendly Python using Pandas and SQLAlchemy.
Implements CSV validation, database ingestion, feature engineering, and temporal alignment.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import DATA_DIR
from app.models import KCCObservation, CommodityObservation, FuelObservation, ImportHistory


# =====================================================================
# 1. HELPER FUNCTIONS FOR CSV VALIDATION
# =====================================================================

def check_missing_columns(df: pd.DataFrame, required_columns: List[str]) -> List[str]:
    """Returns a list of required columns that are missing from the dataframe."""
    existing_lower = [str(c).strip().lower() for c in df.columns]
    missing = []
    for req in required_columns:
        if req.lower() not in existing_lower:
            missing.append(req)
    return missing


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes column names to lowercase with underscores and stripped whitespace."""
    clean_cols = {}
    for col in df.columns:
        clean_name = str(col).strip().lower().replace(" ", "_").replace("-", "_")
        clean_cols[col] = clean_name
    return df.rename(columns=clean_cols)


def safe_parse_dates(series: pd.Series) -> pd.Series:
    """Parses date strings safely into datetime.date objects, returning NaT for invalid formats."""
    parsed = pd.to_datetime(series, errors="coerce", format="mixed")
    return parsed.dt.date


# =====================================================================
# 2. CSV INGESTION FUNCTIONS
# =====================================================================

def import_kcc_csv(
    file_or_path,
    db: Session,
    filename: str = "kcc_data.csv",
    is_synthetic: bool = False
) -> Dict[str, Any]:
    """
    Validates and imports Kisan Call Centre queries from CSV into the database.
    Expects at minimum: observation_date, state, query_count (or raw records).
    """
    try:
        df = pd.read_csv(file_or_path)
    except Exception as e:
        return {
            "status": "FAILED",
            "filename": filename,
            "total_rows": 0,
            "accepted_rows": 0,
            "rejected_rows": 0,
            "duplicate_rows": 0,
            "errors": [f"Could not read CSV file: {str(e)}"]
        }

    df = standardize_column_names(df)
    total_rows = len(df)

    required_cols = ["observation_date", "state"]
    missing = check_missing_columns(df, required_cols)
    if missing:
        err_msg = f"Missing required columns: {', '.join(missing)}. Found: {list(df.columns)}"
        # Log to import history
        hist = ImportHistory(
            dataset_type="kcc",
            filename=filename,
            total_records=total_rows,
            status="FAILED",
            notes=err_msg
        )
        db.add(hist)
        db.commit()
        return {
            "status": "FAILED",
            "filename": filename,
            "total_rows": total_rows,
            "accepted_rows": 0,
            "rejected_rows": total_rows,
            "duplicate_rows": 0,
            "errors": [err_msg]
        }

    # If query_count is not present, assume each row is 1 call transaction
    if "query_count" not in df.columns:
        df["query_count"] = 1
    else:
        df["query_count"] = pd.to_numeric(df["query_count"], errors="coerce")

    # Date parsing
    df["parsed_date"] = safe_parse_dates(df["observation_date"])

    # Identify valid vs rejected rows
    valid_mask = (
        df["parsed_date"].notna() &
        df["state"].notna() &
        (df["state"].str.strip() != "") &
        df["query_count"].notna() &
        (df["query_count"] >= 0)
    )

    rejected_rows = int((~valid_mask).sum())
    valid_df = df[valid_mask].copy()

    # Detect duplicates within the CSV batch (date, state, district, query_type)
    subset_cols = ["parsed_date", "state"]
    if "district" in valid_df.columns:
        subset_cols.append("district")
    if "query_type" in valid_df.columns:
        subset_cols.append("query_type")

    duplicate_mask = valid_df.duplicated(subset=subset_cols, keep="first")
    duplicate_rows = int(duplicate_mask.sum())
    final_df = valid_df[~duplicate_mask]

    accepted_rows = len(final_df)

    # Insert into database in sensible chunks
    objects_to_add = []
    for _, row in final_df.iterrows():
        obj = KCCObservation(
            observation_date=row["parsed_date"],
            state=str(row["state"]).strip(),
            district=str(row["district"]).strip() if "district" in row and pd.notna(row["district"]) else None,
            query_type=str(row["query_type"]).strip() if "query_type" in row and pd.notna(row["query_type"]) else None,
            query_count=int(row["query_count"]),
            is_synthetic=is_synthetic,
            source_ref=filename
        )
        objects_to_add.append(obj)

    db.bulk_save_objects(objects_to_add)

    # Log import history
    hist = ImportHistory(
        dataset_type="kcc",
        filename=filename,
        total_records=total_rows,
        accepted_records=accepted_rows,
        rejected_records=rejected_rows,
        duplicate_records=duplicate_rows,
        status="SUCCESS" if accepted_rows > 0 else "FAILED",
        notes=f"Accepted {accepted_rows}/{total_rows} records."
    )
    db.add(hist)
    db.commit()

    return {
        "status": "SUCCESS" if accepted_rows > 0 else "EMPTY",
        "dataset_type": "kcc",
        "filename": filename,
        "total_rows": total_rows,
        "accepted_rows": accepted_rows,
        "rejected_rows": rejected_rows,
        "duplicate_rows": duplicate_rows,
        "errors": []
    }


def import_commodity_csv(
    file_or_path,
    db: Session,
    filename: str = "commodity_prices.csv",
    is_synthetic: bool = False
) -> Dict[str, Any]:
    """
    Validates and imports Agricultural Commodity Mandi prices into the database.
    Expects at minimum: observation_date, state, commodity, wholesale_price.
    """
    try:
        df = pd.read_csv(file_or_path)
    except Exception as e:
        return {
            "status": "FAILED",
            "filename": filename,
            "total_rows": 0,
            "accepted_rows": 0,
            "rejected_rows": 0,
            "duplicate_rows": 0,
            "errors": [f"Could not read CSV file: {str(e)}"]
        }

    df = standardize_column_names(df)
    total_rows = len(df)

    required_cols = ["observation_date", "state", "commodity", "wholesale_price"]
    missing = check_missing_columns(df, required_cols)
    if missing:
        err_msg = f"Missing required columns: {', '.join(missing)}. Found: {list(df.columns)}"
        hist = ImportHistory(
            dataset_type="commodity",
            filename=filename,
            total_records=total_rows,
            status="FAILED",
            notes=err_msg
        )
        db.add(hist)
        db.commit()
        return {
            "status": "FAILED",
            "filename": filename,
            "total_rows": total_rows,
            "accepted_rows": 0,
            "rejected_rows": total_rows,
            "duplicate_rows": 0,
            "errors": [err_msg]
        }

    # Type casting
    df["parsed_date"] = safe_parse_dates(df["observation_date"])
    df["clean_wholesale"] = pd.to_numeric(df["wholesale_price"], errors="coerce")
    
    if "retail_price" in df.columns:
        df["clean_retail"] = pd.to_numeric(df["retail_price"], errors="coerce")
    else:
        df["clean_retail"] = None

    if "arrival_quantity" in df.columns:
        df["clean_arrival"] = pd.to_numeric(df["arrival_quantity"], errors="coerce")
    else:
        df["clean_arrival"] = None

    # Filter out invalid records (must have valid date, non-empty state, commodity, positive wholesale price)
    valid_mask = (
        df["parsed_date"].notna() &
        df["state"].notna() &
        (df["state"].str.strip() != "") &
        df["commodity"].notna() &
        (df["commodity"].str.strip() != "") &
        df["clean_wholesale"].notna() &
        (df["clean_wholesale"] > 0)
    )

    rejected_rows = int((~valid_mask).sum())
    valid_df = df[valid_mask].copy()

    subset_cols = ["parsed_date", "state", "commodity"]
    if "market" in valid_df.columns:
        subset_cols.append("market")

    duplicate_mask = valid_df.duplicated(subset=subset_cols, keep="first")
    duplicate_rows = int(duplicate_mask.sum())
    final_df = valid_df[~duplicate_mask]

    accepted_rows = len(final_df)

    objects_to_add = []
    for _, row in final_df.iterrows():
        obj = CommodityObservation(
            observation_date=row["parsed_date"],
            state=str(row["state"]).strip(),
            district=str(row["district"]).strip() if "district" in row and pd.notna(row["district"]) else None,
            market=str(row["market"]).strip() if "market" in row and pd.notna(row["market"]) else None,
            commodity=str(row["commodity"]).strip(),
            wholesale_price=float(row["clean_wholesale"]),
            retail_price=float(row["clean_retail"]) if pd.notna(row["clean_retail"]) else None,
            arrival_quantity=float(row["clean_arrival"]) if pd.notna(row["clean_arrival"]) else None,
            units="INR/Quintal",
            is_synthetic=is_synthetic,
            source_ref=filename
        )
        objects_to_add.append(obj)

    db.bulk_save_objects(objects_to_add)

    hist = ImportHistory(
        dataset_type="commodity",
        filename=filename,
        total_records=total_rows,
        accepted_records=accepted_rows,
        rejected_records=rejected_rows,
        duplicate_records=duplicate_rows,
        status="SUCCESS" if accepted_rows > 0 else "FAILED",
        notes=f"Accepted {accepted_rows}/{total_rows} records."
    )
    db.add(hist)
    db.commit()

    return {
        "status": "SUCCESS" if accepted_rows > 0 else "EMPTY",
        "dataset_type": "commodity",
        "filename": filename,
        "total_rows": total_rows,
        "accepted_rows": accepted_rows,
        "rejected_rows": rejected_rows,
        "duplicate_rows": duplicate_rows,
        "errors": []
    }


def import_fuel_csv(
    file_or_path,
    db: Session,
    filename: str = "fuel_prices.csv",
    is_synthetic: bool = False
) -> Dict[str, Any]:
    """
    Validates and imports Diesel fuel prices into the database.
    Expects at minimum: observation_date, diesel_price.
    """
    try:
        df = pd.read_csv(file_or_path)
    except Exception as e:
        return {
            "status": "FAILED",
            "filename": filename,
            "total_rows": 0,
            "accepted_rows": 0,
            "rejected_rows": 0,
            "duplicate_rows": 0,
            "errors": [f"Could not read CSV file: {str(e)}"]
        }

    df = standardize_column_names(df)
    total_rows = len(df)

    required_cols = ["observation_date", "diesel_price"]
    missing = check_missing_columns(df, required_cols)
    if missing:
        err_msg = f"Missing required columns: {', '.join(missing)}. Found: {list(df.columns)}"
        hist = ImportHistory(
            dataset_type="fuel",
            filename=filename,
            total_records=total_rows,
            status="FAILED",
            notes=err_msg
        )
        db.add(hist)
        db.commit()
        return {
            "status": "FAILED",
            "filename": filename,
            "total_rows": total_rows,
            "accepted_rows": 0,
            "rejected_rows": total_rows,
            "duplicate_rows": 0,
            "errors": [err_msg]
        }

    df["parsed_date"] = safe_parse_dates(df["observation_date"])
    df["clean_diesel"] = pd.to_numeric(df["diesel_price"], errors="coerce")

    valid_mask = (
        df["parsed_date"].notna() &
        df["clean_diesel"].notna() &
        (df["clean_diesel"] > 0)
    )

    rejected_rows = int((~valid_mask).sum())
    valid_df = df[valid_mask].copy()

    subset_cols = ["parsed_date"]
    if "state" in valid_df.columns:
        subset_cols.append("state")

    duplicate_mask = valid_df.duplicated(subset=subset_cols, keep="first")
    duplicate_rows = int(duplicate_mask.sum())
    final_df = valid_df[~duplicate_mask]

    accepted_rows = len(final_df)

    objects_to_add = []
    for _, row in final_df.iterrows():
        obj = FuelObservation(
            observation_date=row["parsed_date"],
            state=str(row["state"]).strip() if "state" in row and pd.notna(row["state"]) else None,
            diesel_price=float(row["clean_diesel"]),
            currency="INR/Litre",
            is_synthetic=is_synthetic,
            source_ref=filename
        )
        objects_to_add.append(obj)

    db.bulk_save_objects(objects_to_add)

    hist = ImportHistory(
        dataset_type="fuel",
        filename=filename,
        total_records=total_rows,
        accepted_records=accepted_rows,
        rejected_records=rejected_rows,
        duplicate_records=duplicate_rows,
        status="SUCCESS" if accepted_rows > 0 else "FAILED",
        notes=f"Accepted {accepted_rows}/{total_rows} records."
    )
    db.add(hist)
    db.commit()

    return {
        "status": "SUCCESS" if accepted_rows > 0 else "EMPTY",
        "dataset_type": "fuel",
        "filename": filename,
        "total_rows": total_rows,
        "accepted_rows": accepted_rows,
        "rejected_rows": rejected_rows,
        "duplicate_rows": duplicate_rows,
        "errors": []
    }


# =====================================================================
# 3. DATASET STATUS AND QUALITY CHECKING
# =====================================================================

def get_dataset_status(db: Session) -> Dict[str, Any]:
    """
    Inspects all tables in the database to report record counts,
    date ranges, number of states covered, and analytical readiness.
    """
    tables_info = {}
    notes = []

    # 1. KCC status
    kcc_count = db.query(func.count(KCCObservation.id)).scalar() or 0
    kcc_min_date = db.query(func.min(KCCObservation.observation_date)).scalar()
    kcc_max_date = db.query(func.max(KCCObservation.observation_date)).scalar()
    kcc_states = db.query(func.count(func.distinct(KCCObservation.state))).scalar() or 0
    kcc_synthetic = db.query(func.count(KCCObservation.id)).filter(KCCObservation.is_synthetic == True).scalar() or 0

    tables_info["kcc"] = {
        "table_name": "kcc_observations",
        "total_records": kcc_count,
        "min_date": str(kcc_min_date) if kcc_min_date else None,
        "max_date": str(kcc_max_date) if kcc_max_date else None,
        "states_count": kcc_states,
        "is_synthetic": kcc_synthetic > 0
    }

    # 2. Commodity status
    comm_count = db.query(func.count(CommodityObservation.id)).scalar() or 0
    comm_min_date = db.query(func.min(CommodityObservation.observation_date)).scalar()
    comm_max_date = db.query(func.max(CommodityObservation.observation_date)).scalar()
    comm_states = db.query(func.count(func.distinct(CommodityObservation.state))).scalar() or 0
    comm_synthetic = db.query(func.count(CommodityObservation.id)).filter(CommodityObservation.is_synthetic == True).scalar() or 0

    tables_info["commodity"] = {
        "table_name": "commodity_observations",
        "total_records": comm_count,
        "min_date": str(comm_min_date) if comm_min_date else None,
        "max_date": str(comm_max_date) if comm_max_date else None,
        "states_count": comm_states,
        "is_synthetic": comm_synthetic > 0
    }

    # 3. Fuel status
    fuel_count = db.query(func.count(FuelObservation.id)).scalar() or 0
    fuel_min_date = db.query(func.min(FuelObservation.observation_date)).scalar()
    fuel_max_date = db.query(func.max(FuelObservation.observation_date)).scalar()
    fuel_states = db.query(func.count(func.distinct(FuelObservation.state))).scalar() or 0
    fuel_synthetic = db.query(func.count(FuelObservation.id)).filter(FuelObservation.is_synthetic == True).scalar() or 0

    tables_info["fuel"] = {
        "table_name": "fuel_observations",
        "total_records": fuel_count,
        "min_date": str(fuel_min_date) if fuel_min_date else None,
        "max_date": str(fuel_max_date) if fuel_max_date else None,
        "states_count": fuel_states,
        "is_synthetic": fuel_synthetic > 0
    }

    # Readiness check
    ready = (kcc_count >= 30) and (comm_count >= 30) and (fuel_count >= 30)

    if not ready:
        notes.append("Insufficient data: At least 30 observations per table are required for reliable time-series modeling.")
    if kcc_synthetic > 0 or comm_synthetic > 0 or fuel_synthetic > 0:
        notes.append("Notice: Some or all tables contain synthetic records generated for testing and demonstration.")

    return {
        "status": "READY" if ready else "INSUFFICIENT_DATA",
        "datasets": tables_info,
        "ready_for_analysis": ready,
        "notes": notes
    }


# =====================================================================
# 4. FEATURE ENGINEERING & ANALYTICAL DATASET PREPARATION
# =====================================================================

def build_analytical_dataset(
    db: Session,
    state: Optional[str] = None,
    commodity: Optional[str] = None,
    freq: str = "D",
    export_csv: bool = True
) -> pd.DataFrame:
    """
    Aligns KCC demand, commodity prices, and diesel fuel prices into a single,
    well-formed time-series DataFrame with engineered features.
    
    Steps:
      1. Aggregate KCC daily query counts (summing categories to avoid many-to-many explosion).
      2. Aggregate Mandi wholesale and retail prices (taking daily mean across markets).
      3. Aggregate Fuel diesel price (taking daily mean across state/metros).
      4. Merge on observation_date using an outer join, then reindex to continuous date range.
      5. Calculate feature engineering:
         - Commodity price daily change and percentage change.
         - 7-day rolling price volatility.
         - Wholesale-to-retail spread (if retail price is present).
         - Diesel price daily change and percentage change.
         - 7-day diesel price momentum.
    """
    # 1. KCC Query Data
    kcc_query = db.query(
        KCCObservation.observation_date,
        func.sum(KCCObservation.query_count).label("query_count")
    )
    if state:
        kcc_query = kcc_query.filter(KCCObservation.state == state)
    kcc_query = kcc_query.group_by(KCCObservation.observation_date)
    kcc_rows = kcc_query.all()

    if not kcc_rows:
        return pd.DataFrame()

    df_kcc = pd.DataFrame(kcc_rows, columns=["observation_date", "query_count"])
    df_kcc["observation_date"] = pd.to_datetime(df_kcc["observation_date"])

    # 2. Commodity Price Data
    comm_query = db.query(
        CommodityObservation.observation_date,
        func.avg(CommodityObservation.wholesale_price).label("wholesale_price"),
        func.avg(CommodityObservation.retail_price).label("retail_price"),
        func.sum(CommodityObservation.arrival_quantity).label("arrival_quantity")
    )
    if state:
        comm_query = comm_query.filter(CommodityObservation.state == state)
    if commodity:
        comm_query = comm_query.filter(CommodityObservation.commodity == commodity)
    comm_query = comm_query.group_by(CommodityObservation.observation_date)
    comm_rows = comm_query.all()

    df_comm = pd.DataFrame(comm_rows, columns=["observation_date", "wholesale_price", "retail_price", "arrival_quantity"])
    if not df_comm.empty:
        df_comm["observation_date"] = pd.to_datetime(df_comm["observation_date"])

    # 3. Fuel Price Data
    fuel_query = db.query(
        FuelObservation.observation_date,
        func.avg(FuelObservation.diesel_price).label("diesel_price")
    )
    if state:
        fuel_query = fuel_query.filter(FuelObservation.state == state)
    fuel_query = fuel_query.group_by(FuelObservation.observation_date)
    fuel_rows = fuel_query.all()

    df_fuel = pd.DataFrame(fuel_rows, columns=["observation_date", "diesel_price"])
    if not df_fuel.empty:
        df_fuel["observation_date"] = pd.to_datetime(df_fuel["observation_date"])

    # 4. Merge all on observation_date
    merged = df_kcc.copy()

    if not df_comm.empty:
        merged = pd.merge(merged, df_comm, on="observation_date", how="left")
    else:
        merged["wholesale_price"] = np.nan
        merged["retail_price"] = np.nan
        merged["arrival_quantity"] = np.nan

    if not df_fuel.empty:
        merged = pd.merge(merged, df_fuel, on="observation_date", how="left")
    else:
        merged["diesel_price"] = np.nan

    # Sort chronologically
    merged = merged.sort_values("observation_date").reset_index(drop=True)

    # Set date index for time series operations
    merged = merged.set_index("observation_date")

    # Resample to ensure continuous date range (fill missing query days with 0 or forward fill prices)
    full_idx = pd.date_range(start=merged.index.min(), end=merged.index.max(), freq="D")
    merged = merged.reindex(full_idx)
    merged.index.name = "observation_date"

    # Missing queries: If call centre had no queries logged on a day, count is 0
    merged["query_count"] = merged["query_count"].fillna(0)

    # Commodity and diesel prices don't occur on Sundays; forward fill them from previous trading day
    merged["wholesale_price"] = merged["wholesale_price"].ffill().bfill()
    merged["retail_price"] = merged["retail_price"].ffill().bfill()
    merged["diesel_price"] = merged["diesel_price"].ffill().bfill()
    merged["arrival_quantity"] = merged["arrival_quantity"].fillna(0)

    # 5. Feature Engineering
    # Commodity features
    merged["commodity_price_change"] = merged["wholesale_price"].diff()
    merged["commodity_pct_change"] = merged["wholesale_price"].pct_change(fill_method=None) * 100.0
    merged["commodity_volatility_7d"] = merged["wholesale_price"].rolling(window=7, min_periods=2).std()

    # Wholesale-to-retail spread
    # Only meaningful when retail_price is observed and valid
    if merged["retail_price"].notna().sum() > 0:
        merged["price_spread"] = merged["retail_price"] - merged["wholesale_price"]
        # Retail margin percentage over wholesale
        merged["retail_margin_pct"] = (merged["price_spread"] / merged["wholesale_price"]) * 100.0
    else:
        merged["price_spread"] = np.nan
        merged["retail_margin_pct"] = np.nan

    # Fuel features
    merged["diesel_price_change"] = merged["diesel_price"].diff()
    merged["diesel_pct_change"] = merged["diesel_price"].pct_change(fill_method=None) * 100.0
    # 7-day lagged diesel change to examine delayed impacts
    merged["diesel_change_lag1"] = merged["diesel_price_change"].shift(1)
    merged["diesel_change_lag7"] = merged["diesel_price_change"].shift(7)

    # Weekly or monthly resampling if requested
    if freq.upper() == "W":
        resampled = merged.resample("W").agg({
            "query_count": "sum",
            "wholesale_price": "mean",
            "retail_price": "mean",
            "arrival_quantity": "sum",
            "diesel_price": "mean",
            "commodity_price_change": "sum",
            "commodity_pct_change": "mean",
            "commodity_volatility_7d": "mean",
            "price_spread": "mean",
            "retail_margin_pct": "mean",
            "diesel_price_change": "sum",
            "diesel_pct_change": "mean",
            "diesel_change_lag1": "mean",
            "diesel_change_lag7": "mean",
        })
        merged = resampled
    elif freq.upper() == "M":
        resampled = merged.resample("M").agg({
            "query_count": "sum",
            "wholesale_price": "mean",
            "retail_price": "mean",
            "arrival_quantity": "sum",
            "diesel_price": "mean",
            "commodity_price_change": "sum",
            "commodity_pct_change": "mean",
            "commodity_volatility_7d": "mean",
            "price_spread": "mean",
            "retail_margin_pct": "mean",
            "diesel_price_change": "sum",
            "diesel_pct_change": "mean",
            "diesel_change_lag1": "mean",
            "diesel_change_lag7": "mean",
        })
        merged = resampled

    df_result = merged.reset_index()

    # Export to processed folder if requested
    if export_csv:
        output_file = DATA_DIR / "processed" / "analytical_dataset.csv"
        df_result.to_csv(output_file, index=False)

    return df_result
