import os
from pathlib import Path
from dotenv import load_dotenv

# Load variables from .env file if it exists
load_dotenv()

# Base project directory (d:\python-capstone or wherever the repository is located)
BASE_DIR = Path(__file__).resolve().parent.parent

# Database connection: Defaults to local SQLite, can be overridden by PostgreSQL URL on Render
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'agristress.db'}")

# Data and output folder paths
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
OUTPUTS_DIR = Path(os.getenv("OUTPUTS_DIR", BASE_DIR / "outputs"))

# Make sure essential folders exist on startup
DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "raw").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "processed").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "synthetic").mkdir(parents=True, exist_ok=True)

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
(OUTPUTS_DIR / "charts").mkdir(parents=True, exist_ok=True)
(OUTPUTS_DIR / "reports").mkdir(parents=True, exist_ok=True)
(OUTPUTS_DIR / "tables").mkdir(parents=True, exist_ok=True)
(OUTPUTS_DIR / "forecasts").mkdir(parents=True, exist_ok=True)

TABLES_DIR = OUTPUTS_DIR / "tables"
FORECASTS_DIR = OUTPUTS_DIR / "forecasts"
