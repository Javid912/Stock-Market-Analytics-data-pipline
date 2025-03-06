/*
    Staging model for company information.
    
    This model standardizes company data from Alpha Vantage API:
    - Casts numeric fields to appropriate types
    - Ensures consistent handling of shares outstanding
    - Adds audit timestamps for tracking changes
    - Filters out incomplete company records
    
    This staging model is a key input for:
    - dim_company (primary source)
    - fact_market_metrics (for company attributes)
    
    The data is mostly static, with occasional updates
    to shares outstanding and earnings per share.
*/

WITH source AS (
    -- Extract raw company data
    -- This CTE provides a clean break from source
    -- making it easier to handle source changes
    SELECT * FROM {{ source('raw', 'raw_company_info') }}
),

staged AS (
    -- Transform and clean company data
    -- Handle type conversions and add audit fields
    SELECT
        symbol,
        company_name,
        sector,
        industry,
        country,
        CAST(shares_outstanding AS BIGINT) as shares_outstanding,
        currency,
        CAST(earnings_per_share AS DECIMAL(10,2)) as earnings_per_share,
        CURRENT_TIMESTAMP as created_at,
        CURRENT_TIMESTAMP as updated_at
    FROM source
    -- Ensure critical fields are present
    -- Company records must have symbol and name
    WHERE symbol IS NOT NULL
      AND company_name IS NOT NULL
)

-- Final output of cleaned company data
SELECT * FROM staged 