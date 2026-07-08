"""Global filter panel component."""

import streamlit as st
from datetime import datetime, timedelta

def render_global_filters(show_date: bool = True, show_category: bool = True, show_region: bool = True) -> dict:
    """
    Render a global filter panel, typically in the sidebar.
    Returns a dictionary of selected filter values.
    """
    filters = {}
    
    st.sidebar.markdown("### 🔍 Global Filters")
    st.sidebar.markdown("<hr style='margin: 0.5rem 0 1rem 0;'>", unsafe_allow_html=True)
    
    if show_date:
        st.sidebar.markdown("**Date Range**")
        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)
        
        date_range = st.sidebar.date_input(
            "Select Range",
            value=(thirty_days_ago, today),
            max_value=today,
            label_visibility="collapsed"
        )
        
        if len(date_range) == 2:
            filters['start_date'], filters['end_date'] = date_range
        else:
            filters['start_date'] = date_range[0]
            filters['end_date'] = today.date()
            
    if show_category:
        st.sidebar.markdown("**Category**")
        categories = ["All", "Electronics", "Clothing", "Home", "Sports", "Beauty"]
        filters['category'] = st.sidebar.selectbox("Select Category", options=categories, label_visibility="collapsed")
        
    if show_region:
        st.sidebar.markdown("**Region**")
        regions = ["All", "North America", "Europe", "Asia Pacific", "Latin America"]
        filters['region'] = st.sidebar.selectbox("Select Region", options=regions, label_visibility="collapsed")
        
    return filters
