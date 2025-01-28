from datetime import datetime, timedelta
import sys
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Add src to Python path
sys.path.append('/opt/airflow/src')
from extractors.alpha_vantage import AlphaVantageClient

def extract_market_data():
    """Extract daily stock data for specified symbols"""
    client = AlphaVantageClient()
    symbols = ['AAPL', 'GOOGL', 'MSFT']  # Example symbols
    
    for symbol in symbols:
        try:
            client.get_daily_prices(symbol)
            print(f"Successfully extracted data for {symbol}")
        except Exception as e:
            print(f"Error extracting data for {symbol}: {e}")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'market_data_pipeline',
    default_args=default_args,
    description='A pipeline to extract and transform market data',
    schedule_interval=timedelta(days=1),
)

extract_task = PythonOperator(
    task_id='extract_market_data',
    python_callable=extract_market_data,
    dag=dag,
)

# dbt debug task to verify configuration
dbt_debug = BashOperator(
    task_id='dbt_debug',
    bash_command='cd /dbt && dbt debug --profiles-dir /dbt --project-dir /dbt',
    dag=dag,
)

# dbt run task with full configuration
dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='cd /dbt && dbt run --profiles-dir /dbt --project-dir /dbt',
    dag=dag,
)

# dbt test task to ensure data quality
dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='cd /dbt && dbt test --profiles-dir /dbt --project-dir /dbt',
    dag=dag,
)

# Define the task dependencies
extract_task >> dbt_debug >> dbt_run >> dbt_test 