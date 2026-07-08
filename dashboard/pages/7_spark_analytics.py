"""Spark Analytics Page."""

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
from dashboard.services.db_service import execute_query

configure_page("Spark Analytics", "⚡")
render_header("Distributed Spark Analytics", "Visualizing heavy analytical workloads (Sessionization & aggregations)")

query = (
    "SELECT * FROM analytics.spark_customer_clv ORDER BY lifetime_value DESC LIMIT 20"
)
df = execute_query(query)

if not df.empty:
    st.markdown("##### Spark Customer CLV Outputs")
    fig = px.bar(
        df,
        x="customer_id",
        y="lifetime_value",
        labels={"customer_id": "Customer ID", "lifetime_value": "Lifetime Value ($)"}
    )
    render_chart(fig)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### Underlying Distributed Dataset")
    render_styled_dataframe(df)
else:
    render_empty_state("No Spark Data", "Spark jobs have not generated output to `analytics.spark_customer_clv` yet. Ensure Phase 8 Spark jobs have run.", "⚡")
