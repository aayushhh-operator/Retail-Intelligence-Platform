"""Tests for Phase 8 Spark Layer."""

import pandas as pd
import pytest
from pyspark.sql.types import (DoubleType, IntegerType, StringType,
                               StructField, StructType)

from spark.spark_session import SparkManager
from spark.transforms.aggregations import compute_clv


@pytest.fixture(scope="module")
def spark():
    """Create a local Spark session for testing."""
    return SparkManager.get_session()


def test_spark_session(spark):
    """Ensure the Spark session can be initialized."""
    assert spark is not None
    assert spark.sparkContext.appName == "RetailIntelligencePlatform"


def test_compute_clv(spark):
    """Test the CLV aggregation transformation."""
    # Create mock data
    schema = StructType(
        [
            StructField("order_id", StringType(), True),
            StructField("customer_id", StringType(), True),
            StructField("total_amount", DoubleType(), True),
        ]
    )

    data = [("O1", "C1", 100.0), ("O2", "C1", 50.0), ("O3", "C2", 200.0)]

    df = spark.createDataFrame(data, schema)

    # Run transformation
    result = compute_clv(df).toPandas()

    # Assertions
    c1 = result[result["customer_id"] == "C1"].iloc[0]
    assert c1["lifetime_value"] == 150.0
    assert c1["purchase_frequency"] == 2
    assert c1["average_order_value"] == 75.0

    c2 = result[result["customer_id"] == "C2"].iloc[0]
    assert c2["lifetime_value"] == 200.0
    assert c2["purchase_frequency"] == 1
