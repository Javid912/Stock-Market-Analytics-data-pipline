#!/usr/bin/env python3
"""
Script to extract market data from Alpha Vantage API
"""
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('market_data_extraction')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from src.extractors.alpha_vantage import AlphaVantageClient
    from src.loaders.database import DatabaseLoader
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure you're running this script from the project root")
    sys.exit(1)

def extract_market_data(symbols, development_mode=False):
    """
    Extract market data for the specified symbols
    
    Args:
        symbols (list): List of stock symbols to extract data for
        development_mode (bool): Whether to use development mode (sample data)
    """
    logger.info(f"Starting market data extraction for {len(symbols)} symbols")
    logger.info(f"Development mode: {development_mode}")
    
    # Initialize client
    client = AlphaVantageClient(development_mode=development_mode)
    
    successful_extracts = 0
    failed_extracts = 0
    
    # Track execution time
    start_time = datetime.now()
    
    # Initialize database loader
    with DatabaseLoader() as loader:
        for symbol in symbols:
            try:
                logger.info(f"Extracting data for {symbol}...")
                
                # Extract daily prices
                logger.info(f"Getting daily prices for {symbol}")
                daily_data = client.get_daily_prices(symbol, output_size='compact')
                
                # Extract company info
                logger.info(f"Getting company overview for {symbol}")
                company_data = client.get_company_overview(symbol)
                
                # Store data in database
                logger.info(f"Saving daily prices for {symbol}")
                loader.save_daily_prices(symbol, daily_data)
                
                logger.info(f"Saving company overview for {symbol}")
                loader.save_company_overview(symbol, company_data)
                
                logger.info(f"Successfully extracted data for {symbol}")
                successful_extracts += 1
                
            except Exception as e:
                logger.error(f"Error extracting data for {symbol}: {str(e)}")
                failed_extracts += 1
    
    # Calculate execution time
    execution_time = (datetime.now() - start_time).total_seconds()
    
    # Log summary
    logger.info(f"Extraction complete: {successful_extracts} successful, {failed_extracts} failed")
    logger.info(f"Total execution time: {execution_time:.2f} seconds")
    
    return {
        "successful_extracts": successful_extracts,
        "failed_extracts": failed_extracts,
        "execution_time": execution_time
    }

if __name__ == "__main__":
    # Default symbols
    DEFAULT_SYMBOLS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META"  # Top 5 tech companies
    ]
    
    # Get symbols from command line arguments or use defaults
    symbols = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_SYMBOLS
    
    # Get development mode from environment variable
    development_mode = os.environ.get("DEVELOPMENT_MODE", "false").lower() == "true"
    
    # Run extraction
    extract_market_data(symbols, development_mode) 