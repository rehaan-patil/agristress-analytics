"""
Data Processing and Feature Engineering for AgriStress Analytics.
Written in simple, clear Python using Pandas and SQLAlchemy.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import DATA_DIR
from app.models import KCCObservation, CommodityObservation, FuelObservation, ImportHistory


def check_missing_columns(df: pd.DataFrame, required: List[str]) -> List[str]:
    """Finds which required columns are not present in the dataframe."""
    existing = [str(c).strip().lower() for c in df.columns]
    return [col for col in required if col.lower() not in existing]


COLUMN_SYNONYMS = {
    # Dates
    "arrival_date": "observation_date",
    "createdon": "observation_date",
    "created_on": "observation_date",
    "created_date": "observation_date",
    "call_date": "observation_date",
    "date": "observation_date",
    "reported_date": "observation_date",
    "record_date": "observation_date",

    # State / District / Market
    "statename": "state",
    "state_name": "state",
    "districtname": "district",
    "district_name": "district",
    "marketname": "market",
    "market_name": "market",
    "mandi": "market",
    "mandi_name": "market",

    # KCC Inquiries
    "calls": "query_count",
    "call_count": "query_count",
    "queries": "query_count",
    "inquiries": "query_count",
    "total_queries": "query_count",
    "querytype": "query_type",
    "category": "query_type",
    "sector": "query_type",

    # Commodity Prices & Arrivals
    "commodity_name": "commodity",
    "crop": "commodity",
    "modal_price": "wholesale_price",
    "modal_price_(rs./quintal)": "wholesale_price",
    "modal_price_rs_quintal": "wholesale_price",
    "modal_x0020_price": "wholesale_price",
    "modal_price_(rs/qtl)": "wholesale_price",
    "modal_price_rs_per_qtl": "wholesale_price",
    "price": "wholesale_price",
    "retail_price_(rs./quintal)": "retail_price",
    "retail_price_(rs/qtl)": "retail_price",
    "arrivals": "arrival_quantity",
    "arrivals_(tonnes)": "arrival_quantity",
    "arrivals_in_tonnes": "arrival_quantity",
    "arrival_tonnes": "arrival_quantity",

    # Fuel Prices
    "diesel": "diesel_price",
    "diesel_retail_price": "diesel_price",
    "diesel_price_(rs/litre)": "diesel_price",
    "diesel_(rs./litre)": "diesel_price",
    "diesel_rs_litre": "diesel_price",
    "fuel_price": "diesel_price",
}


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Makes column names lowercase with underscores and no surrounding spaces."""
    renamed = {c: str(c).strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns}
    return df.rename(columns=renamed)


def apply_column_synonyms(df: pd.DataFrame) -> pd.DataFrame:
    """Maps common government and operational dataset column variations to standard schema names."""
    renamed = {}
    for col in df.columns:
        c_clean = str(col).strip().lower().replace(" ", "_").replace("-", "_")
        if c_clean in COLUMN_SYNONYMS:
            renamed[col] = COLUMN_SYNONYMS[c_clean]
        elif c_clean != col:
            renamed[col] = c_clean
    return df.rename(columns=renamed)


def safe_parse_dates(series: pd.Series) -> pd.Series:
    """Parses text into dates, marking invalid text as NaT."""
    return pd.to_datetime(series, errors="coerce", format="mixed").dt.date


def import_kcc_csv(
    file_or_path,
    db: Session,
    filename: str = "kcc_data.csv",
    is_synthetic: bool = False,
    replace: bool = False
) -> Dict[str, Any]:
    """Reads and validates KCC queries CSV and saves records to database."""
    try:
        df = apply_column_synonyms(standardize_column_names(pd.read_csv(file_or_path)))
    except Exception as e:
        return {"status": "FAILED", "filename": filename, "total_rows": 0, "accepted_rows": 0, "rejected_rows": 0, "duplicate_rows": 0, "errors": [str(e)]}

    missing = check_missing_columns(df, ["observation_date", "state"])
    if missing:
        err = f"Missing required columns: {', '.join(missing)}"
        db.add(ImportHistory(dataset_type="kcc", filename=filename, total_records=len(df), status="FAILED", notes=err))
        db.commit()
        return {"status": "FAILED", "filename": filename, "total_rows": len(df), "accepted_rows": 0, "rejected_rows": len(df), "duplicate_rows": 0, "errors": [err]}

    if "query_count" not in df.columns:
        df["query_count"] = 1
        raw_log = True
    else:
        df["query_count"] = pd.to_numeric(df["query_count"], errors="coerce")
        raw_log = False

    df["parsed_date"] = safe_parse_dates(df["observation_date"])
    valid = df[df["parsed_date"].notna() & df["state"].notna() & (df["query_count"] >= 0)].copy()
    rejected = len(df) - len(valid)

    group_cols = ["parsed_date", "state"]
    if "district" in valid.columns:
        group_cols.append("district")
    if "query_type" in valid.columns:
        group_cols.append("query_type")

    if raw_log:
        agg_df = valid.groupby(group_cols, as_index=False, dropna=False)["query_count"].sum()
        duplicates = len(valid) - len(agg_df)
        valid = agg_df
    else:
        before_dedup = len(valid)
        valid = valid.drop_duplicates(subset=group_cols)
        duplicates = before_dedup - len(valid)

    if replace:
        db.query(KCCObservation).delete()
        db.commit()

    # Save to database
    objs = [
        KCCObservation(
            observation_date=r["parsed_date"],
            state=str(r["state"]).strip(),
            district=str(r["district"]).strip() if "district" in r and pd.notna(r["district"]) else None,
            query_type=str(r["query_type"]).strip() if "query_type" in r and pd.notna(r["query_type"]) else None,
            query_count=int(r["query_count"]),
            is_synthetic=is_synthetic,
            source_ref=filename
        )
        for _, r in valid.iterrows()
    ]
    db.bulk_save_objects(objs)
    db.add(ImportHistory(dataset_type="kcc", filename=filename, total_records=len(df), accepted_records=len(objs), rejected_records=rejected, duplicate_records=duplicates, status="SUCCESS" if objs else "EMPTY"))
    db.commit()

    return {"status": "SUCCESS" if objs else "EMPTY", "dataset_type": "kcc", "filename": filename, "total_rows": len(df), "accepted_rows": len(objs), "rejected_rows": rejected, "duplicate_rows": duplicates, "errors": []}


def import_commodity_csv(
    file_or_path,
    db: Session,
    filename: str = "commodity_prices.csv",
    is_synthetic: bool = False,
    replace: bool = False
) -> Dict[str, Any]:
    """Reads, cleans, and saves wholesale commodity price records."""
    try:
        df = apply_column_synonyms(standardize_column_names(pd.read_csv(file_or_path)))
    except Exception as e:
        return {"status": "FAILED", "filename": filename, "total_rows": 0, "accepted_rows": 0, "rejected_rows": 0, "duplicate_rows": 0, "errors": [str(e)]}

    missing = check_missing_columns(df, ["observation_date", "state", "commodity", "wholesale_price"])
    if missing:
        err = f"Missing required columns: {', '.join(missing)}"
        db.add(ImportHistory(dataset_type="commodity", filename=filename, total_records=len(df), status="FAILED", notes=err))
        db.commit()
        return {"status": "FAILED", "filename": filename, "total_rows": len(df), "accepted_rows": 0, "rejected_rows": len(df), "duplicate_rows": 0, "errors": [err]}

    df["parsed_date"] = safe_parse_dates(df["observation_date"])
    df["wholesale_price"] = pd.to_numeric(df["wholesale_price"], errors="coerce")
    df["retail_price"] = pd.to_numeric(df["retail_price"], errors="coerce") if "retail_price" in df.columns else None
    df["arrival_quantity"] = pd.to_numeric(df["arrival_quantity"], errors="coerce") if "arrival_quantity" in df.columns else None

    valid = df[df["parsed_date"].notna() & df["state"].notna() & df["commodity"].notna() & (df["wholesale_price"] > 0)].copy()
    rejected = len(df) - len(valid)

    sub_cols = ["parsed_date", "state", "commodity"]
    if "market" in valid.columns and valid["market"].notna().any():
        sub_cols.append("market")
    valid = valid.drop_duplicates(subset=sub_cols)
    duplicates = len(df) - rejected - len(valid)

    if replace:
        db.query(CommodityObservation).delete()
        db.commit()

    objs = [
        CommodityObservation(
            observation_date=r["parsed_date"],
            state=str(r["state"]).strip(),
            district=str(r["district"]).strip() if "district" in r and pd.notna(r["district"]) else None,
            market=str(r["market"]).strip() if "market" in r and pd.notna(r["market"]) else None,
            commodity=str(r["commodity"]).strip(),
            wholesale_price=float(r["wholesale_price"]),
            retail_price=float(r["retail_price"]) if pd.notna(r["retail_price"]) else None,
            arrival_quantity=float(r["arrival_quantity"]) if pd.notna(r["arrival_quantity"]) else None,
            is_synthetic=is_synthetic,
            source_ref=filename
        )
        for _, r in valid.iterrows()
    ]
    db.bulk_save_objects(objs)
    db.add(ImportHistory(dataset_type="commodity", filename=filename, total_records=len(df), accepted_records=len(objs), rejected_records=rejected, duplicate_records=duplicates, status="SUCCESS" if objs else "EMPTY"))
    db.commit()

    return {"status": "SUCCESS" if objs else "EMPTY", "dataset_type": "commodity", "filename": filename, "total_rows": len(df), "accepted_rows": len(objs), "rejected_rows": rejected, "duplicate_rows": duplicates, "errors": []}


def import_fuel_csv(
    file_or_path,
    db: Session,
    filename: str = "fuel_prices.csv",
    is_synthetic: bool = False,
    replace: bool = False
) -> Dict[str, Any]:
    """Reads and saves retail diesel fuel prices."""
    try:
        df = apply_column_synonyms(standardize_column_names(pd.read_csv(file_or_path)))
    except Exception as e:
        return {"status": "FAILED", "filename": filename, "total_rows": 0, "accepted_rows": 0, "rejected_rows": 0, "duplicate_rows": 0, "errors": [str(e)]}

    missing = check_missing_columns(df, ["observation_date", "diesel_price"])
    if missing:
        err = f"Missing required columns: {', '.join(missing)}"
        db.add(ImportHistory(dataset_type="fuel", filename=filename, total_records=len(df), status="FAILED", notes=err))
        db.commit()
        return {"status": "FAILED", "filename": filename, "total_rows": len(df), "accepted_rows": 0, "rejected_rows": len(df), "duplicate_rows": 0, "errors": [err]}

    df["parsed_date"] = safe_parse_dates(df["observation_date"])
    df["diesel_price"] = pd.to_numeric(df["diesel_price"], errors="coerce")

    valid = df[df["parsed_date"].notna() & (df["diesel_price"] > 0)].copy()
    rejected = len(df) - len(valid)

    subset = ["parsed_date", "state"] if "state" in valid.columns else ["parsed_date"]
    valid = valid.drop_duplicates(subset=subset)
    duplicates = len(df) - rejected - len(valid)

    if replace:
        db.query(FuelObservation).delete()
        db.commit()

    objs = [
        FuelObservation(
            observation_date=r["parsed_date"],
            state=str(r["state"]).strip() if "state" in r and pd.notna(r["state"]) else None,
            diesel_price=float(r["diesel_price"]),
            is_synthetic=is_synthetic,
            source_ref=filename
        )
        for _, r in valid.iterrows()
    ]
    db.bulk_save_objects(objs)
    db.add(ImportHistory(dataset_type="fuel", filename=filename, total_records=len(df), accepted_records=len(objs), rejected_records=rejected, duplicate_records=duplicates, status="SUCCESS" if objs else "EMPTY"))
    db.commit()

    return {"status": "SUCCESS" if objs else "EMPTY", "dataset_type": "fuel", "filename": filename, "total_rows": len(df), "accepted_rows": len(objs), "rejected_rows": rejected, "duplicate_rows": duplicates, "errors": []}


def get_dataset_status(db: Session) -> Dict[str, Any]:
    """Reports counts, date ranges, and analytical readiness of database tables."""
    info = {}
    for name, model in [("kcc", KCCObservation), ("commodity", CommodityObservation), ("fuel", FuelObservation)]:
        count = db.query(func.count(model.id)).scalar() or 0
        min_d = db.query(func.min(model.observation_date)).scalar()
        max_d = db.query(func.max(model.observation_date)).scalar()
        st_count = db.query(func.count(func.distinct(model.state))).scalar() or 0
        synth = db.query(func.count(model.id)).filter(model.is_synthetic == True).scalar() or 0

        info[name] = {
            "table_name": model.__tablename__,
            "total_records": count,
            "min_date": str(min_d) if min_d else None,
            "max_date": str(max_d) if max_d else None,
            "states_count": st_count,
            "is_synthetic": synth > 0
        }

    ready = (info["kcc"]["total_records"] >= 30 and info["commodity"]["total_records"] >= 30 and info["fuel"]["total_records"] >= 30)
    notes = []
    if not ready:
        notes.append("Need at least 30 rows per table to conduct time-series forecasting.")
    if any(v["is_synthetic"] for v in info.values()):
        notes.append("Notice: Some or all tables contain synthetic records generated for testing and demonstration.")

    return {"status": "READY" if ready else "INSUFFICIENT_DATA", "datasets": info, "ready_for_analysis": ready, "notes": notes}


def get_data_quality_report(
    db: Session,
    df: Optional[pd.DataFrame] = None,
    provenance_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates data coverage, missingness, and data provenance.
    Produces an understandable summary for research verification.
    """
    status = get_dataset_status(db)
    is_synth = any(v["is_synthetic"] for v in status["datasets"].values())
    
    if df is None:
        df = build_analytical_dataset(db, export_csv=False)

    if provenance_type is None:
        if is_synth:
            prov_type = "SYNTHETIC"
            prov_label = "Synthetic Demonstration Data"
            prov_note = "PROVENANCE: Data contains synthetic demonstration observations generated deterministically."
        else:
            prov_type = "UNVERIFIED"
            prov_label = "Unverified / User-Supplied Data"
            prov_note = "PROVENANCE: Data imported from local CSV files without independent verification."
    elif provenance_type.upper() == "VERIFIED_REAL":
        prov_type = "VERIFIED_REAL"
        prov_label = "Verified Real-World Observations"
        prov_note = "PROVENANCE: Verified real-world operational records imported from official sources."
    elif provenance_type.upper() == "SYNTHETIC":
        prov_type = "SYNTHETIC"
        prov_label = "Synthetic Demonstration Data"
        prov_note = "PROVENANCE: Data contains synthetic demonstration observations generated deterministically."
    else:
        prov_type = "UNVERIFIED"
        prov_label = "Unverified / User-Supplied Data"
        prov_note = "PROVENANCE: Data imported from local CSV files without independent verification."

    if df.empty:
        return {
            "total_calendar_days": 0,
            "observed_query_days": 0,
            "unrecorded_days": 0,
            "missingness_percentage": 0.0,
            "is_synthetic": (prov_type == "SYNTHETIC"),
            "provenance_type": prov_type,
            "provenance_label": prov_label,
            "quality_status": "NO_DATA",
            "quality_notes": ["No records found in database."]
        }

    min_date = df["observation_date"].min()
    max_date = df["observation_date"].max()
    total_days = (max_date - min_date).days + 1 if hasattr(min_date, "strftime") else len(df)
    
    zero_query_days = int((df["query_count"] == 0).sum())
    observed_days = len(df) - zero_query_days
    missing_pct = round((zero_query_days / len(df)) * 100.0, 2) if len(df) > 0 else 0.0

    notes = [prov_note]
    notes.append("Mandi holiday / Sunday closures are forward-filled for price continuity.")
    if zero_query_days > 0:
        notes.append(f"{zero_query_days} days had 0 recorded queries (e.g., call centre closed on Sundays/holidays).")

    quality_status = "GOOD" if missing_pct < 20 else ("ACCEPTABLE" if missing_pct < 40 else "POOR")

    return {
        "sample_start": str(pd.to_datetime(min_date).date()) if min_date is not None else None,
        "sample_end": str(pd.to_datetime(max_date).date()) if max_date is not None else None,
        "total_calendar_days": total_days,
        "observed_query_days": observed_days,
        "zero_or_unrecorded_days": zero_query_days,
        "missingness_percentage": missing_pct,
        "is_synthetic": (prov_type == "SYNTHETIC"),
        "provenance_type": prov_type,
        "provenance_label": prov_label,
        "quality_status": quality_status,
        "quality_notes": notes
    }


def build_analytical_dataset(db: Session, state: Optional[str] = None, commodity: Optional[str] = None, freq: str = "D", export_csv: bool = True) -> pd.DataFrame:
    """
    Merges KCC queries, commodity prices, and fuel prices by date into a single DataFrame.
    Supports daily ('D'), weekly ('W'), or monthly ('M') time aggregation without duplicate inflation.
    """
    # Check synthetic provenance in source tables
    synth_kcc = db.query(KCCObservation.id).filter(KCCObservation.is_synthetic == True).first() is not None

    # 1. KCC daily queries
    q_kcc = db.query(KCCObservation.observation_date, func.sum(KCCObservation.query_count).label("query_count"))
    if state:
        q_kcc = q_kcc.filter(KCCObservation.state == state)
    df_kcc = pd.DataFrame(q_kcc.group_by(KCCObservation.observation_date).all(), columns=["observation_date", "query_count"])

    if df_kcc.empty:
        return pd.DataFrame()
    df_kcc["observation_date"] = pd.to_datetime(df_kcc["observation_date"])

    # 2. Commodity daily wholesale & retail prices
    q_comm = db.query(
        CommodityObservation.observation_date,
        func.avg(CommodityObservation.wholesale_price).label("wholesale_price"),
        func.avg(CommodityObservation.retail_price).label("retail_price"),
        func.sum(CommodityObservation.arrival_quantity).label("arrival_quantity")
    )
    if state:
        q_comm = q_comm.filter(CommodityObservation.state == state)
    if commodity:
        q_comm = q_comm.filter(CommodityObservation.commodity == commodity)
    df_comm = pd.DataFrame(q_comm.group_by(CommodityObservation.observation_date).all(), columns=["observation_date", "wholesale_price", "retail_price", "arrival_quantity"])
    if not df_comm.empty:
        df_comm["observation_date"] = pd.to_datetime(df_comm["observation_date"])

    # 3. Fuel daily diesel prices
    q_fuel = db.query(FuelObservation.observation_date, func.avg(FuelObservation.diesel_price).label("diesel_price"))
    if state:
        q_fuel = q_fuel.filter(FuelObservation.state == state)
    df_fuel = pd.DataFrame(q_fuel.group_by(FuelObservation.observation_date).all(), columns=["observation_date", "diesel_price"])
    if not df_fuel.empty:
        df_fuel["observation_date"] = pd.to_datetime(df_fuel["observation_date"])

    # 4. Merge on observation_date (left join ensures each observation date is unique)
    merged = df_kcc.copy()
    merged = pd.merge(merged, df_comm, on="observation_date", how="left") if not df_comm.empty else merged.assign(wholesale_price=np.nan, retail_price=np.nan, arrival_quantity=0.0)
    merged = pd.merge(merged, df_fuel, on="observation_date", how="left") if not df_fuel.empty else merged.assign(diesel_price=np.nan)

    # 5. Continuous date index & aggregation
    merged = merged.sort_values("observation_date").set_index("observation_date")
    
    # Handle frequency aggregation
    norm_freq = freq.upper()
    if norm_freq.startswith("W"):
        # Weekly aggregation: sum query volume and arrivals, average prices
        merged = merged.resample("W-SUN").agg({
            "query_count": "sum",
            "wholesale_price": "mean",
            "retail_price": "mean",
            "arrival_quantity": "sum",
            "diesel_price": "mean"
        })
    elif norm_freq.startswith("M"):
        # Monthly aggregation
        merged = merged.resample("MS").agg({
            "query_count": "sum",
            "wholesale_price": "mean",
            "retail_price": "mean",
            "arrival_quantity": "sum",
            "diesel_price": "mean"
        })
    else:
        # Default Daily ('D')
        full_idx = pd.date_range(merged.index.min(), merged.index.max(), freq="D")
        merged = merged.reindex(full_idx)
        merged.index.name = "observation_date"

    # Forward fill prices for Sundays / mandi holidays, missing queries to 0
    merged["query_count"] = merged["query_count"].fillna(0.0)
    merged["wholesale_price"] = merged["wholesale_price"].ffill().bfill()
    merged["retail_price"] = merged["retail_price"].ffill().bfill()
    merged["diesel_price"] = merged["diesel_price"].ffill().bfill()
    merged["arrival_quantity"] = pd.to_numeric(merged["arrival_quantity"], errors="coerce").fillna(0.0)

    # 6. Feature calculations
    merged["commodity_price_change"] = merged["wholesale_price"].diff()
    merged["commodity_pct_change"] = merged["wholesale_price"].pct_change(fill_method=None) * 100.0
    merged["commodity_volatility_7d"] = merged["wholesale_price"].rolling(7, min_periods=2).std()

    if merged["retail_price"].notna().sum() > 0:
        merged["price_spread"] = merged["retail_price"] - merged["wholesale_price"]
        merged["retail_margin_pct"] = (merged["price_spread"] / merged["wholesale_price"]) * 100.0
    else:
        merged["price_spread"] = np.nan
        merged["retail_margin_pct"] = np.nan

    merged["diesel_price_change"] = merged["diesel_price"].diff()
    merged["diesel_pct_change"] = merged["diesel_price"].pct_change(fill_method=None) * 100.0
    merged["diesel_change_lag1"] = merged["diesel_price_change"].shift(1)
    merged["diesel_change_lag7"] = merged["diesel_price_change"].shift(7)
    
    # 7. Data Provenance
    merged["is_synthetic"] = synth_kcc

    result = merged.reset_index()
    if export_csv:
        output_file = DATA_DIR / "processed" / "analytical_dataset.csv"
        result.to_csv(output_file, index=False)

    return result
