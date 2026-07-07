"""Pipeline execution history recorder to database."""

import logging
from datetime import datetime

from sqlalchemy import text

from warehouse.database import DatabaseManager

logger = logging.getLogger(__name__)


class LoadHistoryRecorder:
    """Records pipeline runs and load history to metadata schema."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def record_pipeline_run(
        self, run_id: str, status: str, start_time: datetime, end_time: datetime
    ) -> None:
        """Record a pipeline execution in metadata.pipeline_runs."""
        query = """
            INSERT INTO metadata.pipeline_runs (pipeline_run_id, status, execution_start, execution_end)
            VALUES (:run_id, :status, :start_time, :end_time)
            ON CONFLICT (pipeline_run_id) DO UPDATE SET 
                status = EXCLUDED.status,
                execution_end = EXCLUDED.execution_end;
        """
        try:
            with self.db.connection.engine.connect() as conn:
                with conn.begin():
                    conn.execute(
                        text(query),
                        {
                            "run_id": run_id,
                            "status": status,
                            "start_time": start_time,
                            "end_time": end_time,
                        },
                    )
        except Exception as e:
            logger.error(f"Failed to record pipeline run {run_id}: {e}")

    def record_load(
        self,
        run_id: str,
        dataset: str,
        rows_read: int,
        rows_loaded: int,
        rows_failed: int,
        strategy: str,
        status: str,
    ) -> None:
        """Record individual dataset load history in metadata.load_history."""
        query = """
            INSERT INTO metadata.load_history (pipeline_run_id, dataset, rows_read, rows_loaded, rows_failed, load_strategy, status)
            VALUES (:run_id, :dataset, :rows_read, :rows_loaded, :rows_failed, :strategy, :status);
        """
        try:
            with self.db.connection.engine.connect() as conn:
                with conn.begin():
                    conn.execute(
                        text(query),
                        {
                            "run_id": run_id,
                            "dataset": dataset,
                            "rows_read": rows_read,
                            "rows_loaded": rows_loaded,
                            "rows_failed": rows_failed,
                            "strategy": strategy,
                            "status": status,
                        },
                    )
        except Exception as e:
            logger.error(f"Failed to record load history for {dataset}: {e}")
