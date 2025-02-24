import os
import logging
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseLoader:
    """Handle database operations for market data loading"""
    
    def __init__(self):
        """Initialize database connection"""
        self.conn_params = {
            'dbname': os.getenv('POSTGRES_DB', 'postgres'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'host': os.getenv('POSTGRES_HOST', 'postgres'),
            'port': os.getenv('POSTGRES_PORT', '5432')
        }
        self.conn = None
        self.cursor = None
        logger.info(f"Initializing DatabaseLoader with connection params: host={self.conn_params['host']}, db={self.conn_params['dbname']}")

    def connect(self) -> None:
        """Establish database connection"""
        try:
            logger.info("Attempting to connect to database...")
            self.conn = psycopg2.connect(**self.conn_params)
            self.cursor = self.conn.cursor()
            # Test the connection
            self.cursor.execute("SELECT 1")
            self.cursor.fetchone()
            logger.info("Successfully connected to the database")
        except Exception as e:
            logger.error(f"Error connecting to the database: {str(e)}")
            if self.conn:
                self.conn.close()
            raise

    def disconnect(self) -> None:
        """Close database connection"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {str(e)}")
            raise

    def save_daily_prices(self, symbol: str, data: Dict[str, Any]) -> None:
        """
        Save daily prices data to raw.daily_prices table
        
        Args:
            symbol: Stock symbol
            data: API response data
        """
        try:
            # Extract time series data
            time_series = data.get('Time Series (Daily)', {})
            if not time_series:
                logger.warning(f"No time series data found for {symbol}")
                return

            # Log the data we're about to insert
            logger.info(f"Preparing to insert {len(time_series)} records for {symbol}")

            # Prepare data for bulk insert
            values = []
            for date, prices in time_series.items():
                try:
                    values.append((
                        symbol.upper(),
                        date,
                        float(prices.get('1. open', 0)),
                        float(prices.get('2. high', 0)),
                        float(prices.get('3. low', 0)),
                        float(prices.get('4. close', 0)),
                        int(float(prices.get('5. volume', 0)))
                    ))
                except (ValueError, TypeError) as e:
                    logger.error(f"Error parsing price data for {symbol} on {date}: {str(e)}")
                    continue

            if not values:
                logger.warning(f"No valid price data to insert for {symbol}")
                return

            # Bulk insert/update
            query = """
                INSERT INTO public_raw.raw_stock_prices 
                (symbol, date, open, high, low, close, volume)
                VALUES %s
                ON CONFLICT (symbol, date) 
                DO UPDATE SET 
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume;
            """
            
            # Use execute_values for efficient bulk insert
            from psycopg2.extras import execute_values
            execute_values(self.cursor, query, values)
            
            self.conn.commit()
            logger.info(f"Successfully saved {len(values)} days of price data for {symbol}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error saving daily prices for {symbol}: {str(e)}")
            raise

    def save_intraday_prices(self, symbol: str, interval: str, data: Dict[str, Any]) -> None:
        """
        Save intraday prices data to raw.intraday_prices table
        
        Args:
            symbol: Stock symbol
            interval: Time interval
            data: API response data
        """
        try:
            query = """
                INSERT INTO raw.intraday_prices (symbol, interval, raw_data)
                VALUES (%s, %s, %s)
                ON CONFLICT (symbol, interval, extracted_at)
                DO UPDATE SET raw_data = EXCLUDED.raw_data;
            """
            self.cursor.execute(query, (symbol.upper(), interval, Json(data)))
            self.conn.commit()
            logger.info(f"Successfully saved intraday prices for {symbol}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error saving intraday prices for {symbol}: {str(e)}")
            raise

    def save_company_overview(self, symbol: str, data: Dict[str, Any]) -> None:
        """
        Save company overview data to raw.company_overview table
        
        Args:
            symbol: Stock symbol
            data: API response data
        """
        try:
            query = """
                INSERT INTO raw.company_overview (symbol, raw_data)
                VALUES (%s, %s)
                ON CONFLICT (symbol, extracted_at)
                DO UPDATE SET raw_data = EXCLUDED.raw_data;
            """
            self.cursor.execute(query, (symbol.upper(), Json(data)))
            self.conn.commit()
            logger.info(f"Successfully saved company overview for {symbol}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error saving company overview for {symbol}: {str(e)}")
            raise

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect() 