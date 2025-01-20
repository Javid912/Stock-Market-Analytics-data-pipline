from datetime import datetime, timedelta
import sys
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Add src to Python path
sys.path.append(str(Path(__file__).parents[2]))
from src.extractors.alpha_vantage import AlphaVantageClient

def extract_stock_data():
    """Extract daily stock data for specified symbols"""
    client = AlphaVantageClient()
    symbols = ['AAPL', 'GOOGL', 'MSFT']  # Example symbols
    
    for symbol in symbols:
        try:
            data = client.get_daily_prices(symbol)
            print(f"Successfully extracted data for {symbol}")
            # TODO: Save data to database or file
        except Exception as e:
            print(f"Error extracting data for {symbol}: {e}")

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
    python_callable=extract_stock_data,
    dag=dag,
)

transform_load_data = BashOperator(
    task_id='transform_load_data',
    bash_command='dbt run --profiles-dir /dbt',
    dag=dag,
)

extract_market_data >> transform_load_data 