import os
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import psycopg2
from psycopg2.extras import Json
import requests
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlphaVantageError(Exception):
    """Base exception for Alpha Vantage API errors"""
    pass

class RateLimitError(AlphaVantageError):
    """Raised when API rate limit is exceeded"""
    pass

class TokenBucket:
    """Token bucket algorithm for rate limiting"""
    def __init__(self, tokens: int, fill_rate: float):
        self.capacity = tokens
        self.tokens = tokens
        self.fill_rate = fill_rate
        self.last_update = time.time()

    def consume(self, tokens: int = 1) -> bool:
        now = time.time()
        # Add tokens based on time passed
        time_passed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + time_passed * self.fill_rate)
        self.last_update = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

class AlphaVantageClient:
    def __init__(self, development_mode: bool = False):
        """
        Initialize the Alpha Vantage client.
        
        Args:
            development_mode: If True, uses sample data instead of making API calls
        """
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not self.api_key and not development_mode:
            raise ValueError("ALPHA_VANTAGE_API_KEY environment variable is not set")
        
        self.base_url = "https://www.alphavantage.co/query"
        self.development_mode = development_mode
        
        # Token bucket for rate limiting (5 requests per minute = 1 request per 12 seconds)
        self.rate_limiter = TokenBucket(tokens=5, fill_rate=1/12.0)
        
        # Database connection parameters
        self.db_params = {
            'dbname': os.getenv('POSTGRES_DB', 'postgres'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432')
        }

    def _get_db_connection(self):
        """Get a database connection"""
        return psycopg2.connect(**self.db_params)

    def _store_api_response(self, endpoint: str, params: Dict[str, Any], response_data: Dict[str, Any]):
        """Store API response in database"""
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO raw.api_responses 
                        (endpoint, request_params, response_data, created_at)
                        VALUES (%s, %s, %s, %s)
                    """, (endpoint, Json(params), Json(response_data), datetime.now()))
        except Exception as e:
            logger.error(f"Failed to store API response: {str(e)}")
            # Don't raise the error - we don't want to fail the API call if storage fails

    def _get_sample_data(self, endpoint: str) -> Dict[str, Any]:
        """Get sample data for development mode"""
        sample_data_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 'tests', 'data', 
            f'sample_{endpoint}.json'
        )
        try:
            with open(sample_data_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Sample data file not found: {sample_data_path}")
            return {"Note": "Sample data not available"}

    def _wait_for_rate_limit(self):
        """Implement rate limiting using token bucket"""
        while not self.rate_limiter.consume():
            time.sleep(0.1)  # Sleep briefly before trying again

    def _make_request(self, endpoint: str, params: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """Make an API request with retries"""
        if self.development_mode:
            sample_data = self._get_sample_data(endpoint)
            self._store_api_response(endpoint, params, sample_data)
            return sample_data

        for attempt in range(max_retries):
            try:
                self._wait_for_rate_limit()
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                self._validate_response(data)
                
                # Store successful response
                self._store_api_response(endpoint, params, data)
                return data
                
            except RateLimitError:
                logger.warning(f"Rate limit hit, attempt {attempt + 1}/{max_retries}")
                time.sleep(60)  # Wait for rate limit reset
            except requests.RequestException as e:
                logger.error(f"Request failed, attempt {attempt + 1}/{max_retries}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise

    def _validate_response(self, response: Dict[str, Any]) -> None:
        """Validate API response"""
        if "Error Message" in response:
            raise AlphaVantageError(f"API Error: {response['Error Message']}")
        if "Note" in response and "API call frequency" in response["Note"]:
            raise RateLimitError("API rate limit exceeded")

    def get_daily_prices(self, symbol: str, output_size: str = 'compact') -> Dict[str, Any]:
        """
        Fetch daily prices for a given stock symbol.
        
        Args:
            symbol: The stock symbol (e.g., 'AAPL' for Apple)
            output_size: 'compact' (latest 100 data points) or 'full' (all data points)
            
        Returns:
            Dict containing the daily price data
        """
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("Symbol must be a non-empty string")
        if output_size not in ['compact', 'full']:
            raise ValueError("output_size must be either 'compact' or 'full'")

        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol.upper().strip(),
            "apikey": self.api_key,
            "outputsize": output_size
        }
        
        logger.info(f"Fetching daily prices for {symbol}")
        return self._make_request("daily_prices", params)

    def get_intraday_prices(self, symbol: str, interval: str = '5min') -> Dict[str, Any]:
        """
        Fetch intraday prices for a given stock symbol.
        
        Args:
            symbol: The stock symbol (e.g., 'AAPL' for Apple)
            interval: Time interval between data points ('1min', '5min', '15min', '30min', '60min')
            
        Returns:
            Dict containing the intraday price data
        """
        valid_intervals = ['1min', '5min', '15min', '30min', '60min']
        if interval not in valid_intervals:
            raise ValueError(f"Interval must be one of {valid_intervals}")

        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol.upper().strip(),
                "interval": interval,
                "apikey": self.api_key,
                "outputsize": 'compact'
            }
            
            logger.info(f"Fetching intraday prices for {symbol} at {interval} intervals")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            self._validate_response(data)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {str(e)}")
            raise

    def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch company overview data for a given stock symbol.
        
        Args:
            symbol: The stock symbol (e.g., 'AAPL' for Apple)
            
        Returns:
            Dict containing company overview data
        """
        params = {
            "function": "OVERVIEW",
            "symbol": symbol.upper().strip(),
            "apikey": self.api_key
        }
        
        logger.info(f"Fetching company overview for {symbol}")
        return self._make_request("company_overview", params) 