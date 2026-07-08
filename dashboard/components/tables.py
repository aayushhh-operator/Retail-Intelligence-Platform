"""Styled table components."""

import streamlit as st
import pandas as pd

def render_styled_dataframe(df: pd.DataFrame, height: int = 400):
    """Render a DataFrame with native Streamlit column configuration for a premium feel."""
    if df.empty:
        st.info("No data available for the current selection.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        hide_index=True
    )
