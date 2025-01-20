import os
import pytest
from src.extractors.alpha_vantage import (
    AlphaVantageClient,
    AlphaVantageError,
    RateLimitError
)

@pytest.fixture
def client():
    """Create a test client"""
    return AlphaVantageClient()

def test_alpha_vantage_client_initialization():
    """Test that client initializes with API key"""
    # Test missing API key
    if 'ALPHA_VANTAGE_API_KEY' in os.environ:
        temp = os.environ['ALPHA_VANTAGE_API_KEY']
        del os.environ['ALPHA_VANTAGE_API_KEY']
    
    with pytest.raises(ValueError):
        AlphaVantageClient()
    
    # Test with API key
    os.environ['ALPHA_VANTAGE_API_KEY'] = 'test_key'
    client = AlphaVantageClient()
    assert client.api_key == 'test_key'
    
    # Restore original API key if it existed
    if 'temp' in locals():
        os.environ['ALPHA_VANTAGE_API_KEY'] = temp

def test_get_daily_prices_validation(client):
    """Test input validation for get_daily_prices"""
    # Test invalid symbol
    with pytest.raises(ValueError):
        client.get_daily_prices("")
    
    # Test invalid output_size
    with pytest.raises(ValueError):
        client.get_daily_prices("AAPL", output_size="invalid")

def test_get_daily_prices_integration(client):
    """Test actual API call for daily prices"""
    data = client.get_daily_prices('AAPL')
    
    # Check response structure
    assert 'Meta Data' in data
    assert 'Time Series (Daily)' in data
    
    # Check meta data
    meta_data = data['Meta Data']
    assert '1. Information' in meta_data
    assert '2. Symbol' in meta_data
    assert meta_data['2. Symbol'] == 'AAPL'
    
    # Check time series data
    time_series = data['Time Series (Daily)']
    assert len(time_series) > 0
    
    # Check first data point structure
    first_date = list(time_series.keys())[0]
    first_data = time_series[first_date]
    assert '1. open' in first_data
    assert '2. high' in first_data
    assert '3. low' in first_data
    assert '4. close' in first_data
    assert '5. volume' in first_data

def test_get_intraday_prices_validation(client):
    """Test input validation for get_intraday_prices"""
    # Test invalid interval
    with pytest.raises(ValueError):
        client.get_intraday_prices("AAPL", interval="invalid")

def test_get_intraday_prices_integration(client):
    """Test actual API call for intraday prices"""
    data = client.get_intraday_prices('AAPL')
    
    # Check response structure
    assert 'Meta Data' in data
    assert 'Time Series (5min)' in data
    
    # Check meta data
    meta_data = data['Meta Data']
    assert '1. Information' in meta_data
    assert '2. Symbol' in meta_data
    assert meta_data['2. Symbol'] == 'AAPL'

def test_get_company_overview_integration(client):
    """Test actual API call for company overview"""
    data = client.get_company_overview('AAPL')
    
    # Check essential company information
    assert 'Symbol' in data
    assert 'Name' in data
    assert 'Description' in data
    assert 'Exchange' in data
    assert 'Sector' in data 