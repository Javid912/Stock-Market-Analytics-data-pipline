-- Create airflow user with superuser privileges
CREATE USER airflow WITH PASSWORD 'airflow' SUPERUSER;

-- Create airflow database
CREATE DATABASE airflow WITH OWNER airflow; 