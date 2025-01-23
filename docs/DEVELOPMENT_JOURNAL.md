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

### Day 4: Data Transformation Layer

#### 1. Staging Models Implementation
- Created three staging models:
  * `stg_daily_prices`: Transform raw daily price data
  * `stg_intraday_prices`: Transform intraday trading data
  * `stg_company_overview`: Transform company information
- Key Learning: Using PostgreSQL JSONB operators for efficient data extraction

#### 2. Mart Layer Design
- Created dimension table:
  * `dim_company`: Combines company info with trading stats
- Implemented smart aggregations:
  * Latest company information using window functions
  * 30-day trading statistics
- Key Learning: Using window functions for temporal data management

#### 3. Data Quality Framework
- Implemented comprehensive testing:
  * Not null constraints
  * Uniqueness checks
  * Value validation (e.g., valid intervals)
  * Cross-model relationships
- Key Learning: Balance between data quality and transformation flexibility

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

### 1. dbt Model Architecture

#### Staging Layer
- Purpose: Clean and standardize raw data
- Features:
  * JSON parsing
  * Data type casting
  * Basic validation
- Example:
```sql
SELECT
    symbol,
    (raw_data->>'price')::NUMERIC as price,
    timestamp::TIMESTAMP as trading_time
FROM raw_data
```

#### Mart Layer
- Purpose: Business-level transformations
- Features:
  * Dimensional modeling
  * Aggregations
  * Business rules
- Example:
```sql
WITH latest_data AS (
    SELECT *,
    ROW_NUMBER() OVER (
        PARTITION BY symbol 
        ORDER BY extracted_at DESC
    ) as rn
    FROM stg_company_overview
)
```

### 2. Data Testing Strategy

#### Test Types
1. Schema Tests:
   - Not null validation
   - Unique constraints
   - Accepted values
   - Relationships

2. Data Quality Tests:
   - Value ranges
   - Data freshness
   - Completeness

3. Business Logic Tests:
   - Aggregation accuracy
   - Temporal consistency
   - Cross-model relationships

### 3. SQL Patterns and Best Practices

#### Common Table Expressions (CTEs)
- Purpose: Break down complex logic
- Benefits:
  * Improved readability
  * Easier maintenance
  * Better performance
- Example:
```sql
WITH source AS (
    SELECT * FROM raw
),
transformed AS (
    SELECT * FROM source
)
SELECT * FROM transformed
```

#### Window Functions
- Purpose: Temporal and partitioned analysis
- Use Cases:
  * Latest records
  * Running totals
  * Moving averages
- Example:
```sql
ROW_NUMBER() OVER (
    PARTITION BY symbol 
    ORDER BY extracted_at DESC
)
```

## Lessons Learned

### 1. Data Modeling
- Start with staging models for clean data
- Use dimensional modeling for analytics
- Implement incremental processing where possible

### 2. Testing
- Test at both staging and mart levels
- Validate business logic explicitly
- Use dbt's built-in test framework

### 3. Performance
- Use appropriate indexes
- Optimize JSON queries
- Consider materialization strategies

## Next Steps

1. Fact Tables:
- Create `fact_daily_trading`
- Create `fact_intraday_trading`
- Implement trading metrics

2. Custom Tests:
- Add data freshness tests
- Implement value range validations
- Create cross-model relationship tests

3. Documentation:
- Add column-level documentation
- Create data lineage diagrams
- Document business rules

## Questions to Consider
1. How to handle late-arriving data?
2. What incremental processing strategy to use?
3. How to optimize for query performance?

## Best Practices Established
1. Always use CTEs for complex transformations
2. Document assumptions in models
3. Test both technical and business requirements
4. Use consistent naming conventions
5. Implement proper error handling

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

## Best Practices Learned

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