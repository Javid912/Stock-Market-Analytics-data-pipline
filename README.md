# DataPipe Analytics

A production-grade ETL pipeline for processing financial market data using Apache Airflow, dbt, and PostgreSQL.

## Project Overview

This project implements a robust data engineering pipeline that processes financial market data from Alpha Vantage API. It showcases industry best practices in data engineering including data validation, testing, documentation, and monitoring.

### Features

- **Real-time Market Data**: Automated extraction of stock market data from Alpha Vantage
- **Data Quality**: Comprehensive data testing and validation using dbt
- **Scalable Architecture**: Containerized services with proper health checks and dependency management
- **Monitoring**: Built-in logging and health monitoring for all services
- **Documentation**: Extensive documentation of models, tests, and best practices
- **Analytics Dashboard**: Interactive Streamlit dashboard for market analysis and visualization
- **Resource Optimization**: Support for older hardware with minimal resource requirements

### Tech Stack

- **Apache Airflow (2.7.3)**: Workflow orchestration
- **PostgreSQL (13)**: Data warehouse
- **dbt (1.7.3)**: Data transformation
- **Docker**: Containerization and orchestration
- **Python (3.9)**: Programming language
- **Alpha Vantage API**: Financial data source
- **Streamlit**: Data visualization dashboard
- **Metabase**: Business intelligence platform

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Make (optional, for using Makefile commands)
- Alpha Vantage API key

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/javid912/datapipe-analytics.git
cd datapipe-analytics
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Copy the example environment file and configure your API key:
```bash
cp .env.example .env
# Edit .env and add your Alpha Vantage API key
```

4. Start the services:
```bash
# For standard hardware:
docker-compose up -d

# For older or resource-constrained hardware:
docker-compose -f docker-compose-minimal.yml up -d
```

5. Access the services:
- Streamlit Dashboard: http://localhost:8501
- Metabase: http://localhost:3000 (username: admin@admin.com, password: metabase123)
- Airflow UI: http://localhost:8080 (username: admin, password: admin)
- PostgreSQL: localhost:5432

## Performance Optimization

For older or resource-constrained hardware, we provide a minimal Docker Compose configuration:

```bash
docker-compose -f docker-compose-minimal.yml up -d
```

This configuration:
- Reduces memory usage for all containers
- Limits CPU usage
- Starts only essential services
- Optimizes database connections
- Implements selective computation of technical indicators

## Project Structure

```
datapipe-analytics/
├── airflow/               # Airflow DAGs and configurations
│   └── dags/             # DAG definitions
├── dbt/                  # Data transformation
│   ├── models/          # dbt models
│   └── tests/           # Data tests
├── docker/              # Dockerfile definitions
├── src/                 # Source code
│   └── dashboard/       # Streamlit dashboard
├── tests/               # Python tests
└── docs/                # Documentation
```

## Data Models

Our dbt models follow a layered architecture:
- **Raw (public_raw)**: Original data from external sources
- **Staging (public_staging)**: Clean, typed data from raw sources
- **Marts (public_marts)**: Business logic transformations for analytics

## Testing

The project includes:
- dbt tests covering data quality and business logic
- Python unit tests for data extraction
- Integration tests for the full pipeline
- Container health checks

## Monitoring

- Service health monitoring via Docker health checks
- Airflow task monitoring and alerting
- dbt test coverage and data quality metrics
- Logging for all components

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [x] Add Streamlit dashboard for data visualization
- [x] Implement resource optimization for older hardware
- [x] Add Metabase integration
- [ ] Implement real-time data processing
- [ ] Add more technical indicators
- [ ] Enhance monitoring and alerting
- [ ] Add support for more data sources

## Data Visualization

### Metabase Dashboard
The project now includes Metabase for data visualization and analytics. Access the dashboard at:
- URL: http://localhost:3000
- Default credentials:
  - Email: admin@admin.com
  - Password: metabase123

### Features
- Real-time market data visualization
- Company performance metrics
- Technical analysis indicators
- Custom SQL queries and charts

## Recent Updates
- Added Metabase for data visualization
- Implemented data retention policies
- Enhanced data quality tests
- Added comprehensive documentation