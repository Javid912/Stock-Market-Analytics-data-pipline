FROM python:3.9-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        libpq-dev \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create dbt directory
WORKDIR /dbt

# Copy requirements file
COPY requirements.txt /dbt/requirements.txt

# Install Python packages
RUN pip install --no-cache-dir -r /dbt/requirements.txt

# Set environment variables
ENV DBT_PROFILES_DIR=/dbt
ENV PYTHONPATH=/dbt:${PYTHONPATH}

# Create non-root user
RUN useradd -m -s /bin/bash dbt_user \
    && chown -R dbt_user:dbt_user /dbt

USER dbt_user

# Default command
CMD ["dbt", "--version"]