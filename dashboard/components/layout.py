"""Layout components for the Streamlit dashboard."""

import streamlit as st
from pathlib import Path
from datetime import datetime

def load_css():
    """Load and inject custom CSS."""
    css_file = Path(__file__).resolve().parent.parent / "styles" / "theme.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_header(title: str, subtitle: str = None):
    """Render a standardized page header."""
    load_css()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(title)
        if subtitle:
            st.markdown(f"<p style='color: var(--text-muted, #666); font-size: 1.1rem; margin-top: -1rem; margin-bottom: 2rem;'>{subtitle}</p>", unsafe_allow_html=True)
            
    with col2:
        st.markdown(
            f"""
            <div style='text-align: right; color: var(--text-muted, #666); font-size: 0.9rem;'>
                Last Refreshed<br>
                <strong>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</strong>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    st.markdown("<hr style='margin-top: 0; margin-bottom: 2rem;'>", unsafe_allow_html=True)

def configure_page(page_title: str, page_icon: str = "📊", layout: str = "wide"):
    """Standard page configuration."""
    st.set_page_config(
        page_title=f"{page_title} | Retail Intelligence",
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state="expanded"
    )
    load_css()
