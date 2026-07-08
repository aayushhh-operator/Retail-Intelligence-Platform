"""Settings Page."""

import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from dashboard.components.layout import configure_page, render_header

configure_page("Settings", "⚙️")
render_header("Platform Settings", "Application preferences and version information")

st.markdown("""
<div style='background-color: var(--card-bg, #ffffff); padding: 2rem; border-radius: 12px; border: 1px solid var(--border-color, #e0e0e0);'>
    <h4 style='color: var(--text-primary, #111827); margin-top: 0;'>Application Settings</h4>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Preferences")
    st.selectbox("Theme Preference", ["System Default", "Light Mode", "Dark Mode"], disabled=True, help="Currently controlled by Streamlit Native Theme Settings (Top right menu).")
    st.selectbox("Default Date Range", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Year to Date"], index=1)
    st.slider("Auto-Refresh Interval (Minutes)", min_value=5, max_value=60, value=15, step=5)

with col2:
    st.markdown("##### System Info")
    st.markdown("**Version:** 2.0.0 (Premium UX Edition)")
    st.markdown("**Architecture:** Dockerized microservices (Airflow, Spark, Postgres)")
    st.markdown("**Database Connected:** `retail_intelligence` (PostgreSQL)")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Dashboard Cache"):
        st.cache_data.clear()
        st.success("Cache cleared successfully!")
