"""Auto-generate Plotly Charts."""
import pandas as pd
import plotly.express as px

def generate_chart(df: pd.DataFrame):
    if df.empty or len(df.columns) < 2:
        return None
    # Basic heuristic: if first column is date-like or categorical and second is numeric
    cols = df.columns
    if pd.api.types.is_numeric_dtype(df[cols[1]]):
        if 'date' in cols[0].lower() or 'dt' in cols[0].lower():
            return px.line(df, x=cols[0], y=cols[1], title="Trend Analysis")
        else:
            return px.bar(df, x=cols[0], y=cols[1], title="Distribution Analysis")
    return None
