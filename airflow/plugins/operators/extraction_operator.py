"""Custom operator for extract phase."""

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

class ExtractionOperator(BaseOperator):
    """Executes the extract pipeline module."""

    @apply_defaults
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, context):
        self.log.info(f"Starting ExtractionOperator execution")
        try:
            if 'extract' == 'data_generator':
                import data_generator
                data_generator.main()
            elif 'extract' == 'extract':
                import extract.manager
                extract.manager.main()
            elif 'extract' == 'validate':
                import validate.manager
                validate.manager.main()
            elif 'extract' == 'transform':
                import transform.manager
                transform.manager.main()
            elif 'extract' == 'warehouse':
                import warehouse.warehouse_manager
                warehouse.warehouse_manager.main()
            elif 'extract' == 'analytics':
                import analytics.analytics_manager
                analytics.analytics_manager.main()
            
            self.log.info(f"Successfully completed ExtractionOperator")
        except Exception as e:
            self.log.error(f"ExtractionOperator failed: {e}")
            raise
