"""State components for the Streamlit dashboard."""

import streamlit as st

def render_loading(message: str = "Loading data..."):
    """Render a standardized loading state."""
    with st.spinner(message):
        yield

def render_empty_state(title: str, message: str, icon: str = "📭"):
    """Render a standardized empty state."""
    st.markdown(
        f"""
        <div style='text-align: center; padding: 4rem 2rem; background-color: var(--bg-secondary, #f9fafb); border-radius: 12px; border: 1px dashed var(--border-color, #e0e0e0); margin: 2rem 0;'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>{icon}</div>
            <h3 style='color: var(--text-primary, #111827); margin-bottom: 0.5rem;'>{title}</h3>
            <p style='color: var(--text-muted, #666);'>{message}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_error_state(title: str, error: Exception):
    """Render a standardized error state."""
    st.error(f"**{title}**")
    with st.expander("Technical Details"):
        st.code(str(error))
    
    st.markdown(
        """
        <div style='text-align: center; margin-top: 1rem;'>
            <p style='color: var(--text-muted, #666); font-size: 0.9rem;'>If this issue persists, please contact data engineering support.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
