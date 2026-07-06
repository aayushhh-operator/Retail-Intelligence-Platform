"""Abstract Base Class for Spark Jobs."""

from abc import ABC, abstractmethod
import logging
from pyspark.sql import DataFrame
from spark.spark_session import SparkManager
import time

logger = logging.getLogger(__name__)

class BaseSparkJob(ABC):
    """Abstract base class defining the standard Spark Job lifecycle."""

    def __init__(self, job_name: str):
        self.job_name = job_name
        self.spark = SparkManager.get_session()
        
    @abstractmethod
    def load_data(self) -> dict[str, DataFrame]:
        """Load required DataFrames and return them in a dictionary."""
        pass
        
    @abstractmethod
    def transform(self, dataframes: dict[str, DataFrame]) -> DataFrame:
        """Apply business transformations and return the final DataFrame."""
        pass
        
    @abstractmethod
    def write_output(self, df: DataFrame) -> None:
        """Write the resulting DataFrame to the target destination."""
        pass

    def run(self) -> None:
        """Execute the full job lifecycle."""
        logger.info(f"Starting Spark Job: {self.job_name}")
        start_time = time.time()
        
        try:
            logger.info(f"[{self.job_name}] Loading data...")
            dataframes = self.load_data()
            
            logger.info(f"[{self.job_name}] Applying transformations...")
            result_df = self.transform(dataframes)
            
            logger.info(f"[{self.job_name}] Writing output...")
            self.write_output(result_df)
            
            duration = time.time() - start_time
            logger.info(f"Completed Spark Job: {self.job_name} in {duration:.2f} seconds.")
            
        except Exception as e:
            logger.error(f"Spark Job '{self.job_name}' failed: {e}")
            raise
