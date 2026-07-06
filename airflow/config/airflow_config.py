"""Airflow centralized configuration."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure we load the .env from the project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# Database Connection Variables for Airflow Custom Hook Logging
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "RetailIntelligencePlatform")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")

# Airflow Environment specific settings
ENVIRONMENT = os.getenv("AIRFLOW_ENV", "dev")

# Flags
ENABLE_DATA_GENERATION = os.getenv("ENABLE_DATA_GENERATION", "False").lower() == "true"
