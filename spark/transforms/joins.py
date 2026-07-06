"""Join transformations."""
from pyspark.sql import DataFrame

def join_orders_products(orders_df: DataFrame, products_df: DataFrame) -> DataFrame:
    return orders_df.join(products_df, "product_id", "left")
