{{
    config(
        materialized='incremental',
        unique_key=['symbol', 'date']
    )
}}

WITH source AS (
    SELECT 
        symbol,
        date,
        open,
        high,
        low,
        close,
        volume,
        ingestion_timestamp
    FROM {{ source('raw', 'stock_prices') }}
    {% if is_incremental() %}
        WHERE ingestion_timestamp > (SELECT MAX(ingestion_timestamp) FROM {{ this }})
    {% endif %}
),

validation AS (
    SELECT 
        *,
        CASE 
            WHEN open > high OR close > high OR low > high THEN 'Invalid price ranges'
            WHEN volume < 0 THEN 'Invalid volume'
            ELSE 'Valid'
        END as data_quality_check
    FROM source
)

SELECT 
    symbol,
    date,
    open,
    high,
    low,
    close,
    volume,
    ingestion_timestamp,
    data_quality_check
FROM validation
WHERE data_quality_check = 'Valid'