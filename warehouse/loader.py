"""Main loader coordinating dataset validation and insertion."""

import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from warehouse.connection import DatabaseConnection
from warehouse.csv_loader import CSVLoader
from warehouse.exceptions import LoadError, SchemaValidationError
from warehouse.load_history import LoadHistoryRecorder
from warehouse.table_manager import TableManager
from warehouse.transaction_manager import TransactionManager
from warehouse.validators import DatasetValidator

logger = logging.getLogger(__name__)


class WarehouseLoader:
    """Orchestrates loading datasets with transactions and validation."""

    def __init__(self, connection: DatabaseConnection, run_id: str):
        self.connection = connection
        self.run_id = run_id
        self.csv_loader = CSVLoader()
        self.transaction_mgr = TransactionManager(connection)
        self.table_mgr = TableManager(from_connection(connection))
        self.history_recorder = LoadHistoryRecorder(from_connection(connection))

    def load_dataset(
        self,
        filepath: Path,
        dataset_name: str,
        schema: str = "warehouse",
        strategy: str = "Replace",
    ) -> int:
        """Validate, prepare, and load a dataset within a transaction."""
        logger.info(f"Starting load for dataset {dataset_name} (Strategy: {strategy})")

        try:
            # 1. Read subset of CSV to validate schema (or whole if needed, but pd.read_csv is fast)
            # Actually just load first row for schema check
            df_preview = pd.read_csv(filepath, nrows=1)
            DatasetValidator.validate_schema(dataset_name, df_preview)

            rows_loaded = 0
            with self.transaction_mgr.transaction() as session:
                if strategy.lower() == "replace":
                    # Cannot use TRUNCATE easily inside transaction manager session without a commit block usually,
                    # but we can execute raw SQL within the session context.
                    session.execute(
                        text(f"TRUNCATE TABLE {schema}.{dataset_name} CASCADE;")
                    )

                rows_loaded = self.csv_loader.load(
                    filepath, dataset_name, schema, session
                )

            self.history_recorder.record_load(
                run_id=self.run_id,
                dataset=dataset_name,
                rows_read=rows_loaded,  # assuming 1:1 for simplicity unless tracked elsewhere
                rows_loaded=rows_loaded,
                rows_failed=0,
                strategy=strategy,
                status="SUCCESS",
            )
            return rows_loaded

        except Exception as e:
            logger.error(f"Failed to load dataset {dataset_name}: {e}")
            self.history_recorder.record_load(
                run_id=self.run_id,
                dataset=dataset_name,
                rows_read=0,
                rows_loaded=0,
                rows_failed=0,
                strategy=strategy,
                status="FAILED",
            )
            raise LoadError(f"Failed to load {dataset_name}") from e


def from_connection(connection: DatabaseConnection):
    from warehouse.database import DatabaseManager

    return DatabaseManager(connection)
