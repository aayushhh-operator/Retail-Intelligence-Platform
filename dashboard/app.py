"""Main Streamlit Application."""

import streamlit as st
import os
import sys

# Ensure the root path is in sys.path so components can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.components.layout import configure_page, render_header

configure_page("Home")
render_header("Welcome to Retail Intelligence", "Enterprise Analytics Platform")

st.markdown("""
<div style='background-color: var(--card-bg, #ffffff); padding: 2rem; border-radius: 12px; border: 1px solid var(--border-color, #e0e0e0); margin-top: 1rem;'>
    <h3 style='margin-top: 0; color: var(--text-primary, #111827);'>Available Domains</h3>
    <ul style='color: var(--text-muted, #666); font-size: 1.1rem; line-height: 1.8;'>
        <li><strong>📊 Overview</strong>: High-level business KPIs and executive summary</li>
        <li><strong>📈 Sales Analysis</strong>: Deep dive into revenue and category performance</li>
        <li><strong>👥 Customer Insights</strong>: Segmentation, retention, and lifetime value</li>
        <li><strong>📦 Product Performance</strong>: Inventory health and top sellers</li>
        <li><strong>⚙️ Operations Monitoring</strong>: Supply chain and warehouse status</li>
        <li><strong>🚦 Pipeline Health</strong>: Orchestration observability and data quality</li>
        <li><strong>⚡ Spark Analytics</strong>: Distributed processing insights</li>
        <li><strong>🤖 AI Copilot</strong>: Natural language data analyst</li>
    </ul>
</div>
""", unsafe_allow_html=True)

