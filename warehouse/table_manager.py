"""Table management utilities."""

import logging
from warehouse.database import DatabaseManager

logger = logging.getLogger(__name__)

class TableManager:
    """Manages table-level operations like truncation."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def truncate_table(self, schema: str, table: str) -> None:
        """Truncate a specific table (Cascade if necessary)."""
        logger.info(f"Truncating table {schema}.{table}...")
        # Use CASCADE to prevent foreign key constraint violations during truncate
        self.db.execute_query(f"TRUNCATE TABLE {schema}.{table} CASCADE;")
        logger.info(f"Successfully truncated {schema}.{table}.")
