"""Plotly chart configurations for consistent, enterprise-grade visuals."""

import plotly.graph_objects as go
import streamlit as st

# Corporate color palette
CHART_COLORS = [
    '#2563eb', # Blue
    '#3b82f6', # Light Blue
    '#0ea5e9', # Sky
    '#06b6d4', # Cyan
    '#14b8a6', # Teal
    '#059669', # Emerald
    '#10b981', # Green
]

def apply_corporate_theme(fig: go.Figure) -> go.Figure:
    """Apply a clean, minimalist theme to any Plotly figure."""
    fig.update_layout(
        font=dict(family="Inter, sans-serif", color="#666666"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        colorway=CHART_COLORS,
        margin=dict(t=40, r=20, b=40, l=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title_text=""
        ),
        hovermode="x unified",
        modebar=dict(remove=["lasso2d", "select2d"])
    )
    
    fig.update_xaxes(
        showgrid=False,
        linecolor="#e0e0e0",
        tickcolor="#e0e0e0"
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#f3f4f6",
        linecolor="#e0e0e0",
        tickcolor="#e0e0e0",
        zerolinecolor="#e0e0e0"
    )
    
    return fig

def render_chart(fig: go.Figure, use_container_width: bool = True, height: int = 400):
    """Render a Plotly figure with the corporate theme applied."""
    themed_fig = apply_corporate_theme(fig)
    themed_fig.update_layout(height=height)
    st.plotly_chart(themed_fig, use_container_width=use_container_width, config={'displayModeBar': False})
