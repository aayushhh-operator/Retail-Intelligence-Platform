"""Configuration for the Phase 6 Analytics Layer."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ANALYTICS_DIR = Path(__file__).resolve().parent
SQL_DIR = ANALYTICS_DIR / "sql"
MODELS_DIR = ANALYTICS_DIR / "models"

DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_NAME = os.getenv("DATABASE_NAME", "RetailIntelligencePlatform")
DB_USER = os.getenv("DATABASE_USER", "postgres")
DB_PASS = os.getenv("DATABASE_PASSWORD", "postgres")

SOURCE_SCHEMA = "warehouse"
TARGET_SCHEMA = "analytics"
