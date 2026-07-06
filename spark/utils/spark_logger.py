"""Spark Logging Utilities."""

import logging

def get_spark_logger(spark):
    """Retrieve the Spark log4j logger for distributed logging."""
    log4jLogger = spark.sparkContext._jvm.org.apache.log4j
    return log4jLogger.LogManager.getLogger(__name__)

# Standard python logger for driver-node logging
logger = logging.getLogger("spark_jobs")
