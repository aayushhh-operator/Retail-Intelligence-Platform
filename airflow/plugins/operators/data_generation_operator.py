"""Custom operator for data_generator phase."""

import sys
from pathlib import Path

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class DataGenerationOperator(BaseOperator):
    """Executes the data_generator pipeline module."""

    @apply_defaults
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, context):
        self.log.info(f"Starting DataGenerationOperator execution")
        try:
            if "data_generator" == "data_generator":
                import data_generator

                data_generator.main()
            elif "data_generator" == "extract":
                import extract.manager

                extract.manager.main()
            elif "data_generator" == "validate":
                import validate.manager

                validate.manager.main()
            elif "data_generator" == "transform":
                import transform.manager

                transform.manager.main()
            elif "data_generator" == "warehouse":
                import warehouse.warehouse_manager

                warehouse.warehouse_manager.main()
            elif "data_generator" == "analytics":
                import analytics.analytics_manager

                analytics.analytics_manager.main()

            self.log.info(f"Successfully completed DataGenerationOperator")
        except Exception as e:
            self.log.error(f"DataGenerationOperator failed: {e}")
            raise
