"""Dynamic PostgreSQL Schema Loader."""
import pandas as pd
from sqlalchemy import create_engine, text
from ai.config import DB_URI

def load_schema() -> str:
    """Fetch table and column definitions dynamically."""
    engine = create_engine(DB_URI)
    query = """
        SELECT table_schema, table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema IN ('warehouse', 'analytics', 'airflow')
        ORDER BY table_schema, table_name;
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
            schema_str = ""
            for (sch, tab), group in df.groupby(['table_schema', 'table_name']):
                schema_str += f"Table: {sch}.{tab}\nColumns:\n"
                for _, row in group.iterrows():
                    schema_str += f"  - {row['column_name']} ({row['data_type']})\n"
                schema_str += "\n"
            return schema_str
    except Exception as e:
        return f"Error loading schema: {e}"
