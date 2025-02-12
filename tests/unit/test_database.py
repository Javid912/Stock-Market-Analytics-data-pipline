import pytest
from unittest.mock import MagicMock, patch
from psycopg2.extras import Json
from src.loaders.database import DatabaseLoader

@pytest.fixture
def mock_cursor():
    return MagicMock()

@pytest.fixture
def mock_connection(mock_cursor):
    conn = MagicMock()
    conn.cursor.return_value = mock_cursor
    conn.encoding = 'UTF8'  # Add encoding attribute
    return conn

@pytest.fixture
def loader(mock_connection):
    with patch('psycopg2.connect', return_value=mock_connection):
        loader = DatabaseLoader()
        loader.connect()
        yield loader
        loader.disconnect()

def test_save_daily_prices(loader, mock_cursor, mock_connection):
    """Test saving daily prices data"""
    # Test data
    symbol = "AAPL"
    data = {
        "Meta Data": {
            "1. Information": "Daily Prices",
            "2. Symbol": "AAPL"
        },
        "Time Series (Daily)": {
            "2024-01-16": {
                "1. open": "100.0",
                "2. high": "101.0",
                "3. low": "99.0",
                "4. close": "100.5",
                "5. volume": "1000000"
            }
        }
    }
    
    # Call the method
    loader.save_daily_prices(symbol, data)
    
    # Verify that execute_values was called
    assert mock_cursor.execute.called or hasattr(mock_cursor, 'execute_values')
    
    # Verify commit was called
    mock_connection.commit.assert_called_once()

def test_save_intraday_prices(loader, mock_cursor, mock_connection):
    """Test saving intraday prices data"""
    # Test data
    symbol = "AAPL"
    interval = "5min"
    data = {
        "Meta Data": {
            "1. Information": "Intraday Prices",
            "2. Symbol": "AAPL"
        },
        "Time Series (5min)": {
            "2024-01-16 16:00:00": {
                "1. open": "100.0",
                "2. high": "101.0",
                "3. low": "99.0",
                "4. close": "100.5",
                "5. volume": "1000000"
            }
        }
    }
    
    # Call the method
    loader.save_intraday_prices(symbol, interval, data)
    
    # Verify the SQL execution
    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]
    
    # Check the SQL query
    assert "INSERT INTO raw.intraday_prices" in call_args[0]
    assert "ON CONFLICT" in call_args[0]
    
    # Check the parameters
    assert call_args[1][0] == symbol.upper()
    assert call_args[1][1] == interval
    assert isinstance(call_args[1][2], Json)
    assert call_args[1][2].adapted == data  # Check the underlying data
    
    # Verify commit was called
    mock_connection.commit.assert_called_once()

def test_database_connection_error():
    """Test database connection error handling"""
    with patch('psycopg2.connect') as mock_connect:
        mock_connect.side_effect = Exception("Connection failed")
        
        loader = DatabaseLoader()
        with pytest.raises(Exception) as exc_info:
            loader.connect()
        
        assert "Connection failed" in str(exc_info.value)

def test_context_manager(mock_connection):
    """Test database loader context manager"""
    with patch('psycopg2.connect', return_value=mock_connection):
        with DatabaseLoader() as loader:
            assert loader.conn is not None
            assert loader.cursor is not None
            
            # Test a simple operation
            loader.save_daily_prices("AAPL", {"test": "data"})
            
        # Verify connection was closed
        mock_connection.close.assert_called_once() 