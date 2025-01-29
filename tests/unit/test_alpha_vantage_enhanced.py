import os
import pytest
import time
import requests
from unittest.mock import MagicMock, patch
from datetime import datetime
from psycopg2.extras import Json

from src.extractors.alpha_vantage import (
    AlphaVantageClient,
    AlphaVantageError,
    RateLimitError,
    TokenBucket
)

@pytest.fixture(autouse=True)
def setup_environment():
    """Setup environment variables for all tests"""
    old_env = os.environ.copy()
    os.environ['ALPHA_VANTAGE_API_KEY'] = 'test_key'
    yield
    os.environ.clear()
    os.environ.update(old_env)

# Token Bucket Tests
def test_token_bucket_initialization():
    """Test token bucket initialization"""
    bucket = TokenBucket(tokens=5, fill_rate=1/12.0)
    assert bucket.tokens == 5
    assert bucket.capacity == 5
    assert bucket.fill_rate == 1/12.0

def test_token_bucket_consume():
    """Test token bucket consumption"""
    bucket = TokenBucket(tokens=2, fill_rate=1.0)  # 1 token per second
    
    # Should be able to consume first token
    assert bucket.consume() is True
    # Should be able to consume second token
    assert bucket.consume() is True
    # Should not be able to consume third token immediately
    assert bucket.consume() is False
    
    # Wait for token regeneration
    time.sleep(1.1)  # Wait just over 1 second
    # Should be able to consume one token again
    assert bucket.consume() is True

# Development Mode Tests
@pytest.fixture
def dev_client():
    """Create a client in development mode"""
    return AlphaVantageClient(development_mode=True)

def test_development_mode_initialization():
    """Test client initialization in development mode"""
    # Should not raise error even without API key
    if 'ALPHA_VANTAGE_API_KEY' in os.environ:
        del os.environ['ALPHA_VANTAGE_API_KEY']
    
    client = AlphaVantageClient(development_mode=True)
    assert client.development_mode is True
    assert client.api_key is None

def test_development_mode_sample_data(dev_client):
    """Test that development mode returns sample data"""
    data = dev_client.get_daily_prices('AAPL')
    
    assert 'Meta Data' in data
    assert data['Meta Data']['2. Symbol'] == 'AAPL'
    assert 'Time Series (Daily)' in data

# Database Integration Tests
@pytest.fixture
def mock_db_connection():
    """Create a mock database connection"""
    with patch('psycopg2.connect') as mock_connect:
        conn = MagicMock()
        cursor = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cursor
        mock_connect.return_value.__enter__.return_value = conn
        yield cursor

def test_store_api_response(dev_client, mock_db_connection):
    """Test storing API response in database"""
    dev_client.get_daily_prices('AAPL')
    
    # Verify that insert was called
    mock_db_connection.execute.assert_called_once()
    call_args = mock_db_connection.execute.call_args[0]
    
    # Verify SQL contains INSERT
    assert 'INSERT INTO raw.api_responses' in call_args[0]
    
    # Verify parameters
    assert call_args[1][0] == 'daily_prices'  # endpoint
    assert isinstance(call_args[1][1], Json)   # request_params
    assert isinstance(call_args[1][2], Json)   # response_data
    assert isinstance(call_args[1][3], datetime)  # created_at

# Error Handling Tests
@patch('requests.get')
def test_rate_limit_retry(mock_get):
    """Test rate limit retry behavior"""
    # Create client in production mode to test actual API calls
    client = AlphaVantageClient()
    client.api_key = 'test_key'  # Set dummy API key
    
    # Setup mock to fail with rate limit twice, then succeed
    mock_get.side_effect = [
        MagicMock(
            raise_for_status=MagicMock(),
            json=MagicMock(return_value={"Note": "API call frequency"})
        ),
        MagicMock(
            raise_for_status=MagicMock(),
            json=MagicMock(return_value={"Note": "API call frequency"})
        ),
        MagicMock(
            raise_for_status=MagicMock(),
            json=MagicMock(return_value={"success": True})
        )
    ]
    
    # Should eventually succeed
    with patch.object(client, '_store_api_response'):  # Don't actually store in DB
        result = client.get_daily_prices('AAPL')
    
    assert result == {"success": True}
    assert mock_get.call_count == 3

@patch('requests.get')
def test_exponential_backoff(mock_get):
    """Test exponential backoff for connection errors"""
    # Create client in production mode to test actual API calls
    client = AlphaVantageClient()
    client.api_key = 'test_key'  # Set dummy API key
    
    # Setup mock to fail with connection error twice, then succeed
    mock_get.side_effect = [
        requests.RequestException("Connection error"),
        requests.RequestException("Connection error"),
        MagicMock(
            raise_for_status=MagicMock(),
            json=MagicMock(return_value={"success": True})
        )
    ]
    
    start_time = time.time()
    with patch.object(client, '_store_api_response'):  # Don't actually store in DB
        result = client.get_daily_prices('AAPL')
    elapsed_time = time.time() - start_time
    
    assert result == {"success": True}
    assert mock_get.call_count == 3
    # Should have waited at least 3 seconds (1 + 2 seconds for exponential backoff)
    assert elapsed_time >= 3

# Integration Test with Real API (Optional)
@pytest.mark.integration
def test_real_api_call():
    """Test real API call (requires API key)"""
    if 'ALPHA_VANTAGE_API_KEY' not in os.environ:
        pytest.skip("No API key available")
    
    client = AlphaVantageClient()
    data = client.get_daily_prices('AAPL')
    
    assert 'Meta Data' in data
    assert 'Time Series (Daily)' in data
    assert data['Meta Data']['2. Symbol'] == 'AAPL' 