"""Main entry point for Phase 6 Analytics Layer."""

import logging
from datetime import datetime
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.pipeline_run import get_pipeline_run_id, set_pipeline_run_id
from config.logging_config import configure_logging
from analytics.utils import AnalyticsDBManager
from analytics.star_schema import StarSchemaBuilder
from analytics.config import TARGET_SCHEMA

def main() -> None:
    """Run the analytics star schema pipeline."""
    pipeline_run_id = set_pipeline_run_id()
    logger = configure_logging(pipeline_run_id=pipeline_run_id)
    start_time = datetime.now()
    
    logger.info("Starting Phase 6 Analytics Pipeline...")

    db = AnalyticsDBManager()
    
    try:
        # 1. Initialize schema and tables
        builder = StarSchemaBuilder(db)
        builder.initialize_schema()
        
        # Record pipeline start
        db.execute_query(f"""
            INSERT INTO {TARGET_SCHEMA}.pipeline_runs (run_id, status, execution_start)
            VALUES ('{pipeline_run_id}', 'RUNNING', '{start_time}')
            ON CONFLICT (run_id) DO NOTHING;
        """)
        
        # 2. Clear out old data (TRUNCATE + RELOAD)
        builder.truncate_and_reload()
        
        # 3. Build Dimensions and Facts
        builder.build(pipeline_run_id)
        
        end_time = datetime.now()
        
        # Record success
        db.execute_query(f"""
            UPDATE {TARGET_SCHEMA}.pipeline_runs
            SET status = 'SUCCESS', execution_end = '{end_time}'
            WHERE run_id = '{pipeline_run_id}';
        """)
        
        logger.info(f"Analytics Pipeline completed successfully in {end_time - start_time}.")
        
    except Exception as e:
        logger.critical(f"Analytics Pipeline failed: {e}")
        end_time = datetime.now()
        
        # Attempt to record failure
        try:
            db.execute_query(f"""
                UPDATE {TARGET_SCHEMA}.pipeline_runs
                SET status = 'FAILED', execution_end = '{end_time}'
                WHERE run_id = '{pipeline_run_id}';
            """)
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
