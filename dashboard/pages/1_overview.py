"""Overview Page."""

import sys
import os
from pathlib import Path

# Ensure root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plotly.express as px
import streamlit as st

from dashboard.components.layout import configure_page, render_header
from dashboard.components.cards import render_kpi_card
from dashboard.components.charts import render_chart
from dashboard.components.states import render_empty_state
from dashboard.services.analytics_service import get_overview_kpis, get_sales_trend

configure_page("Overview")
render_header("Business Overview", "High-level Executive Summary")

kpis = get_overview_kpis()

col1, col2, col3 = st.columns(3)
with col1:
    render_kpi_card("Total Revenue", f"${kpis['revenue']:,.2f}", "+5.2%", "normal", "💵")
with col2:
    render_kpi_card("Total Orders", f"{kpis['orders']:,}", "+1.1%", "normal", "📦")
with col3:
    render_kpi_card("Avg Order Value", f"${kpis['aov']:,.2f}", "-0.5%", "inverse", "🛒")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📈 Revenue Trend")

trend_df = get_sales_trend()

if not trend_df.empty:
    fig = px.area(trend_df, x="dt", y="daily_revenue", 
                  title="Daily Revenue (30 Days)",
                  labels={"dt": "Date", "daily_revenue": "Revenue ($)"})
    render_chart(fig)
else:
    render_empty_state("No Sales Data", "The data warehouse has not accumulated enough sales data to render this chart.", "📉")

