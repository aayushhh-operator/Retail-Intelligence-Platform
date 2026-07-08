"""Operations Monitoring Page."""

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
from dashboard.components.cards import render_kpi_card
from dashboard.services.analytics_service import get_shipping_status

configure_page("Operations Monitoring", "🚛")
render_header("Operations & Logistics", "Supply chain and warehouse status")

filters = render_global_filters(show_date=True, show_category=False, show_region=True)

ship_df = get_shipping_status()

if not ship_df.empty:
    total_orders = ship_df['count'].sum()
    delivered = ship_df[ship_df['shipping_status'] == 'Delivered']['count'].sum() if 'Delivered' in ship_df['shipping_status'].values else 0
    delivery_rate = (delivered / total_orders * 100) if total_orders > 0 else 0
    
    col1, col2 = st.columns(2)
    with col1:
        render_kpi_card("Total Orders Processed", f"{total_orders:,}", None, "normal", "📦")
    with col2:
        render_kpi_card("Delivery Rate", f"{delivery_rate:.1f}%", None, "normal", "🚚")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Shipping Status Distribution")
    
    fig = px.pie(
        ship_df,
        names="shipping_status",
        values="count",
        hole=0.4
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    render_chart(fig)
else:
    render_empty_state("No Logistics Data", "No shipping status updates recorded.", "🚛")
