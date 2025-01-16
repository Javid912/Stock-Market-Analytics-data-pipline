FROM apache/airflow:2.7.1

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy requirements and install Python dependencies
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

# Copy the rest of the application
COPY . /opt/airflow/

WORKDIR /opt/airflow 