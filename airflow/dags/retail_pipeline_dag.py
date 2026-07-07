"""End-to-End Orchestration DAG for Retail Intelligence Platform."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

from airflow import DAG
from airflow.config.airflow_config import ENABLE_DATA_GENERATION
from airflow.config.dag_settings import DEFAULT_ARGS, SCHEDULE_INTERVAL
from airflow.plugins.operators.analytics_operator import AnalyticsOperator
from airflow.plugins.operators.data_generation_operator import \
    DataGenerationOperator
from airflow.plugins.operators.extraction_operator import ExtractionOperator
from airflow.plugins.operators.transformation_operator import \
    TransformationOperator
from airflow.plugins.operators.validation_operator import ValidationOperator
from airflow.plugins.operators.warehouse_operator import WarehouseOperator
from airflow.plugins.utils.airflow_logger import (log_dag_run_failure,
                                                  log_dag_run_start,
                                                  log_dag_run_success,
                                                  log_task_failure,
                                                  log_task_start,
                                                  log_task_success)

with DAG(
    dag_id="retail_intelligence_pipeline",
    default_args=DEFAULT_ARGS,
    schedule_interval=SCHEDULE_INTERVAL,
    catchup=False,
    max_active_runs=1,
    description="End-to-End Data Pipeline",
    on_success_callback=log_dag_run_success,
    on_failure_callback=log_dag_run_failure,
) as dag:

    start = EmptyOperator(task_id="start", on_execute_callback=log_dag_run_start)

    with TaskGroup(
        "data_generation", tooltip="Generate Synthetic Data"
    ) as data_generation_group:
        if ENABLE_DATA_GENERATION:
            generate_data = DataGenerationOperator(
                task_id="generate_synthetic_data",
                on_execute_callback=log_task_start,
                on_success_callback=log_task_success,
                on_failure_callback=log_task_failure,
            )
        else:
            generate_data = EmptyOperator(task_id="skip_generation")

    extract_data = ExtractionOperator(
        task_id="extract_data",
        on_execute_callback=log_task_start,
        on_success_callback=log_task_success,
        on_failure_callback=log_task_failure,
    )

    validate_data = ValidationOperator(
        task_id="validate_data",
        on_execute_callback=log_task_start,
        on_success_callback=log_task_success,
        on_failure_callback=log_task_failure,
    )

    transform_data = TransformationOperator(
        task_id="transform_data",
        on_execute_callback=log_task_start,
        on_success_callback=log_task_success,
        on_failure_callback=log_task_failure,
    )

    load_warehouse = WarehouseOperator(
        task_id="load_warehouse",
        on_execute_callback=log_task_start,
        on_success_callback=log_task_success,
        on_failure_callback=log_task_failure,
    )

    build_analytics = AnalyticsOperator(
        task_id="build_analytics",
        on_execute_callback=log_task_start,
        on_success_callback=log_task_success,
        on_failure_callback=log_task_failure,
    )

    end = EmptyOperator(task_id="end")

    # Dependencies
    (
        start
        >> data_generation_group
        >> extract_data
        >> validate_data
        >> transform_data
        >> load_warehouse
        >> build_analytics
        >> end
    )
