FROM apache/airflow:2.7.3-python3.9

USER root

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy requirements file
COPY requirements.txt /opt/airflow/requirements.txt

# Install Python packages
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Set the PYTHONPATH
ENV PYTHONPATH=/opt/airflow/src:${PYTHONPATH}

# Initialize airflow DB and create admin user
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://postgres:postgres@postgres:5432/postgres

# Create directory for source code
RUN mkdir -p /opt/airflow/src && chown -R airflow:root /opt/airflow/src

# Install Airflow with DBT support and other dependencies
RUN pip install --no-cache-dir \
    "apache-airflow[dbt]==2.8.1" \
    "apache-airflow-providers-postgres==5.7.1" \
    "apache-airflow-providers-docker==3.8.0" \
    "apache-airflow-providers-ssh==3.10.0" \
    "apache-airflow-providers-dbt-cloud==3.10.1" \
    "psycopg2-binary==2.9.9" \
    "python-dotenv==1.0.0" \
    "requests==2.31.0" \
    "pandas==1.5.3" \
    "dbt-core==1.7.3" \
    "dbt-postgres==1.7.3"

# Copy source code
COPY --chown=airflow:root src/ /opt/airflow/src/

WORKDIR /opt/airflow