"""Custom operator for analytics phase."""

import sys
from pathlib import Path

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class AnalyticsOperator(BaseOperator):
    """Executes the analytics pipeline module."""

    @apply_defaults
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, context):
        self.log.info(f"Starting AnalyticsOperator execution")
        try:
            if "analytics" == "data_generator":
                import data_generator

                data_generator.main()
            elif "analytics" == "extract":
                import extract.manager

                extract.manager.main()
            elif "analytics" == "validate":
                import validate.manager

                validate.manager.main()
            elif "analytics" == "transform":
                import transform.manager

                transform.manager.main()
            elif "analytics" == "warehouse":
                import warehouse.warehouse_manager

                warehouse.warehouse_manager.main()
            elif "analytics" == "analytics":
                import analytics.analytics_manager

                analytics.analytics_manager.main()

            self.log.info(f"Successfully completed AnalyticsOperator")
        except Exception as e:
            self.log.error(f"AnalyticsOperator failed: {e}")
            raise
