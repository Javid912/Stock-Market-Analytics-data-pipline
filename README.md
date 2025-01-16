# DataPipe Analytics

A production-grade ETL pipeline for processing financial market data using Apache Airflow, dbt, and PostgreSQL.

## Project Overview

This project demonstrates a modern data engineering pipeline that processes financial market data from Alpha Vantage API. It showcases best practices in data engineering including data validation, testing, documentation, and monitoring.

### Tech Stack

- **Apache Airflow**: Workflow orchestration
- **PostgreSQL**: Data warehouse
- **dbt**: Data transformation
- **Docker**: Containerization
- **Python**: Programming language
- **Alpha Vantage API**: Data source

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Make (optional, for using Makefile commands)

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

3. Copy the example environment file:
```bash
cp .env.example .env
```

4. Start the services:
```bash
docker-compose up -d
```

## Project Structure

- `airflow/`: Apache Airflow DAGs and custom operators
- `dbt/`: Data transformation models and tests
- `src/`: Source code for data extraction and loading
- `tests/`: Unit and integration tests
- `docker/`: Dockerfile and related configurations

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.