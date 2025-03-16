# Multi-stage build for dbt
# Stage 1: Build dependencies
FROM python:3.9-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY dbt/requirements.txt .

# Build wheels
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels \
    dbt-core==1.6.1 \
    dbt-postgres==1.6.1 \
    psycopg2-binary==2.9.9

# Stage 2: Runtime image
FROM python:3.9-slim

WORKDIR /dbt

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    ssh-client \
    libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder stage
COPY --from=builder /app/wheels /wheels

# Install packages from wheels
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Copy dbt project
COPY dbt/ /dbt/

# Default entrypoint
ENTRYPOINT ["dbt"] 