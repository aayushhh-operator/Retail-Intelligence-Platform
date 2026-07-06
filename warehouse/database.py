"""General database operations and utilities."""

from sqlalchemy import text
from warehouse.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles general DB tasks like executing raw SQL files."""
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection

    def execute_sql_file(self, filepath: str) -> None:
        """Execute a raw SQL script from a file."""
        if not self.connection.engine:
            raise RuntimeError("Database connection not initialized.")
            
        with open(filepath, "r", encoding="utf-8") as file:
            sql_script = file.read()
        
        try:
            with self.connection.engine.connect() as conn:
                with conn.begin():
                    # For simple scripts we can just execute the whole block
                    conn.execute(text(sql_script))
                logger.info(f"Successfully executed SQL script: {filepath}")
        except Exception as e:
            logger.error(f"Error executing {filepath}: {e}")
            raise

    def execute_query(self, query: str) -> None:
        """Execute a single raw SQL query."""
        if not self.connection.engine:
            raise RuntimeError("Database connection not initialized.")
            
        try:
            with self.connection.engine.connect() as conn:
                with conn.begin():
                    conn.execute(text(query))
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
