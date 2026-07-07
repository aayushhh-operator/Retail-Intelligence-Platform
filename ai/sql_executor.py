"""Safe SQL Executor."""
import pandas as pd
from sqlalchemy import create_engine, text
from ai.config import DB_URI
from ai.sql_validator import validate_sql

def execute_sql(sql: str) -> pd.DataFrame:
    safe_sql = validate_sql(sql)
    engine = create_engine(DB_URI)
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(safe_sql), conn)
    except Exception as e:
        raise Exception(f"Database execution failed: {e}")
