"""
Database initialization script for AgriStress Analytics.
Creates all SQLite or PostgreSQL tables defined in app/models.py.
"""
import sys
from pathlib import Path

# Add project root directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import Base, engine
from app.config import DATABASE_URL
import app.models  # Ensures all models are registered with Base.metadata


import argparse


def init_database(reset: bool = False):
    print(f"Connecting to database: {DATABASE_URL}")
    if reset:
        print("Dropping all existing database tables...")
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize AgriStress Database")
    parser.add_argument("--reset", action="store_true", help="Drop existing tables before recreating")
    args = parser.parse_args()
    init_database(reset=args.reset)

