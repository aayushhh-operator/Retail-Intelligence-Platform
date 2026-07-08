"""Customer Insights Page."""

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
from dashboard.services.analytics_service import get_top_customers

configure_page("Customer Insights", "👥")
render_header("Customer Insights", "Segmentation, retention, and lifetime value")

filters = render_global_filters(show_date=True, show_category=False, show_region=True)

cust_df = get_top_customers()

if not cust_df.empty:
    st.markdown("##### Top 10 Customers by Lifetime Value (LTV)")
    render_styled_dataframe(cust_df.head(10))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Order Count vs Lifetime Value")
    
    fig = px.scatter(
        cust_df,
        x="order_count",
        y="lifetime_value",
        hover_name="name",
        size="lifetime_value",
        color="lifetime_value",
        labels={"order_count": "Number of Orders", "lifetime_value": "Lifetime Value ($)"}
    )
    # Remove color scale bar for cleaner look
    fig.update_layout(coloraxis_showscale=False)
    render_chart(fig, height=500)
else:
    render_empty_state("No Customer Data", "The data warehouse has not accumulated enough customer activity to generate insights.", "👥")

