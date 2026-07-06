"""Transaction management for loading data."""

import logging
from contextlib import contextmanager
from sqlalchemy.orm import Session
from warehouse.connection import DatabaseConnection

logger = logging.getLogger(__name__)

class TransactionManager:
    """Provides a context manager for transactional safety."""
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection

    @contextmanager
    def transaction(self) -> Session:
        """Context manager yielding a SQLAlchemy session wrapped in a transaction."""
        session = self.connection.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            logger.error(f"Transaction failed, rolling back. Error: {e}")
            session.rollback()
            raise
        finally:
            session.close()
