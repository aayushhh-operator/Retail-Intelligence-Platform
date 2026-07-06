"""Reusable constants for project-wide names and paths."""

from __future__ import annotations

PROJECT_NAME = "Retail Intelligence Platform"
PROJECT_SLUG = "retail_intelligence_platform"

PIPELINE_NAME = "retail_intelligence_pipeline"

CONFIG_DIR = "config"
DATA_DIR = "data"
SOURCE_DATA_DIR = "data/source"
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
EXPORT_DATA_DIR = "data/exports"
EXTRACT_DIR = "extract"
VALIDATE_DIR = "validate"
TRANSFORM_DIR = "transform"
LOAD_DIR = "load"
WAREHOUSE_DIR = "warehouse"
SQL_DIR = "sql"
AIRFLOW_DIR = "airflow"
SPARK_DIR = "spark"
DASHBOARD_DIR = "dashboard"
AI_DIR = "ai"
LOGS_DIR = "logs"
TESTS_DIR = "tests"
DOCS_DIR = "docs"
SCRIPTS_DIR = "scripts"

DEFAULT_LOG_FILE = "retail_intelligence.log"
VALIDATION_REPORT_FILE = "validation_report.json"
PIPELINE_RUN_REPORT_FILE = "pipeline_run_report.json"

# Planned warehouse table names.
DIM_CUSTOMERS_TABLE = "dim_customers"
DIM_PRODUCTS_TABLE = "dim_products"
DIM_DATES_TABLE = "dim_dates"
DIM_LOCATIONS_TABLE = "dim_locations"
FACT_ORDERS_TABLE = "fact_orders"
FACT_ORDER_ITEMS_TABLE = "fact_order_items"
FACT_PAYMENTS_TABLE = "fact_payments"

# Planned source file names.
CUSTOMERS_SOURCE_FILE = "customers.csv"
PRODUCTS_SOURCE_FILE = "products.csv"
ORDERS_SOURCE_FILE = "orders.csv"
ORDER_ITEMS_SOURCE_FILE = "order_items.csv"
PAYMENTS_SOURCE_FILE = "payments.csv"
INVENTORY_SOURCE_FILE = "inventory.csv"
