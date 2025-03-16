# Optimized Airflow Dockerfile
FROM apache/airflow:2.7.1-python3.9-slim

USER root

# Install only essential system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create directory for source code with proper permissions
RUN mkdir -p /opt/airflow/src && chown -R airflow:root /opt/airflow/src

USER airflow

# Install only required Airflow providers and dependencies
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir \
    apache-airflow-providers-postgres==5.7.1 \
    psycopg2-binary==2.9.9 \
    python-dotenv==1.0.0 \
    requests==2.31.0 \
    pandas==1.5.3

# Copy source code
COPY --chown=airflow:root src/ /opt/airflow/src/

# Set working directory
WORKDIR /opt/airflow

# Set environment variables for better performance
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False \
    AIRFLOW__SCHEDULER__MIN_FILE_PROCESS_INTERVAL=60 \
    AIRFLOW__WEBSERVER__WORKERS=1 \
    AIRFLOW__CORE__PARALLELISM=4 \
    AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG=1 