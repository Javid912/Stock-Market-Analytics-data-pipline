from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'market_data_pipeline',
    default_args=default_args,
    description='A pipeline to process financial market data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['market_data'],
)

extract_market_data = PythonOperator(
    task_id='extract_market_data',
    python_callable=lambda: print("Extracting market data..."),
    dag=dag,
)

transform_load_data = BashOperator(
    task_id='transform_load_data',
    bash_command='dbt run --profiles-dir /dbt',
    dag=dag,
)

extract_market_data >> transform_load_data 