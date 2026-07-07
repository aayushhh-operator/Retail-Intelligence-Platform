"""Entry point for Phase 5 PostgreSQL Data Warehouse Loading Framework."""

import logging
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.logging_config import configure_logging
from config.pipeline_run import get_pipeline_run_id, set_pipeline_run_id
from warehouse.config import PROCESSED_DATA_DIR
from warehouse.connection import DatabaseConnection
from warehouse.database import DatabaseManager
from warehouse.load_history import LoadHistoryRecorder
from warehouse.loader import WarehouseLoader
from warehouse.metadata import WarehouseMetadata
from warehouse.schema_manager import SchemaManager


def main() -> None:
    """Run the warehouse loader."""
    pipeline_run_id = set_pipeline_run_id()
    logger = configure_logging(pipeline_run_id=pipeline_run_id)
    start_time = datetime.now()

    logger.info("Initializing Warehouse Phase 5...")

    connection = DatabaseConnection()
    try:
        connection.connect()
        db_manager = DatabaseManager(connection)

        # 1. Schema Management
        schema_manager = SchemaManager(db_manager)
        schema_manager.initialize_warehouse()

        # 2. Loading Pipeline
        loader = WarehouseLoader(connection, pipeline_run_id)
        metadata_writer = WarehouseMetadata()
        history_recorder = LoadHistoryRecorder(db_manager)

        history_recorder.record_pipeline_run(
            pipeline_run_id, "RUNNING", start_time, datetime.now()
        )

        datasets = [
            "customers",
            "products",
            "inventory",
            "orders",
            "payments",
            "shipping",
            "reviews",
            "website_events",
        ]

        for dataset in datasets:
            filepath = PROCESSED_DATA_DIR / f"{dataset}.csv"
            if not filepath.exists():
                logger.warning(f"Dataset {dataset} not found at {filepath}. Skipping.")
                continue

            try:
                # Every dataset loads independently
                rows = loader.load_dataset(filepath, dataset, strategy="Replace")
                metadata_writer.record_success(dataset, rows)
            except Exception as e:
                logger.error(
                    f"Error loading {dataset}. Pipeline will continue. Error: {e}"
                )
                metadata_writer.record_failure(dataset)

        # 3. Save Metadata
        metadata_writer.save()

        # 4. Record Success
        history_recorder.record_pipeline_run(
            pipeline_run_id, "SUCCESS", start_time, datetime.now()
        )
        logger.info("Warehouse loading complete.")

    except Exception as e:
        logger.critical(f"Warehouse pipeline failed: {e}")
        history_recorder = LoadHistoryRecorder(DatabaseManager(connection))
        history_recorder.record_pipeline_run(
            pipeline_run_id, "FAILED", start_time, datetime.now()
        )
    finally:
        connection.dispose()


if __name__ == "__main__":
    main()
