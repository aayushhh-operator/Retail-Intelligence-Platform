"""Product Performance Page."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import plotly.express as px
import streamlit as st

from dashboard.services.analytics_service import get_product_performance

st.set_page_config(page_title="Product Performance", page_icon="📦", layout="wide")
st.title("Product Performance")

st.subheader("Top Performing Products")
prod_df = get_product_performance()

if not prod_df.empty:
    # Sort for horizontal bar chart
    prod_df = prod_df.sort_values(by="revenue", ascending=True)
    fig = px.bar(
        prod_df,
        x="revenue",
        y="product_name",
        orientation="h",
        title="Revenue by Product",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        prod_df.sort_values(by="revenue", ascending=False), use_container_width=True
    )
else:
    st.info("No product data available.")
