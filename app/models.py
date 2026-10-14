"""
SQLAlchemy database models for AgriStress Analytics.
Simple, readable tables for student research and SQLite storage.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text
from app.database import Base


class KCCObservation(Base):
    """Stores Kisan Call Centre query records."""
    __tablename__ = "kcc_observations"

    id = Column(Integer, primary_key=True, index=True)
    observation_date = Column(Date, nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=True)
    query_type = Column(String(100), nullable=True)
    query_count = Column(Integer, default=1, nullable=False)
    is_synthetic = Column(Boolean, default=False)
    source_ref = Column(String(200), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "observation_date": str(self.observation_date),
            "state": self.state,
            "district": self.district,
            "query_type": self.query_type,
            "query_count": self.query_count,
            "is_synthetic": self.is_synthetic,
            "source_ref": self.source_ref
        }


class CommodityObservation(Base):
    """Stores wholesale mandi prices and arrivals."""
    __tablename__ = "commodity_observations"

    id = Column(Integer, primary_key=True, index=True)
    observation_date = Column(Date, nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=True)
    market = Column(String(150), nullable=True)
    commodity = Column(String(100), nullable=False, index=True)
    wholesale_price = Column(Float, nullable=False)
    retail_price = Column(Float, nullable=True)
    arrival_quantity = Column(Float, nullable=True)
    units = Column(String(50), default="INR/Quintal")
    is_synthetic = Column(Boolean, default=False)
    source_ref = Column(String(200), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "observation_date": str(self.observation_date),
            "state": self.state,
            "district": self.district,
            "market": self.market,
            "commodity": self.commodity,
            "wholesale_price": self.wholesale_price,
            "retail_price": self.retail_price,
            "arrival_quantity": self.arrival_quantity,
            "units": self.units,
            "is_synthetic": self.is_synthetic,
            "source_ref": self.source_ref
        }


class FuelObservation(Base):
    """Stores daily retail diesel fuel prices in INR/Litre."""
    __tablename__ = "fuel_observations"

    id = Column(Integer, primary_key=True, index=True)
    observation_date = Column(Date, nullable=False, index=True)
    state = Column(String(100), nullable=True, index=True)
    diesel_price = Column(Float, nullable=False)
    currency = Column(String(20), default="INR/Litre")
    is_synthetic = Column(Boolean, default=False)
    source_ref = Column(String(200), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "observation_date": str(self.observation_date),
            "state": self.state,
            "diesel_price": self.diesel_price,
            "currency": self.currency,
            "is_synthetic": self.is_synthetic,
            "source_ref": self.source_ref
        }


class ImportHistory(Base):
    """Simple audit log of CSV import runs."""
    __tablename__ = "import_history"

    id = Column(Integer, primary_key=True, index=True)
    dataset_type = Column(String(50), nullable=False)
    filename = Column(String(255), nullable=False)
    import_time = Column(DateTime, default=datetime.utcnow)
    total_records = Column(Integer, default=0)
    accepted_records = Column(Integer, default=0)
    rejected_records = Column(Integer, default=0)
    duplicate_records = Column(Integer, default=0)
    status = Column(String(50), default="PENDING")
    notes = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "dataset_type": self.dataset_type,
            "filename": self.filename,
            "import_time": self.import_time.isoformat() if self.import_time else None,
            "total_records": self.total_records,
            "accepted_records": self.accepted_records,
            "rejected_records": self.rejected_records,
            "duplicate_records": self.duplicate_records,
            "status": self.status,
            "notes": self.notes
        }


class ForecastHistory(Base):
    """Logs forecast outputs and operational advisory stress category."""
    __tablename__ = "forecast_history"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    model_name = Column(String(100), nullable=False)
    target_variable = Column(String(50), default="query_count")
    state = Column(String(100), nullable=True)
    forecast_start_date = Column(Date, nullable=False)
    forecast_end_date = Column(Date, nullable=False)
    horizon_days = Column(Integer, nullable=False)
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)
    stress_category = Column(String(50), nullable=True)
    details_json = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "model_name": self.model_name,
            "target_variable": self.target_variable,
            "state": self.state,
            "forecast_start_date": str(self.forecast_start_date),
            "forecast_end_date": str(self.forecast_end_date),
            "horizon_days": self.horizon_days,
            "mae": self.mae,
            "rmse": self.rmse,
            "mape": self.mape,
            "stress_category": self.stress_category
        }
