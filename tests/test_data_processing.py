"""
Unit tests for CSV import, validation, date parsing, and data alignment.
"""
import io
import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.data_processing import (
    check_missing_columns,
    standardize_column_names,
    safe_parse_dates,
    import_kcc_csv,
    import_commodity_csv,
    import_fuel_csv,
    build_analytical_dataset
)


@pytest.fixture
def in_memory_db():
    """Provides a fresh SQLite in-memory database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_check_missing_columns():
    df = pd.DataFrame({"observation_date": ["2024-01-01"], "state": ["Maharashtra"]})
    missing = check_missing_columns(df, ["observation_date", "state", "query_count"])
    assert missing == ["query_count"]

    no_missing = check_missing_columns(df, ["observation_date", "state"])
    assert no_missing == []


def test_standardize_column_names():
    df = pd.DataFrame({" Observation Date ": [1], "State-Name": [2], "Query Count": [3]})
    clean_df = standardize_column_names(df)
    assert "observation_date" in clean_df.columns
    assert "state_name" in clean_df.columns
    assert "query_count" in clean_df.columns


def test_safe_parse_dates():
    dates = pd.Series(["2024-05-10", "10/05/2024", "not-a-date", None])
    parsed = safe_parse_dates(dates)
    assert parsed.iloc[0] is not None
    assert pd.isna(parsed.iloc[2])  # Invalid date turns into NaT


def test_import_kcc_csv_success_and_duplicates(in_memory_db):
    csv_data = """observation_date,state,district,query_type,query_count
2024-01-01,Maharashtra,Nashik,Weather,15
2024-01-01,Maharashtra,Nashik,Weather,15
2024-01-02,Maharashtra,Nashik,Weather,22
not_a_date,Maharashtra,Nashik,Weather,10
"""
    buf = io.StringIO(csv_data)
    result = import_kcc_csv(buf, in_memory_db, filename="test_kcc.csv", is_synthetic=True)

    assert result["status"] == "SUCCESS"
    assert result["total_rows"] == 4
    assert result["accepted_rows"] == 2  # 1 duplicate dropped, 1 bad date dropped
    assert result["rejected_rows"] == 1
    assert result["duplicate_rows"] == 1


def test_import_commodity_csv_validation(in_memory_db):
    bad_csv = io.StringIO("random_column,another_col\n1,2\n")
    result = import_commodity_csv(bad_csv, in_memory_db, filename="bad_comm.csv")
    assert result["status"] == "FAILED"
    assert len(result["errors"]) > 0


def test_data_alignment_pipeline(in_memory_db):
    # Ingest 3 days of matched data
    kcc_csv = io.StringIO("""observation_date,state,query_count
2024-01-01,Maharashtra,10
2024-01-02,Maharashtra,20
2024-01-03,Maharashtra,30
""")
    comm_csv = io.StringIO("""observation_date,state,commodity,wholesale_price,retail_price
2024-01-01,Maharashtra,Onion,2000,2800
2024-01-02,Maharashtra,Onion,2100,2900
2024-01-03,Maharashtra,Onion,2200,3100
""")
    fuel_csv = io.StringIO("""observation_date,state,diesel_price
2024-01-01,Maharashtra,92.5
2024-01-02,Maharashtra,92.5
2024-01-03,Maharashtra,93.5
""")
    import_kcc_csv(kcc_csv, in_memory_db, is_synthetic=True)
    import_commodity_csv(comm_csv, in_memory_db, is_synthetic=True)
    import_fuel_csv(fuel_csv, in_memory_db, is_synthetic=True)

    df_aligned = build_analytical_dataset(in_memory_db, state="Maharashtra", export_csv=False)
    assert len(df_aligned) == 3
    assert "query_count" in df_aligned.columns
    assert "wholesale_price" in df_aligned.columns
    assert "price_spread" in df_aligned.columns
    assert "commodity_price_change" in df_aligned.columns
    # Check price spread calculation: 2800 - 2000 = 800
    assert df_aligned.loc[0, "price_spread"] == 800.0
