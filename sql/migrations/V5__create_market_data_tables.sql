/*
    Migration V5: Create Market Data Schema and Tables
    
    This migration establishes the core data structure for our market data pipeline:
    1. Creates three schemas for our layered architecture:
       - public_raw: Landing zone for raw data
       - public_staging: Cleaned and validated data
       - public_marts: Business-ready data models
    
    2. Creates two main raw tables:
       - raw_stock_prices: Daily price and volume data
       - raw_company_info: Company reference data
    
    3. Implements best practices:
       - Appropriate data types and precision
       - Primary key constraints
       - Useful indexes for performance
       - Timestamp fields for auditing
       - Detailed table comments
*/

-- Create schemas if they don't exist
-- Each schema serves a specific purpose in our data architecture
CREATE SCHEMA IF NOT EXISTS public_raw;
CREATE SCHEMA IF NOT EXISTS public_staging;
CREATE SCHEMA IF NOT EXISTS public_marts;

-- Create raw stock prices table
-- Stores daily OHLCV (Open, High, Low, Close, Volume) data
-- Composite primary key ensures no duplicate entries
CREATE TABLE IF NOT EXISTS public_raw.raw_stock_prices (
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, date)
);

-- Create raw company info table
-- Stores relatively static company reference data
-- Single-column primary key as symbol is unique
CREATE TABLE IF NOT EXISTS public_raw.raw_company_info (
    symbol VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    country VARCHAR(50),
    shares_outstanding BIGINT,
    currency VARCHAR(3),
    earnings_per_share DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for better query performance
-- These support common query patterns and joins
CREATE INDEX IF NOT EXISTS idx_raw_stock_prices_date ON public_raw.raw_stock_prices(date);
CREATE INDEX IF NOT EXISTS idx_raw_stock_prices_symbol ON public_raw.raw_stock_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_raw_company_info_sector ON public_raw.raw_company_info(sector);

-- Add comments for documentation
-- These help other developers understand the purpose of each table
COMMENT ON TABLE public_raw.raw_stock_prices IS 'Raw daily stock price data from Alpha Vantage API';
COMMENT ON TABLE public_raw.raw_company_info IS 'Raw company information from Alpha Vantage API'; 