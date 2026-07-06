"""Warehouse Writer utility for JDBC operations."""

import logging
from pyspark.sql import DataFrame
from spark.config import JDBC_URL, JDBC_PROPERTIES, SPARK_OUTPUT_DIR

logger = logging.getLogger(__name__)

class WarehouseWriter:
    """Handles writing Spark DataFrames back to PostgreSQL or local Parquet."""

    @staticmethod
    def write_to_postgres(df: DataFrame, table_name: str, mode: str = "overwrite") -> None:
        """Write DataFrame to PostgreSQL via JDBC."""
        try:
            logger.info(f"Writing to PostgreSQL table '{table_name}' with mode '{mode}'...")
            df.write.jdbc(
                url=JDBC_URL,
                table=table_name,
                mode=mode,
                properties=JDBC_PROPERTIES
            )
            logger.info(f"Successfully wrote to {table_name}.")
        except Exception as e:
            logger.error(f"Failed to write to PostgreSQL table {table_name}: {e}")
            raise

    @staticmethod
    def write_to_parquet(df: DataFrame, directory_name: str, mode: str = "overwrite") -> None:
        """Write DataFrame to local Parquet for staging/simulation."""
        try:
            output_path = str(SPARK_OUTPUT_DIR / directory_name)
            logger.info(f"Writing Parquet to '{output_path}' with mode '{mode}'...")
            df.write.mode(mode).parquet(output_path)
            logger.info(f"Successfully wrote parquet to {output_path}.")
        except Exception as e:
            logger.error(f"Failed to write parquet to {directory_name}: {e}")
            raise
