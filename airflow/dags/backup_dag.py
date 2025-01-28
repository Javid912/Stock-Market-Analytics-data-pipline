from datetime import datetime, timedelta
import sys
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator

# Add src to Python path
sys.path.append('/opt/airflow/src')
from backup_db import create_backup

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'database_backup',
    default_args=default_args,
    description='Regular database backup',
    schedule_interval='0 0 * * *',  # Daily at midnight
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

backup_task = PythonOperator(
    task_id='create_backup',
    python_callable=create_backup,
    dag=dag,
)