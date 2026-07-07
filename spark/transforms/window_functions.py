"""Window transformations."""

import pyspark.sql.functions as F
from pyspark.sql import DataFrame, Window


def sessionize_events(events_df: DataFrame, timeout_minutes: int = 30) -> DataFrame:
    """Group events into sessions based on inactivity timeout."""
    w = Window.partitionBy("customer_id").orderBy("event_timestamp")

    # Calculate time difference from previous event
    df = events_df.withColumn("prev_timestamp", F.lag("event_timestamp").over(w))
    df = df.withColumn(
        "time_diff_seconds",
        F.unix_timestamp("event_timestamp") - F.unix_timestamp("prev_timestamp"),
    )

    # Flag new sessions where gap > timeout
    df = df.withColumn(
        "is_new_session",
        F.when(F.col("time_diff_seconds") > (timeout_minutes * 60), 1).otherwise(0),
    )
    # The first event for a customer is also a new session (time_diff is null)
    df = df.withColumn(
        "is_new_session",
        F.when(F.col("prev_timestamp").isNull(), 1).otherwise(F.col("is_new_session")),
    )

    # Cumulative sum to create a session ID
    session_window = (
        Window.partitionBy("customer_id")
        .orderBy("event_timestamp")
        .rowsBetween(Window.unboundedPreceding, 0)
    )
    df = df.withColumn("session_group_id", F.sum("is_new_session").over(session_window))

    # Create final unique session ID
    df = df.withColumn(
        "session_id", F.concat_ws("_", F.col("customer_id"), F.col("session_group_id"))
    )

    return df.drop(
        "prev_timestamp", "time_diff_seconds", "is_new_session", "session_group_id"
    )
