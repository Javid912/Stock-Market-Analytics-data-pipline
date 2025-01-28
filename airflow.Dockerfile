FROM apache/airflow:2.7.1-python3.9

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/airflow/src && chown -R airflow:root /opt/airflow/src

USER airflow

# Install Airflow with DBT support and other dependencies
RUN pip install --no-cache-dir \
    "apache-airflow[dbt]==2.7.1" \
    "apache-airflow-providers-postgres==5.7.1" \
    "apache-airflow-providers-docker==3.8.0" \
    "apache-airflow-providers-ssh==3.10.0" \
    "psycopg2-binary==2.9.9" \
    "python-dotenv==1.0.0" \
    "requests==2.31.0" \
    "pandas==1.5.3" \
    "dbt-core==1.7.3" \
    "dbt-postgres==1.7.3"

COPY --chown=airflow:root ./src /opt/airflow/src 