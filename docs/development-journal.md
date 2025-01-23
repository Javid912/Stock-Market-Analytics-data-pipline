## Day 7: Environment Troubleshooting and Dashboard Development

### Environment and Dependencies Resolution
- **Issue**: Encountered segmentation faults when running the Streamlit dashboard due to Python version and package compatibility issues
- **Resolution**:
  - Migrated from Python 3.8 to Python 3.9
  - Implemented specific version constraints for key dependencies:
    - streamlit==1.24.1
    - pandas==1.5.3
    - plotly==5.18.0
    - psycopg2-binary==2.9.9
  - Successfully resolved segmentation faults and got the dashboard running

### Current Challenges
- **Database Connectivity**: Dashboard is unable to connect to PostgreSQL database
  - Error: "could not translate host name 'postgres' to address"
  - Root cause: Docker container networking issue - dashboard running on host machine cannot resolve Docker container hostname
  - Next steps: Update database connection configuration to use localhost or Docker network bridge

### Technical Learnings
1. **Python Environment Management**:
   - Importance of maintaining consistent Python versions across development
   - Critical role of package version compatibility in preventing runtime issues
   - Value of explicit version pinning for core dependencies

2. **Docker Networking**:
   - Need to consider network connectivity between host machine and containerized services
   - Importance of proper host resolution when accessing containerized databases

### Next Steps
1. Resolve database connectivity by updating connection configuration
2. Implement proper error handling in dashboard for database connection issues
3. Add connection retry logic with appropriate timeout settings

## Day 8: DAG Implementation and Import Error Resolution

### Airflow DAG Implementation and Debugging
- **Initial Challenge**: Import error in Airflow DAG
  - Error: `ModuleNotFoundError: No module named 'src'`
  - Root cause: Python path configuration in Docker container
  - Resolution: Added src directory to Python path in DAG file and updated Airflow Dockerfile

### Current DAG Architecture
1. **Data Extraction (Task 1)**:
   - Fetches daily stock data for key tech companies (AAPL, GOOGL, MSFT)
   - Implements rate limiting for API calls
   - Stores raw JSON responses in PostgreSQL

2. **Data Transformation (Task 2)**:
   - Executes dbt models for data transformation
   - Creates staging views for cleaned data
   - Builds dimensional model for company analytics

### Technical Learnings
1. **Airflow Configuration**:
   - Importance of proper Python path setup in containerized environments
   - Best practices for organizing custom modules in Airflow
   - Effective use of Airflow's BashOperator for dbt integration

2. **Data Pipeline Architecture**:
   - Separation of concerns between extraction and transformation
   - Benefits of using dbt for transformation layer
   - Importance of proper error handling in API calls

### Next Steps
1. **Pipeline Enhancement**:
   - Add more stock symbols for broader market coverage
   - Implement intraday data collection
   - Add error notifications via email/Slack
   
2. **Data Quality**:
   - Implement data freshness checks
   - Add data quality tests in dbt
   - Monitor API rate limits and failures

3. **Dashboard Improvements**:
   - Add technical indicators (Moving averages, RSI)
   - Implement real-time price updates
   - Add portfolio tracking functionality 