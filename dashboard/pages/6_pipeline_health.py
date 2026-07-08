"""Pipeline Health Page."""

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
from dashboard.components.tables import render_styled_dataframe
from dashboard.components.states import render_empty_state
from dashboard.services.db_service import execute_query

configure_page("Pipeline Health", "🚦")
render_header("Pipeline Observability", "Airflow DAGs & Data Quality Monitoring")

query = "SELECT dag_id, execution_date, status, duration FROM airflow.dag_runs_log ORDER BY execution_date DESC LIMIT 50"
df = execute_query(query)

if not df.empty:
    # Calculate some dynamic metrics based on the DAG runs
    total_runs = len(df)
    success_runs = len(df[df['status'] == 'success'])
    failure_runs = len(df[df['status'] == 'failed'])
    success_rate = (success_runs / total_runs * 100) if total_runs > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        render_kpi_card("Success Rate", f"{success_rate:.1f}%", None, "normal", "✅")
    with col2:
        render_kpi_card("Failed Runs", f"{failure_runs}", "Needs Attention" if failure_runs > 0 else "All Good", "inverse" if failure_runs > 0 else "normal", "🚨")
    with col3:
        render_kpi_card("Total Runs", f"{total_runs}", None, "normal", "⚙️")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Run Status Distribution", "📋 Execution History"])
    
    with tab1:
        if "status" in df.columns:
            # We want specific colors for success/failed
            color_map = {'success': '#10b981', 'failed': '#ef4444', 'running': '#3b82f6'}
            fig = px.pie(df, names="status", title="DAG Run Status", hole=0.4, color='status', color_discrete_map=color_map)
            render_chart(fig)
            
    with tab2:
        st.markdown("##### Recent DAG Executions")
        render_styled_dataframe(df)
        
else:
    render_empty_state("No Pipeline Data", "The airflow.dag_runs_log table is empty or hasn't been created yet. Ensure Airflow has executed the DAG.", "🛠️")

