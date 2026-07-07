"""Configuration for the Phase 5 Data Warehouse."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Database Connection Details
DB_HOST = os.environ.get("DATABASE_HOST", "localhost")
DB_PORT = os.environ.get("DATABASE_PORT", "5432")
DB_NAME = os.environ.get("DATABASE_NAME", "RetailIntelligencePlatform")
DB_USER = os.environ.get("DATABASE_USER", "postgres")
DB_PASSWORD = os.environ.get("DATABASE_PASSWORD", "postgres")

# Directories
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
SQL_DIR = PROJECT_ROOT / "sql"
METADATA_DIR = PROJECT_ROOT / "logs" / "metadata"

# Ensure metadata directory exists
METADATA_DIR.mkdir(parents=True, exist_ok=True)
