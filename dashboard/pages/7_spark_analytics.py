"""Spark Analytics Page."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import plotly.express as px
import streamlit as st

from dashboard.services.db_service import execute_query

st.set_page_config(page_title="Spark Analytics", page_icon="⚡", layout="wide")
st.title("Distributed Spark Analytics")
st.markdown(
    "Visualizing heavy analytical workloads (Sessionization, large aggregations)."
)

st.subheader("Spark Customer CLV Outputs")
query = (
    "SELECT * FROM analytics.spark_customer_clv ORDER BY lifetime_value DESC LIMIT 20"
)
df = execute_query(query)

if not df.empty:
    fig = px.bar(
        df,
        x="customer_id",
        y="lifetime_value",
        title="Customer LTV (Computed by Spark)",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(
        "Spark jobs have not generated output to `analytics.spark_customer_clv` yet. Run Phase 8."
    )
