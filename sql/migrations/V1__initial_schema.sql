-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;

-- Raw tables to store data exactly as received from API
CREATE TABLE IF NOT EXISTS raw.daily_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    raw_data JSONB NOT NULL,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, extracted_at)
);

CREATE TABLE IF NOT EXISTS raw.intraday_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    interval VARCHAR(5) NOT NULL,
    raw_data JSONB NOT NULL,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, interval, extracted_at)
);

CREATE TABLE IF NOT EXISTS raw.company_overview (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    raw_data JSONB NOT NULL,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, extracted_at)
);

-- Create indexes for better query performance
CREATE INDEX idx_daily_prices_symbol ON raw.daily_prices(symbol);
CREATE INDEX idx_daily_prices_extracted_at ON raw.daily_prices(extracted_at);
CREATE INDEX idx_intraday_prices_symbol ON raw.intraday_prices(symbol);
CREATE INDEX idx_intraday_prices_extracted_at ON raw.intraday_prices(extracted_at);
CREATE INDEX idx_company_overview_symbol ON raw.company_overview(symbol);

-- Create a function to update extracted_at timestamp
CREATE OR REPLACE FUNCTION update_extracted_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.extracted_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update extracted_at
CREATE TRIGGER update_daily_prices_extracted_at
    BEFORE UPDATE ON raw.daily_prices
    FOR EACH ROW
    EXECUTE FUNCTION update_extracted_at();

CREATE TRIGGER update_intraday_prices_extracted_at
    BEFORE UPDATE ON raw.intraday_prices
    FOR EACH ROW
    EXECUTE FUNCTION update_extracted_at();

CREATE TRIGGER update_company_overview_extracted_at
    BEFORE UPDATE ON raw.company_overview
    FOR EACH ROW
    EXECUTE FUNCTION update_extracted_at();