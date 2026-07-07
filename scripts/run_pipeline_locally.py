"""Local Pipeline Runner (Airflow Alternative).

This script allows you to run the entire pipeline end-to-end locally using standard Python
without needing to spin up the heavy Apache Airflow Docker containers.
"""

import logging
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("local_orchestrator")


def run_phase(name: str, module_main):
    """Run a specific phase of the pipeline with error handling and timing."""
    logger.info(f"{'='*50}")
    logger.info(f"STARTING PHASE: {name}")
    logger.info(f"{'='*50}")
    start_time = time.time()

    try:
        module_main()
        duration = time.time() - start_time
        logger.info(f"SUCCESS: {name} completed in {duration:.2f} seconds.\n")
    except Exception as e:
        logger.error(f"FAILED: {name} failed with error: {e}")
        logger.error("Halting pipeline execution.")
        sys.exit(1)


def main():
    logger.info("Initializing Local Retail Intelligence Pipeline...")

    # Import phases
    import analytics.analytics_manager
    import data_generator.generate_all
    import extract.ingestion_manager
    import transform.transformation_manager
    import validate.validation_manager
    import warehouse.warehouse_manager

    # Execute sequentially
    # Optional: Toggle data generation (can be slow if you already generated data)
    run_phase("Phase 1: Synthetic Data Generation", data_generator.generate_all.main)
    run_phase("Phase 2: Extraction", extract.ingestion_manager.main)
    run_phase("Phase 3: Validation", validate.validation_manager.main)
    run_phase("Phase 4: Transformation", transform.transformation_manager.main)
    run_phase("Phase 5: Warehouse Load", warehouse.warehouse_manager.main)
    run_phase("Phase 6: Analytics Star Schema Build", analytics.analytics_manager.main)

    logger.info("🎉 All phases completed successfully! Data is now in PostgreSQL.")
    logger.info(
        "You can now start the Streamlit dashboard: streamlit run dashboard/app.py"
    )


if __name__ == "__main__":
    main()
