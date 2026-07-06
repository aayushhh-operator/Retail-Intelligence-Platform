"""PySpark Configuration Module."""

import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# Spark Core Settings
SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")
SPARK_APP_NAME = "RetailIntelligencePlatform"
SPARK_DRIVER_MEMORY = os.getenv("SPARK_DRIVER_MEMORY", "2g")
SPARK_EXECUTOR_MEMORY = os.getenv("SPARK_EXECUTOR_MEMORY", "2g")

# Database Connection Settings
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "RetailIntelligencePlatform")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")

# JDBC Connection URL
JDBC_URL = f"jdbc:postgresql://{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
JDBC_PROPERTIES = {
    "user": DATABASE_USER,
    "password": DATABASE_PASSWORD,
    "driver": "org.postgresql.Driver"
}

# Path Settings
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
SPARK_OUTPUT_DIR = PROJECT_ROOT / "spark" / "output"
CHECKPOINT_DIR = PROJECT_ROOT / "spark" / "checkpoints"

# Ensure directories exist
SPARK_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

# Feature Flags
ENABLE_CUSTOMER_ANALYTICS = True
ENABLE_ORDER_ANALYTICS = True
ENABLE_PRODUCT_PERFORMANCE = True
ENABLE_EVENT_PROCESSING = True
ENABLE_SESSIONIZATION = True
ENABLE_REVENUE_AGGREGATION = True
