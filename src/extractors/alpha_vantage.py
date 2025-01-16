import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class AlphaVantageClient:
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not self.api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY environment variable is not set")
        self.base_url = "https://www.alphavantage.co/query"

    def get_daily_prices(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch daily prices for a given stock symbol.
        
        Args:
            symbol: The stock symbol (e.g., 'AAPL' for Apple)
            
        Returns:
            Dict containing the daily price data
        """
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key,
            "outputsize": "compact"
        }
        
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        
        return response.json() 