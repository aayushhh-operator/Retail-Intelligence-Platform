"""Database utilities for the analytics layer."""

import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from analytics.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
import logging

logger = logging.getLogger(__name__)

class AnalyticsDBManager:
    """Manages connections and raw SQL execution for the analytics schema."""

    def __init__(self):
        self.dsn = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        self.engine = create_engine(self.dsn)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    @contextmanager
    def transaction(self) -> Session:
        """Provide a transactional scope around a series of operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Transaction failed and rolled back. Error: {e}")
            raise
        finally:
            session.close()

    def execute_sql_file(self, filepath: str) -> None:
        """Execute a raw SQL script from a file using standard psycopg2 for complex DDL."""
        # Using raw psycopg2 to ensure complex DDL (like DO blocks) executes smoothly
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        conn.autocommit = True
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                sql_script = file.read()
            with conn.cursor() as cur:
                cur.execute(sql_script)
            logger.info(f"Successfully executed SQL script: {filepath}")
        except Exception as e:
            logger.error(f"Error executing SQL file {filepath}: {e}")
            raise
        finally:
            conn.close()

    def execute_query(self, query: str) -> None:
        """Execute a single query in an auto-committed connection."""
        try:
            with self.engine.begin() as conn:
                conn.execute(text(query))
        except Exception as e:
            logger.error(f"Failed to execute query: {query[:50]}... Error: {e}")
            raise
