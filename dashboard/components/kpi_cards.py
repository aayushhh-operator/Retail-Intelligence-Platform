"""KPI Card Components."""

import streamlit as st


def render_kpi(label: str, value: str, delta: str = None):
    """Render a standard Streamlit metric card."""
    st.metric(label=label, value=value, delta=delta)
