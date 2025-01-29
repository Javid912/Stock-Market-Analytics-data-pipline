from datetime import datetime, timedelta
import sys
from pathlib import Path
import logging
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.hooks.base import BaseHook
from airflow.models import Variable
from airflow.exceptions import AirflowException

# Configure logging
logger = logging.getLogger(__name__)

# Add src to Python path
sys.path.append('/opt/airflow/src')
from extractors.alpha_vantage import AlphaVantageClient

def extract_market_data(**context):
    """
    Extract daily stock data for specified symbols with enhanced error handling and logging
    """
    try:
        # Initialize client with proper error handling
        client = AlphaVantageClient()
        
        # Get symbols from Airflow variables (can be configured in UI)
        symbols = Variable.get("stock_symbols", deserialize_json=True,
                             default_var=['AAPL', 'GOOGL', 'MSFT'])
        
        successful_extracts = 0
        failed_extracts = 0
        
        for symbol in symbols:
            try:
                # Extract both daily prices and company info
                daily_data = client.get_daily_prices(symbol)
                company_data = client.get_company_overview(symbol)
                
                logger.info(f"Successfully extracted data for {symbol}")
                successful_extracts += 1
                
                # Push metrics to XCom for monitoring
                context['task_instance'].xcom_push(
                    key=f'daily_data_{symbol}',
                    value={'status': 'success', 'timestamp': datetime.now().isoformat()}
                )
                
            except Exception as e:
                logger.error(f"Error extracting data for {symbol}: {str(e)}")
                failed_extracts += 1
                
                # Push error to XCom
                context['task_instance'].xcom_push(
                    key=f'error_{symbol}',
                    value={'error': str(e), 'timestamp': datetime.now().isoformat()}
                )
        
        # Raise exception if all extracts failed
        if failed_extracts == len(symbols):
            raise AirflowException(f"All {len(symbols)} symbol extractions failed")
        
        # Log summary
        logger.info(f"Extraction complete. Successful: {successful_extracts}, Failed: {failed_extracts}")
        
    except Exception as e:
        logger.error(f"Critical error in extract_market_data: {str(e)}")
        raise AirflowException(f"Critical error in data extraction: {str(e)}")

def verify_data_quality(**context):
    """
    Verify the quality of extracted data before transformation
    """
    try:
        # Get extraction results from XCom
        task_instance = context['task_instance']
        symbols = Variable.get("stock_symbols", deserialize_json=True,
                             default_var=['AAPL', 'GOOGL', 'MSFT'])
        
        for symbol in symbols:
            daily_data = task_instance.xcom_pull(key=f'daily_data_{symbol}')
            if not daily_data or daily_data.get('status') != 'success':
                logger.error(f"Data quality check failed for {symbol}")
                raise AirflowException(f"Data quality check failed for {symbol}")
        
        logger.info("All data quality checks passed")
        
    except Exception as e:
        logger.error(f"Data quality verification failed: {str(e)}")
        raise AirflowException(f"Data quality verification failed: {str(e)}")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30)
}

dag = DAG(
    'market_data_pipeline',
    default_args=default_args,
    description='A pipeline to extract and transform market data',
    schedule_interval='0 0 * * 1-5',  # Run at midnight on weekdays
    catchup=False,
    tags=['market_data', 'stocks'],
)

start = DummyOperator(
    task_id='start',
    dag=dag,
)

extract_task = PythonOperator(
    task_id='extract_market_data',
    python_callable=extract_market_data,
    provide_context=True,
    dag=dag,
)

verify_data = PythonOperator(
    task_id='verify_data_quality',
    python_callable=verify_data_quality,
    provide_context=True,
    dag=dag,
)

dbt_debug = BashOperator(
    task_id='dbt_debug',
    bash_command='cd /dbt && dbt debug --profiles-dir /dbt --project-dir /dbt',
    dag=dag,
)

dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='cd /dbt && dbt run --profiles-dir /dbt --project-dir /dbt',
    dag=dag,
)

dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='cd /dbt && dbt test --profiles-dir /dbt --project-dir /dbt',
    dag=dag,
)

end = DummyOperator(
    task_id='end',
    dag=dag,
)

# Define the task dependencies
start >> extract_task >> verify_data >> dbt_debug >> dbt_run >> dbt_test >> end 