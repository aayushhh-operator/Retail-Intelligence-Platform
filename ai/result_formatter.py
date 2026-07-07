"""Format SQL Results."""

import pandas as pd


def format_dataframe(df: pd.DataFrame) -> str:
    if df.empty:
        return "No results found."
    # To avoid huge context limits, just summarize or stringify head
    return df.head(50).to_markdown()
