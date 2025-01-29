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

### Tech Stack

- **Apache Airflow (2.7.3)**: Workflow orchestration
- **PostgreSQL (13)**: Data warehouse
- **dbt (1.7.3)**: Data transformation
- **Docker**: Containerization and orchestration
- **Python (3.9)**: Programming language
- **Alpha Vantage API**: Financial data source
- **Streamlit**: Data visualization (coming soon)

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
docker-compose up -d
```

5. Access the services:
- Airflow UI: http://localhost:8080 (username: admin, password: admin)
- PostgreSQL: localhost:5432

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
├── tests/               # Python tests
└── docs/                # Documentation
```

## Data Models

Our dbt models follow a layered architecture:
- **Staging (stg_)**: Clean, typed data from raw sources
- **Intermediate (int_)**: Business logic transformations
- **Marts**: Final presentation layer for analytics

## Testing

The project includes:
- 49 dbt tests covering data quality and business logic
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

- [ ] Add Streamlit dashboard for data visualization
- [ ] Implement real-time data processing
- [ ] Add more technical indicators
- [ ] Enhance monitoring and alerting
- [ ] Add support for more data sources