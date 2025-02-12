-- Create schemas if they don't exist
CREATE SCHEMA IF NOT EXISTS public_raw;
CREATE SCHEMA IF NOT EXISTS public_staging;
CREATE SCHEMA IF NOT EXISTS public_marts;

-- Create raw stock prices table
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
CREATE INDEX IF NOT EXISTS idx_raw_stock_prices_date ON public_raw.raw_stock_prices(date);
CREATE INDEX IF NOT EXISTS idx_raw_stock_prices_symbol ON public_raw.raw_stock_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_raw_company_info_sector ON public_raw.raw_company_info(sector);

-- Add comments for documentation
COMMENT ON TABLE public_raw.raw_stock_prices IS 'Raw daily stock price data from Alpha Vantage API';
COMMENT ON TABLE public_raw.raw_company_info IS 'Raw company information from Alpha Vantage API'; 