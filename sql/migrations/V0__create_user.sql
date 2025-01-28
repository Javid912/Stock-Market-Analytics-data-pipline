-- Create postgres superuser if it doesn't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE rolname = 'postgres'
   ) THEN
      CREATE ROLE postgres WITH LOGIN PASSWORD 'postgres' SUPERUSER CREATEDB CREATEROLE REPLICATION BYPASSRLS;
   ELSE
      ALTER ROLE postgres WITH LOGIN PASSWORD 'postgres' SUPERUSER CREATEDB CREATEROLE REPLICATION BYPASSRLS;
   END IF;
END
$do$;

-- Create airflow user with all necessary privileges
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE rolname = 'airflow'
   ) THEN
      CREATE ROLE airflow WITH LOGIN PASSWORD 'postgres' SUPERUSER CREATEDB CREATEROLE REPLICATION BYPASSRLS;
   ELSE
      ALTER ROLE airflow WITH LOGIN PASSWORD 'postgres' SUPERUSER CREATEDB CREATEROLE REPLICATION BYPASSRLS;
   END IF;
END
$do$;

-- Grant privileges on postgres database
GRANT ALL PRIVILEGES ON DATABASE postgres TO airflow;
GRANT ALL PRIVILEGES ON DATABASE postgres TO postgres;

-- Create airflow database if it doesn't exist
CREATE DATABASE airflow WITH OWNER airflow;

\connect airflow;

-- Create schemas if they don't exist
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- Grant privileges on airflow database
GRANT ALL PRIVILEGES ON DATABASE airflow TO postgres;
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA raw TO airflow;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA staging TO airflow;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA marts TO airflow; 