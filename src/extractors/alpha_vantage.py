import os
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
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

class AlphaVantageClient:
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not self.api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY environment variable is not set")
        self.base_url = "https://www.alphavantage.co/query"
        self.last_request_time = 0
        self.min_request_interval = 12.1  # Alpha Vantage free tier: 5 requests per minute

    def _wait_for_rate_limit(self):
        """Implement rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

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
            
        Raises:
            AlphaVantageError: If the API returns an error
            RateLimitError: If rate limit is exceeded
            requests.RequestException: If the HTTP request fails
        """
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("Symbol must be a non-empty string")
        if output_size not in ['compact', 'full']:
            raise ValueError("output_size must be either 'compact' or 'full'")

        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol.upper().strip(),
                "apikey": self.api_key,
                "outputsize": output_size
            }
            
            logger.info(f"Fetching daily prices for {symbol}")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            self._validate_response(data)
            return data
            
        except requests.RequestException as e:
            logger.error(f"HTTP Request failed for {symbol}: {str(e)}")
            raise
        except (AlphaVantageError, RateLimitError) as e:
            logger.error(f"Alpha Vantage API error for {symbol}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching data for {symbol}: {str(e)}")
            raise

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
        self._wait_for_rate_limit()
        
        try:
            params = {
                "function": "OVERVIEW",
                "symbol": symbol.upper().strip(),
                "apikey": self.api_key
            }
            
            logger.info(f"Fetching company overview for {symbol}")
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            self._validate_response(data)
            return data
            
        except Exception as e:
            logger.error(f"Error fetching company overview for {symbol}: {str(e)}")
            raise 