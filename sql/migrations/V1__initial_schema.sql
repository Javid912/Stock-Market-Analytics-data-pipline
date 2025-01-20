-- Create schema for raw data
CREATE SCHEMA IF NOT EXISTS raw;

-- Create table for daily stock prices
CREATE TABLE IF NOT EXISTS raw.stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open NUMERIC(10,2),
    high NUMERIC(10,2),
    low NUMERIC(10,2),
    close NUMERIC(10,2),
    volume BIGINT,
    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'alpha_vantage',
    UNIQUE(symbol, date)
);

-- Create table for metadata
CREATE TABLE IF NOT EXISTS raw.extraction_metadata (
    id SERIAL PRIMARY KEY,
    extraction_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    symbol VARCHAR(10) NOT NULL,
    records_extracted INTEGER,
    status VARCHAR(20),
    error_message TEXT
);