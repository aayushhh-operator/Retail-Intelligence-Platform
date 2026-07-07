"""Main Streamlit Application."""

import streamlit as st

st.set_page_config(
    page_title="Retail Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Retail Intelligence Platform")
st.markdown("""
Welcome to the Retail Intelligence Platform Analytics Dashboard.
Use the sidebar to navigate between different domains:
- **Overview**: High-level business KPIs
- **Sales Analysis**: Deep dive into revenue and category performance
- **Customer Insights**: Segmentation and CLV
- **Product Performance**: Inventory and top sellers
- **Operations Monitoring**: Supply chain and warehouse status
- **Pipeline Health**: Airflow orchestration observability
- **Spark Analytics**: Distributed workloads
""")
