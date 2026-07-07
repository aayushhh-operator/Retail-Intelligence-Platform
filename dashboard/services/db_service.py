"""Database Connection Service."""
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from dashboard.config import DB_URI

@st.cache_resource
def get_engine():
    return create_engine(DB_URI)

def execute_query(query: str, params: dict = None) -> pd.DataFrame:
    """Execute a read-only query and return a DataFrame."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn, params=params)
            return df
    except Exception as e:
        # Instead of crashing, just return an empty dataframe.
        return pd.DataFrame()
