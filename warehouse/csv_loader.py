"""CSV loading logic into the database."""

import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from warehouse.exceptions import LoadError
import logging

logger = logging.getLogger(__name__)

class CSVLoader:
    """Loads CSV files into PostgreSQL in chunks."""
    
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size

    def load(self, filepath: Path, table: str, schema: str, session: Session) -> int:
        """Load a CSV file into the database using pandas in chunks."""
        if not filepath.is_file():
            raise FileNotFoundError(f"File not found: {filepath}")

        rows_loaded = 0
        try:
            logger.info(f"Loading {filepath.name} into {schema}.{table}...")
            # We use the session's underlying engine for pandas to_sql,
            # but we explicitly pass the session's connection to participate in the transaction.
            engine_connection = session.connection()
            
            for chunk in pd.read_csv(filepath, chunksize=self.chunk_size):
                # Cast to object and replace NaN with None so SQLAlchemy handles NULLs correctly
                # (Otherwise pandas float64 NaNs cause invalid input syntax for postgres timestamp)
                import numpy as np
                chunk = chunk.astype(object).replace({np.nan: None})
                
                chunk.to_sql(
                    name=table,
                    con=engine_connection,
                    schema=schema,
                    if_exists="append",
                    index=False,
                    method="multi"
                )
                rows_loaded += len(chunk)
                logger.debug(f"Loaded chunk of {len(chunk)} rows into {table}.")
                
            logger.info(f"Successfully loaded {rows_loaded} total rows into {schema}.{table}.")
            return rows_loaded
        except Exception as e:
            import traceback
            logger.error(f"Error loading {filepath.name} into {schema}.{table}: {e}")
            logger.error(traceback.format_exc())
            raise LoadError(f"Failed to load {filepath.name}") from e
