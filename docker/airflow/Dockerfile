FROM apache/airflow:2.7.1-python3.9

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    dbt-core==1.7.3 \
    dbt-postgres==1.7.3 \
    apache-airflow[dbt]==2.7.3 \
    psycopg2-binary==2.9.9

USER airflow

WORKDIR /opt/airflow