from datetime import datetime, timedelta
import sys
from pathlib import Path
import logging
import json
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.hooks.base import BaseHook
from airflow.models import Variable
from airflow.exceptions import AirflowException
from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook

# Configure logging
logger = logging.getLogger(__name__)

def send_slack_notification(context):
    """
    Send Slack notification about task failure
    """
    task_instance = context['task_instance']
    dag_id = context['dag'].dag_id
    task_id = task_instance.task_id
    execution_date = context['execution_date']
    error_message = context.get('exception', 'No error message available')
    
    # Get execution metrics if available
    execution_metrics = task_instance.xcom_pull(key='execution_metrics') or {}
    quality_metrics = task_instance.xcom_pull(key='quality_metrics') or {}
    
    # Create detailed message
    message = f"""
:red_circle: Task Failed!
*DAG*: {dag_id}
*Task*: {task_id}
*Execution Date*: {execution_date}
*Error*: {str(error_message)}

*Execution Metrics*:
- Success Rate: {execution_metrics.get('success_rate', 'N/A')}%
- Total Symbols: {execution_metrics.get('total_symbols', 'N/A')}
- Execution Time: {execution_metrics.get('execution_time_seconds', 'N/A')}s

*Quality Issues*:
- Missing Data: {len(quality_metrics.get('missing_data', []))} symbols
- Stale Data: {len(quality_metrics.get('stale_data', []))} symbols
- Anomalies: {len(quality_metrics.get('data_anomalies', []))} issues
    """
    
    # Send to Slack
    hook = SlackWebhookHook(
        slack_webhook_conn_id='slack_monitoring',
        message=message,
        channel='#market-data-alerts'
    )
    hook.execute()

# Add src to Python path
sys.path.append('/opt/airflow/src')
from extractors.alpha_vantage import AlphaVantageClient

# Add import for DatabaseLoader
from loaders.database import DatabaseLoader

# Default stock symbols if not configured in Airflow Variables
DEFAULT_SYMBOLS = [
    # Tech Companies
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META'
]

def extract_market_data(**context):
    """
    Extract daily stock data for specified symbols with enhanced error handling and logging
    """
    try:
        # Initialize client with proper error handling - use development mode for testing
        development_mode = Variable.get("development_mode", default_var="true").lower() == "true"
        client = AlphaVantageClient(development_mode=development_mode)
        
        # Get symbols from Airflow variables with expanded default list
        symbols = Variable.get("stock_symbols", deserialize_json=True,
                             default_var=DEFAULT_SYMBOLS)  # Use same symbols in both dev and prod mode
        
        successful_extracts = 0
        failed_extracts = 0
        
        # Track execution time for monitoring
        start_time = datetime.now()
        
        # Initialize database loader
        with DatabaseLoader() as loader:
            for symbol in symbols:
                try:
                    # Extract both daily prices and company info with full history
                    daily_data = client.get_daily_prices(symbol, output_size='full')
                    company_data = client.get_company_overview(symbol)
                    
                    # Store data in database
                    loader.save_daily_prices(symbol, daily_data)
                    loader.save_company_overview(symbol, company_data)
                    
                    logger.info(f"Successfully extracted data for {symbol}")
                    successful_extracts += 1
                    
                    # Enhanced metrics for monitoring
                    context['task_instance'].xcom_push(
                        key=f'daily_data_{symbol}',
                        value={
                            'status': 'success',
                            'timestamp': datetime.now().isoformat(),
                            'data_points': len(daily_data.get('Time Series (Daily)', {})),
                            'latest_date': max(daily_data.get('Time Series (Daily)', {}).keys(), default=None)
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Error extracting data for {symbol}: {str(e)}")
                    failed_extracts += 1
                    
                    # Enhanced error tracking
                    context['task_instance'].xcom_push(
                        key=f'error_{symbol}',
                        value={
                            'error': str(e),
                            'timestamp': datetime.now().isoformat(),
                            'attempt': context.get('task_instance').try_number
                        }
                    )
        
        # Calculate execution metrics
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Push execution metrics
        context['task_instance'].xcom_push(
            key='execution_metrics',
            value={
                'execution_time_seconds': execution_time,
                'successful_extracts': successful_extracts,
                'failed_extracts': failed_extracts,
                'total_symbols': len(symbols),
                'success_rate': (successful_extracts / len(symbols)) * 100
            }
        )
        
        # Raise exception if all extracts failed
        if failed_extracts == len(symbols):
            raise AirflowException(f"All {len(symbols)} symbol extractions failed")
        
        # Log summary with enhanced metrics
        logger.info(
            f"Extraction complete. Success: {successful_extracts}, Failed: {failed_extracts}, "
            f"Time: {execution_time:.2f}s, Success Rate: {(successful_extracts/len(symbols))*100:.1f}%"
        )
        
    except Exception as e:
        logger.error(f"Critical error in extract_market_data: {str(e)}")
        raise AirflowException(f"Critical error in data extraction: {str(e)}")

def verify_data_quality(**context):
    """
    Comprehensive data quality verification reading directly from database
    """
    try:
        symbols = Variable.get("stock_symbols", deserialize_json=True,
                             default_var=DEFAULT_SYMBOLS)
        
        quality_checks = {
            'missing_data': [],
            'stale_data': [],
            'data_anomalies': []
        }
        
        current_date = datetime.now().date()
        
        # Initialize database loader
        with DatabaseLoader() as loader:
            # Query to check latest data for each symbol
            with loader.conn.cursor() as cur:
                for symbol in symbols:
                    # Check if we have any data for this symbol
                    cur.execute("""
                        SELECT MAX(date) as latest_date, COUNT(*) as data_points
                        FROM public_raw.raw_stock_prices
                        WHERE symbol = %s
                    """, (symbol,))
                    result = cur.fetchone()
                    
                    if not result or not result[0]:  # No data found
                        quality_checks['missing_data'].append(symbol)
                        continue
                    
                    latest_date = result[0]
                    data_points = result[1]
                    
                    # Check data freshness
                    days_old = (current_date - latest_date).days
                    if days_old > 5:  # Data shouldn't be more than 5 days old
                        quality_checks['stale_data'].append({
                            'symbol': symbol,
                            'days_old': days_old,
                            'latest_date': latest_date.isoformat()
                        })
                    
                    # Check data points (should have at least 100 days of history)
                    if data_points < 100:
                        quality_checks['data_anomalies'].append({
                            'symbol': symbol,
                            'issue': 'insufficient_history',
                            'data_points': data_points
                        })
                    
                    # Additional quality checks
                    cur.execute("""
                        SELECT COUNT(*) 
                        FROM public_raw.raw_stock_prices
                        WHERE symbol = %s 
                        AND (
                            open IS NULL OR high IS NULL OR low IS NULL 
                            OR close IS NULL OR volume IS NULL
                            OR open = 0 OR high = 0 OR low = 0 
                            OR close = 0 OR volume = 0
                        )
                    """, (symbol,))
                    invalid_records = cur.fetchone()[0]
                    
                    if invalid_records > 0:
                        quality_checks['data_anomalies'].append({
                            'symbol': symbol,
                            'issue': 'invalid_values',
                            'count': invalid_records
                        })
        
        # Push quality metrics to XCom (much smaller payload now)
        context['task_instance'].xcom_push(
            key='quality_metrics',
            value=quality_checks
        )
        
        # Evaluate quality checks
        if quality_checks['missing_data']:
            logger.error(f"Missing data for symbols: {quality_checks['missing_data']}")
            raise AirflowException(f"Data quality check failed - missing data for {len(quality_checks['missing_data'])} symbols")
        
        if quality_checks['stale_data']:
            logger.warning(f"Stale data detected: {quality_checks['stale_data']}")
        
        if quality_checks['data_anomalies']:
            logger.warning(f"Data anomalies detected: {quality_checks['data_anomalies']}")
        
        logger.info("All critical data quality checks passed")
        
    except Exception as e:
        logger.error(f"Data quality verification failed: {str(e)}")
        raise AirflowException(f"Data quality verification failed: {str(e)}")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
    'execution_timeout': timedelta(minutes=60),
    'on_failure_callback': send_slack_notification,  # Add Slack notification on failure
    'sla': timedelta(hours=2)
}

dag = DAG(
    'market_data_pipeline',
    default_args=default_args,
    description='A pipeline to extract and transform market data',
    schedule_interval='30 18 * * 1-5',  # Run at 18:30 UTC (after US market close) on weekdays
    catchup=False,
    tags=['market_data', 'stocks', 'production'],
    max_active_runs=1,
    concurrency=3
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