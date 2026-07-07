"""Customer Insights Page."""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import plotly.express as px
from dashboard.services.analytics_service import get_top_customers

st.set_page_config(page_title="Customer Insights", page_icon="👥", layout="wide")
st.title("Customer Insights")

st.subheader("Top 10 Customers by Lifetime Value (LTV)")
cust_df = get_top_customers()

if not cust_df.empty:
    st.dataframe(cust_df, use_container_width=True)
    
    st.subheader("Order Count vs Lifetime Value")
    fig = px.scatter(cust_df, x="order_count", y="lifetime_value", hover_name="name", size="lifetime_value", color="lifetime_value")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No customer data available.")
