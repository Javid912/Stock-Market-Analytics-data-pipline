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
            'dbname': os.getenv('POSTGRES_DB', 'airflow'),
            'user': os.getenv('POSTGRES_USER', 'airflow'),
            'password': os.getenv('POSTGRES_PASSWORD', 'airflow'),
            'host': os.getenv('POSTGRES_HOST', 'postgres'),
            'port': os.getenv('POSTGRES_PORT', '5432')
        }
        self.conn = None
        self.cursor = None

    def connect(self) -> None:
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            self.cursor = self.conn.cursor()
            logger.info("Successfully connected to the database")
        except Exception as e:
            logger.error(f"Error connecting to the database: {str(e)}")
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
            query = """
                INSERT INTO raw.daily_prices (symbol, raw_data)
                VALUES (%s, %s)
                ON CONFLICT (symbol, extracted_at)
                DO UPDATE SET raw_data = EXCLUDED.raw_data;
            """
            self.cursor.execute(query, (symbol.upper(), Json(data)))
            self.conn.commit()
            logger.info(f"Successfully saved daily prices for {symbol}")
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