# olist_churn_prediction/paths.py
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR     = PROJECT_ROOT / "data"
RAW_DIR      = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
SRC_DIR = PROJECT_ROOT / "src"
REPORTS_DIR = PROJECT_ROOT / 'reports'
MODELS_DIR = PROJECT_ROOT / 'models'
INTERIM_NOTEBOOK_DIR = DATA_DIR / "interim/notebook_related"
INTERIM_CLI_DIR = DATA_DIR / "interim/cli_related"