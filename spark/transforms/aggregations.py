"""Aggregation transformations."""

import pyspark.sql.functions as F
from pyspark.sql import DataFrame


def compute_clv(df: DataFrame) -> DataFrame:
    return df.groupBy("customer_id").agg(
        F.sum("total_amount").alias("lifetime_value"),
        F.count("order_id").alias("purchase_frequency"),
        F.avg("total_amount").alias("average_order_value"),
    )
