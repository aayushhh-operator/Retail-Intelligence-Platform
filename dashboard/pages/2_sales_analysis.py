"""Sales Analysis Page."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import plotly.express as px
import streamlit as st

from dashboard.services.analytics_service import (get_sales_by_category,
                                                  get_sales_by_region)

st.set_page_config(page_title="Sales Analysis", page_icon="📈", layout="wide")
st.title("Sales Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Category")
    cat_df = get_sales_by_category()
    if not cat_df.empty:
        fig = px.bar(cat_df, x="category", y="revenue", title="Category Performance")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category data available.")

with col2:
    st.subheader("Revenue by Country")
    reg_df = get_sales_by_region()
    if not reg_df.empty:
        fig = px.pie(
            reg_df,
            names="country",
            values="revenue",
            title="Regional Revenue Share",
            hole=0.4,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No regional data available.")
