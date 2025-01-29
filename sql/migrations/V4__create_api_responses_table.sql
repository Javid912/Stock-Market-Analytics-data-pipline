-- Create raw schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS raw;

-- Create api_responses table
CREATE TABLE IF NOT EXISTS raw.api_responses (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(100) NOT NULL,
    request_params JSONB NOT NULL,
    response_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_api_responses_endpoint ON raw.api_responses(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_responses_created_at ON raw.api_responses(created_at);

-- Add comment for documentation
COMMENT ON TABLE raw.api_responses IS 'Stores raw API responses from Alpha Vantage API calls'; 