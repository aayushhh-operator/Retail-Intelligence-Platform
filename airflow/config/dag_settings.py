"""DAG default arguments and settings."""

from datetime import timedelta
import pendulum

DEFAULT_ARGS = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    'start_date': pendulum.today('UTC').add(days=-1),
    'catchup': False
}

SCHEDULE_INTERVAL = '@daily'
