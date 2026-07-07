"""Custom Postgres Hook Wrapper for Metadata Logging."""

import logging
import sys
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from airflow.plugins_manager import AirflowPlugin
from psycopg2 import pool

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from airflow.config.airflow_config import (DATABASE_HOST, DATABASE_NAME,
                                           DATABASE_PASSWORD, DATABASE_PORT,
                                           DATABASE_USER)

logger = logging.getLogger(__name__)


class MetadataPostgresHook:
    """
    A custom Postgres Hook dedicated to safe, retryable execution of metadata logging queries.
    Avoids using Airflow's built-in PostgresHook to prevent cyclic dependencies or issues
    if the Airflow metastore is running on a different instance than our Retail DB.
    """

    _connection_pool = None

    @classmethod
    def get_pool(cls):
        if cls._connection_pool is None:
            try:
                cls._connection_pool = psycopg2.pool.ThreadedConnectionPool(
                    1,
                    10,
                    host=DATABASE_HOST,
                    port=DATABASE_PORT,
                    dbname=DATABASE_NAME,
                    user=DATABASE_USER,
                    password=DATABASE_PASSWORD,
                )
            except Exception as e:
                logger.error(f"Failed to initialize metadata connection pool: {e}")
                raise
        return cls._connection_pool

    @classmethod
    @contextmanager
    def get_connection(cls):
        pool = cls.get_pool()
        conn = pool.getconn()
        conn.autocommit = True
        try:
            yield conn
        finally:
            pool.putconn(conn)

    @classmethod
    def initialize_metadata_tables(cls):
        """Create airflow logging tables in PostgreSQL if they don't exist."""
        sql = """
            CREATE SCHEMA IF NOT EXISTS airflow;
            CREATE TABLE IF NOT EXISTS airflow.dag_runs_log (
                run_id VARCHAR(100) PRIMARY KEY,
                dag_id VARCHAR(100),
                execution_date TIMESTAMP,
                status VARCHAR(50),
                duration FLOAT,
                error_message TEXT
            );
            CREATE TABLE IF NOT EXISTS airflow.task_runs_log (
                id SERIAL PRIMARY KEY,
                run_id VARCHAR(100),
                dag_id VARCHAR(100),
                task_id VARCHAR(100),
                execution_date TIMESTAMP,
                status VARCHAR(50),
                duration FLOAT,
                error_message TEXT
            );
        """
        cls.execute(sql)

    @classmethod
    def execute(cls, query: str, parameters: tuple = None):
        """Execute a query safely with a connection from the pool."""
        retries = 3
        for attempt in range(retries):
            try:
                with cls.get_connection() as conn:
                    with conn.cursor() as cur:
                        if parameters:
                            cur.execute(query, parameters)
                        else:
                            cur.execute(query)
                return
            except psycopg2.OperationalError as e:
                logger.warning(f"Connection issue, retrying {attempt+1}/{retries}: {e}")
                if attempt == retries - 1:
                    logger.error("Max retries reached for DB execute.")
                    raise
            except Exception as e:
                logger.error(f"Error executing metadata query: {e}")
                raise


class MetadataHookPlugin(AirflowPlugin):
    name = "metadata_postgres_hook_plugin"
