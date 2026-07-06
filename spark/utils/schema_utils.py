"""Spark schema utilities."""
def cast_columns(df, type_map):
    for col_name, data_type in type_map.items():
        df = df.withColumn(col_name, df[col_name].cast(data_type))
    return df
