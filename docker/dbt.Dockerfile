FROM python:3.9-slim

WORKDIR /dbt

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    ssh-client \
    software-properties-common \
    make \
    build-essential \
    ca-certificates \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dbt and dependencies
RUN pip install --no-cache-dir \
    dbt-core==1.6.1 \
    dbt-postgres==1.6.1 \
    psycopg2-binary==2.9.9

# Copy dbt project
COPY dbt/ /dbt/

# Default entrypoint
ENTRYPOINT ["dbt"]