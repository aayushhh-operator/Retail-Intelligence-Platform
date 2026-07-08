"""Sales Analysis Page."""

import sys
import os
from pathlib import Path

# Ensure root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plotly.express as px
import streamlit as st

from dashboard.components.layout import configure_page, render_header
from dashboard.components.charts import render_chart
from dashboard.components.states import render_empty_state
from dashboard.components.filters import render_global_filters
from dashboard.services.analytics_service import get_sales_by_category, get_sales_by_region

configure_page("Sales Analysis", "📈")
render_header("Sales Analysis", "Deep dive into revenue, geography, and categories")

# Inject filters (currently decorative as backend is fixed for this phase, but good UX)
filters = render_global_filters(show_date=True, show_category=False, show_region=False)

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Revenue by Category")
    cat_df = get_sales_by_category()
    if not cat_df.empty:
        fig = px.bar(cat_df, x="category", y="revenue", 
                     labels={"category": "", "revenue": "Revenue ($)"})
        render_chart(fig)
    else:
        render_empty_state("No Category Data", "No category sales recorded.", "🏷️")

with col2:
    st.markdown("##### Regional Revenue Share")
    reg_df = get_sales_by_region()
    if not reg_df.empty:
        fig = px.pie(
            reg_df,
            names="country",
            values="revenue",
            hole=0.5,
        )
        # Tweak pie chart text
        fig.update_traces(textposition='inside', textinfo='percent+label')
        render_chart(fig)
    else:
        render_empty_state("No Regional Data", "No regional sales recorded.", "🌍")

