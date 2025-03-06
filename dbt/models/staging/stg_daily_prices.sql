/*
    Staging model for daily stock prices.
    
    This model performs initial data cleaning and type casting on raw stock price data:
    - Ensures proper decimal precision for price fields
    - Converts volume to BIGINT for large numbers
    - Adds audit timestamps for data lineage
    - Filters out records with missing critical fields
    
    This is a foundational model that feeds into:
    - fact_market_metrics
    - dim_company (for latest prices)
    
    Incremental processing can be added later for better performance
    as data volume grows.
*/

WITH source AS (
    -- Extract raw data from source table
    -- This CTE helps isolate source data and makes
    -- it easier to modify source queries if needed
    SELECT * FROM {{ source('raw', 'raw_stock_prices') }}
),

staged AS (
    -- Clean and standardize the raw data
    -- Cast text fields to proper data types
    -- Add audit fields for tracking transformations
    SELECT
        symbol,
        date AS trading_date,
        CAST(open AS DECIMAL(10,2)) AS open_price,
        CAST(high AS DECIMAL(10,2)) AS high_price,
        CAST(low AS DECIMAL(10,2)) AS low_price,
        CAST(close AS DECIMAL(10,2)) AS close_price,
        CAST(volume AS BIGINT) AS volume,
        CURRENT_TIMESTAMP as extracted_at,
        CURRENT_TIMESTAMP as transformed_at
    FROM source
    -- Filter out records with missing critical fields
    -- This ensures data quality in downstream models
    WHERE symbol IS NOT NULL
      AND date IS NOT NULL
      AND close IS NOT NULL
)

-- Final output with all transformed and validated fields
SELECT * FROM staged 