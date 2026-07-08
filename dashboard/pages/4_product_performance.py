"""Product Performance Page."""

import sys
import os
from pathlib import Path

# Ensure root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plotly.express as px
import streamlit as st

from dashboard.components.layout import configure_page, render_header
from dashboard.components.charts import render_chart
from dashboard.components.tables import render_styled_dataframe
from dashboard.components.states import render_empty_state
from dashboard.components.filters import render_global_filters
from dashboard.services.analytics_service import get_product_performance

configure_page("Product Performance", "📦")
render_header("Product Performance", "Inventory health and top sellers")

filters = render_global_filters(show_date=True, show_category=True, show_region=False)

prod_df = get_product_performance()

if not prod_df.empty:
    st.markdown("##### Top Performing Products by Revenue")
    
    # Sort for horizontal bar chart
    prod_df_sorted = prod_df.sort_values(by="revenue", ascending=True).tail(15) # Show top 15
    fig = px.bar(
        prod_df_sorted,
        x="revenue",
        y="product_name",
        orientation="h",
        labels={"revenue": "Total Revenue ($)", "product_name": ""}
    )
    render_chart(fig, height=600)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Detailed Product Metrics")
    render_styled_dataframe(prod_df.sort_values(by="revenue", ascending=False))

else:
    render_empty_state("No Product Data", "The data warehouse has not accumulated enough product sales to generate insights.", "📦")
