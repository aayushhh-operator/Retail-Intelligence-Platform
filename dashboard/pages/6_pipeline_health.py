"""Pipeline Health Page."""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dashboard.services.db_service import execute_query
import plotly.express as px

st.set_page_config(page_title="Pipeline Health", page_icon="⚙️", layout="wide")
st.title("Airflow Pipeline Health")

st.markdown("Observability dashboard reading from Airflow metadata.")

query = "SELECT dag_id, execution_date, status, duration FROM airflow.dag_runs_log ORDER BY execution_date DESC LIMIT 50"
df = execute_query(query)

if not df.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Recent Runs")
        st.dataframe(df, use_container_width=True)
    with col2:
        if 'status' in df.columns:
            st.subheader("Run Status Distribution")
            fig = px.pie(df, names='status', title='DAG Status')
            st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No pipeline runs found, or the `airflow.dag_runs_log` table hasn't been created yet. Ensure Airflow has executed the DAG at least once.")
