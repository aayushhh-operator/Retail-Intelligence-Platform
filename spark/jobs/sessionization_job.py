"""SessionizationJob."""

from spark.base_job import BaseSparkJob
from spark.config import JDBC_PROPERTIES, JDBC_URL
from spark.warehouse_writer import WarehouseWriter


class SessionizationJob(BaseSparkJob):
    def __init__(self):
        super().__init__("SessionizationJob")

    def load_data(self):
        # Load from processed CSV for speed (data lake simulation)
        from spark.config import PROCESSED_DATA_DIR

        events_df = self.spark.read.csv(
            str(PROCESSED_DATA_DIR / "website_events.csv"),
            header=True,
            inferSchema=True,
        )
        # Handle column naming mismatch if any
        if "timestamp" in events_df.columns:
            events_df = events_df.withColumnRenamed("timestamp", "event_timestamp")
        return {"events": events_df}

    def transform(self, dataframes):
        from spark.transforms.window_functions import sessionize_events

        return sessionize_events(dataframes["events"])

    def write_output(self, df):
        WarehouseWriter.write_to_parquet(df, "sessionized_events", mode="overwrite")


def main():
    job = SessionizationJob()
    job.run()


if __name__ == "__main__":
    main()
