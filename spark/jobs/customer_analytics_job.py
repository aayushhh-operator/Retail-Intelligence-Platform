"""CustomerAnalyticsJob."""

from spark.base_job import BaseSparkJob
from spark.config import JDBC_PROPERTIES, JDBC_URL
from spark.warehouse_writer import WarehouseWriter


class CustomerAnalyticsJob(BaseSparkJob):
    def __init__(self):
        super().__init__("CustomerAnalyticsJob")

    def load_data(self):
        # Load from PG
        orders_df = self.spark.read.jdbc(
            url=JDBC_URL, table="warehouse.orders", properties=JDBC_PROPERTIES
        )
        return {"orders": orders_df}

    def transform(self, dataframes):
        from spark.transforms.aggregations import compute_clv

        return compute_clv(dataframes["orders"])

    def write_output(self, df):
        WarehouseWriter.write_to_postgres(
            df, "analytics.spark_customer_clv", mode="overwrite"
        )


def main():
    job = CustomerAnalyticsJob()
    job.run()


if __name__ == "__main__":
    main()
