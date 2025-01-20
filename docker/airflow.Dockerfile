FROM apache/airflow:2.7.1-python3.9

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create directory for source code
RUN mkdir -p /opt/airflow/src && chown -R airflow:root /opt/airflow/src

USER airflow

# Install Airflow providers and other dependencies
RUN pip install --no-cache-dir \
    apache-airflow-providers-postgres==5.7.1 \
    psycopg2-binary==2.9.9 \
    python-dotenv==1.0.0 \
    requests==2.31.0 \
    pandas==1.5.3

# Copy source code
COPY --chown=airflow:root src/ /opt/airflow/src/

WORKDIR /opt/airflow