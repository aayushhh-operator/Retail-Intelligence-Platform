"""Spark Session Manager."""

import logging
from pyspark.sql import SparkSession
from spark.config import (
    SPARK_MASTER, SPARK_APP_NAME, SPARK_DRIVER_MEMORY, 
    SPARK_EXECUTOR_MEMORY, CHECKPOINT_DIR
)

logger = logging.getLogger(__name__)

class SparkManager:
    """Manages the creation and configuration of the Spark Session."""
    
    _spark = None

    @classmethod
    def get_session(cls) -> SparkSession:
        """Returns a configured SparkSession singleton."""
        if cls._spark is None:
            logger.info(f"Initializing Spark Session: {SPARK_APP_NAME} on {SPARK_MASTER}")
            try:
                cls._spark = (
                    SparkSession.builder
                    .master(SPARK_MASTER)
                    .appName(SPARK_APP_NAME)
                    .config("spark.driver.memory", SPARK_DRIVER_MEMORY)
                    .config("spark.executor.memory", SPARK_EXECUTOR_MEMORY)
                    # Dynamically fetch PostgreSQL JDBC Driver
                    .config("spark.jars.packages", "org.postgresql:postgresql:42.6.0")
                    # Memory & performance tuning defaults
                    .config("spark.sql.shuffle.partitions", "20") # Reduced for local/small datasets
                    .config("spark.sql.adaptive.enabled", "true") # Enable AQE
                    .config("spark.sql.parquet.compression.codec", "snappy")
                    .getOrCreate()
                )
                
                # Set checkpoint directory for stateful operations (like some window functions)
                cls._spark.sparkContext.setCheckpointDir(str(CHECKPOINT_DIR))
                
                # Reduce logging verbosity in the console
                cls._spark.sparkContext.setLogLevel("WARN")
                
                logger.info("Spark Session initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Spark Session: {e}")
                raise
                
        return cls._spark

    @classmethod
    def stop_session(cls):
        """Stops the Spark Session gracefully."""
        if cls._spark:
            logger.info("Stopping Spark Session...")
            cls._spark.stop()
            cls._spark = None
