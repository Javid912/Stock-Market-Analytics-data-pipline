# DataPipe Analytics Development Journal

## Project Overview
Building a production-grade ETL pipeline for processing financial market data using Apache Airflow, dbt, and PostgreSQL.

## Development Log

### Day 1: Project Setup and Initial Structure

#### 1. Project Structure Setup
Created the initial project structure with all necessary directories:
```
datapipe_analytics/
├── .github/workflows/      # CI/CD workflows
├── airflow/                # Airflow DAGs and plugins
├── dbt/                    # dbt transformations
├── src/                    # Source code
├── tests/                  # Test files
└── docker/                 # Dockerfile definitions
```

#### 2. Docker Environment Setup
- Created `docker-compose.yml` with multiple services:
  * PostgreSQL for data warehouse
  * Airflow (split into init, webserver, and scheduler)
  * dbt for transformations
  * Test service for running tests
- Key Learning: Splitting Airflow into multiple services (init, webserver, scheduler) improves maintainability and follows best practices

#### 3. Configuration Management
- Created `.env.example` for environment variables
- Implemented configuration for:
  * Database credentials
  * Airflow settings
  * Alpha Vantage API key
  * dbt settings
- Key Learning: Using environment variables for configuration allows for easy deployment across different environments

### Day 2: Data Extraction Layer

#### 1. Alpha Vantage Client Implementation
- Created robust API client with:
  * Rate limiting (5 requests/minute)
  * Error handling with custom exceptions
  * Input validation
  * Comprehensive logging
  * Multiple endpoints support (daily prices, intraday, company overview)
- Key Learning: Implementing rate limiting is crucial for API clients to avoid hitting limits

#### 2. Testing Setup
- Implemented comprehensive test suite:
  * Unit tests for validation
  * Integration tests for API calls
  * Fixture usage for test client
  * Environment variable handling in tests
- Key Learning: Using pytest fixtures makes tests more maintainable and reduces code duplication

#### 3. Python Package Structure
- Created proper Python package structure:
  * Added `__init__.py` files
  * Set up `PYTHONPATH` in both local and Docker environments
  * Created `pytest.ini` for test configuration
- Key Learning: Proper package structure is essential for imports to work in both local and Docker environments

### Day 3: Data Loading Layer and Testing

#### 1. Database Schema Design
- Created raw and staging schemas
- Implemented JSONB storage for API data
- Added indexes and triggers
- Key Learning: Using JSONB type in PostgreSQL allows flexible schema evolution while maintaining query performance

#### 2. Database Loader Implementation
- Created DatabaseLoader class with context manager pattern
- Implemented connection pooling
- Added error handling and logging
- Key Learning: Context managers ensure proper resource cleanup in Python

#### 3. Testing Challenges and Solutions
- Initial Issue: Fixture usage errors in pytest
- Problem: Direct fixture calls instead of dependency injection
- Solution: Properly chained fixtures and used pytest's dependency injection
- Key Learning: Fixtures should be used as parameters, not called directly

#### 4. Test Mocking Improvements
- Initial Issue: Type assertion failures with psycopg2.Json
- Problem: Testing for dict instead of Json type
- Solution: Updated assertions to handle psycopg2's Json type
- Key Learning: Mock objects need to match the actual types used in the code

## Technical Deep Dives

### 1. Docker and Images
- Docker builds create layers in images
- Each build command creates a new layer
- Images are immutable, containers are mutable instances
- Best Practice: Use multi-stage builds to keep final images small

### 2. Testing Components

#### Fixtures in pytest
- Purpose: Provide reusable test setup
- Features:
  * Dependency injection
  * Setup and teardown handling
  * Resource sharing between tests
- Example:
```python
@pytest.fixture
def mock_connection(mock_cursor):  # Dependencies can be other fixtures
    conn = MagicMock()
    conn.cursor.return_value = mock_cursor
    return conn
```

#### Mocking Database Connections
- Purpose: Test database code without actual database
- Components:
  * Mock connection objects
  * Mock cursors
  * Mock query results
- Example:
```python
with patch('psycopg2.connect') as mock_connect:
    mock_connect.return_value = mock_connection
```

#### Context Managers
- Purpose: Resource management (setup/teardown)
- Use Cases:
  * Database connections
  * File handling
  * Lock management
- Testing:
  * Verify proper entry/exit
  * Check resource cleanup
  * Test error handling

### 3. Database Components

#### psycopg2
- Python PostgreSQL adapter
- Features:
  * Native Python types to PostgreSQL conversion
  * Connection pooling
  * Transaction management
  * JSON handling

#### Staging Models
- Purpose: Clean and standardize raw data
- Components:
  * Views or tables
  * Data type conversions
  * Basic validations
- Example:
```sql
WITH source AS (
    SELECT * FROM raw.daily_prices
),
parsed AS (
    SELECT
        symbol,
        (raw_data->>'price')::numeric as price
    FROM source
)
```

### 4. dbt Components

#### Current Setup
1. Models:
   - staging/stg_daily_prices.sql: Transforms raw daily prices
   - More models needed for intraday and company data

2. Schema:
   - sources.yml: Defines raw data sources
   - schema.yml: Defines model structure and tests

#### Planned Extensions
1. Additional Models:
   - staging/stg_intraday_prices
   - staging/stg_company_overview
   - marts/dim_company
   - marts/fact_daily_trading

2. Tests:
   - Data quality checks
   - Business logic validation
   - Relationship checks

## Common Issues and Solutions

### 1. Fixture Usage Errors
**Problem**: `Fixture "mock_connection" called directly`
**Solution**: 
- Use fixtures as parameters
- Chain fixture dependencies
- Don't call fixtures directly

### 2. Type Assertions in Tests
**Problem**: Json type mismatch
**Solution**:
```python
assert isinstance(call_args[1][1], Json)
assert call_args[1][1].adapted == data
```

## Next Steps

1. Data Transformation:
- Create remaining staging models
- Implement marts layer
- Add data quality tests

2. Pipeline Orchestration:
- Fix Airflow module imports
- Create comprehensive DAG
- Add proper scheduling

3. Monitoring:
- Add logging
- Implement error tracking
- Create dashboards

### Best Practices Learned

1. Docker:
- Use multi-stage builds when possible
- Keep images minimal
- Use proper health checks
- Implement proper networking

2. Python:
- Use virtual environments
- Implement proper package structure
- Add comprehensive logging
- Use type hints

3. Testing:
- Use fixtures for common setup
- Separate unit and integration tests
- Mock external services when appropriate
- Test both success and error cases 