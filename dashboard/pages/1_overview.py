"""Overview Page."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import plotly.express as px
import streamlit as st

from dashboard.services.analytics_service import (get_overview_kpis,
                                                  get_sales_trend)

st.set_page_config(page_title="Overview", page_icon="📈", layout="wide")
st.title("Business Overview")

kpis = get_overview_kpis()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Revenue", f"${kpis['revenue']:,.2f}")
with col2:
    st.metric("Total Orders", f"{kpis['orders']:,}")
with col3:
    st.metric("Avg Order Value", f"${kpis['aov']:,.2f}")

st.markdown("---")
st.subheader("Revenue Trend")
trend_df = get_sales_trend()

if not trend_df.empty:
    fig = px.line(trend_df, x="dt", y="daily_revenue", title="Daily Revenue")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No sales data available to plot yet.")
