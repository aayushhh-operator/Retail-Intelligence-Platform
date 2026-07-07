"""Operations Monitoring Page."""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import plotly.express as px
from dashboard.services.analytics_service import get_shipping_status

st.set_page_config(page_title="Operations Monitoring", page_icon="🚛", layout="wide")
st.title("Operations & Logistics")

st.subheader("Shipping Status Distribution")
ship_df = get_shipping_status()

if not ship_df.empty:
    fig = px.pie(ship_df, names="shipping_status", values="count", title="Order Fulfillment States")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No shipping data available.")
