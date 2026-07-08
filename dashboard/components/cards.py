"""Standardized metric and KPI cards."""

import streamlit as st

def render_kpi_card(title: str, value: str, delta: str = None, delta_color: str = "normal", icon: str = None):
    """
    Render a polished KPI card using Streamlit's native metric component 
    (styled globally via theme.css).
    """
    if icon:
        title = f"{icon} {title}"
        
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )
