"""Schema manager for the warehouse framework."""

import logging
from pathlib import Path

from warehouse.config import SQL_DIR
from warehouse.database import DatabaseManager
from warehouse.exceptions import SchemaCreationError

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages creation of schemas, tables, indexes, and constraints."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def initialize_warehouse(self) -> None:
        """Execute all DDL scripts to set up the warehouse."""
        try:
            logger.info("Initializing warehouse schemas...")
            self._execute_sql_script("schema.sql")

            logger.info("Creating warehouse tables...")
            self._execute_sql_script("create_tables.sql")

            logger.info("Creating metadata tables...")
            self._execute_sql_script("load_history.sql")

            logger.info("Creating indexes...")
            self._execute_sql_script("create_indexes.sql")

            logger.info("Adding constraints...")
            self._execute_sql_script("constraints.sql")

            logger.info("Warehouse initialization complete.")
        except Exception as e:
            logger.error(f"Failed to initialize warehouse: {e}")
            raise SchemaCreationError("Error during warehouse initialization.") from e

    def _execute_sql_script(self, filename: str) -> None:
        filepath = SQL_DIR / filename
        if not filepath.is_file():
            logger.warning(f"SQL script not found: {filepath}. Skipping.")
            return
        self.db.execute_sql_file(str(filepath))
