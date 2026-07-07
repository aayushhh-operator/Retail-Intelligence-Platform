"""High-level Star Schema builder."""

import logging

from analytics.config import SQL_DIR
from analytics.dim_builder import DimensionBuilder
from analytics.fact_builder import FactBuilder
from analytics.utils import AnalyticsDBManager

logger = logging.getLogger(__name__)


class StarSchemaBuilder:
    """Coordinates the building of the entire Star Schema."""

    def __init__(self, db: AnalyticsDBManager):
        self.db = db
        self.dim_builder = DimensionBuilder(db)
        self.fact_builder = FactBuilder(db)

    def initialize_schema(self) -> None:
        """Create schemas, metadata tables, and empty facts/dimensions."""
        logger.info("Initializing analytics schema and tables...")
        self.db.execute_sql_file(str(SQL_DIR / "create_analytics_schema.sql"))
        self.db.execute_sql_file(str(SQL_DIR / "create_dimensions.sql"))
        self.db.execute_sql_file(str(SQL_DIR / "create_facts.sql"))

    def truncate_and_reload(self) -> None:
        """Drop existing fact data and rebuild."""
        logger.info("Executing TRUNCATE + RELOAD strategy...")
        self.db.execute_sql_file(str(SQL_DIR / "drop_and_rebuild.sql"))

    def build(self, run_id: str) -> None:
        """Run the full transformation pipeline."""
        try:
            self.dim_builder.build_all(run_id)
            self.fact_builder.build_all(run_id)
            logger.info("Star schema built successfully.")
        except Exception as e:
            logger.error(f"Failed to build star schema: {e}")
            raise
