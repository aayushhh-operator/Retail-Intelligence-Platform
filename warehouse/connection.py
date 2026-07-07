"""Database connection management."""

import logging

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from warehouse.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
from warehouse.exceptions import DatabaseConnectionError

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages the SQLAlchemy engine and connections."""

    def __init__(self) -> None:
        self.engine: Engine | None = None
        self.SessionLocal: sessionmaker | None = None

    def connect(self) -> None:
        """Establish the SQLAlchemy engine using the .env configuration."""
        try:
            db_url = (
                f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            )
            self.engine = create_engine(db_url, echo=False, pool_pre_ping=True)
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )
            # Test connection
            with self.engine.connect() as conn:
                logger.info(
                    f"Successfully connected to database '{DB_NAME}' at {DB_HOST}:{DB_PORT}."
                )
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise DatabaseConnectionError(
                f"Failed to connect to {DB_NAME} at {DB_HOST}:{DB_PORT}"
            ) from e

    def get_session(self) -> Session:
        """Get a new SQLAlchemy session."""
        if not self.SessionLocal:
            raise DatabaseConnectionError(
                "Engine not initialized. Call connect() first."
            )
        return self.SessionLocal()

    def dispose(self) -> None:
        """Dispose of the engine connection pool."""
        if self.engine:
            self.engine.dispose()
