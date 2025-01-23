WITH source AS (
    SELECT 
        symbol,
        interval,
        raw_data,
        extracted_at
    FROM {{ source('raw', 'intraday_prices') }}
),

parsed AS (
    SELECT
        symbol,
        interval,
        -- Extract timestamp from the JSON key (e.g., "2024-01-16 16:00:00")
        timestamp::TIMESTAMP as trading_timestamp,
        -- Parse price data from nested JSON
        (raw_data->'Time Series (5min)'->timestamp->>'1. open')::NUMERIC as open_price,
        (raw_data->'Time Series (5min)'->timestamp->>'2. high')::NUMERIC as high_price,
        (raw_data->'Time Series (5min)'->timestamp->>'3. low')::NUMERIC as low_price,
        (raw_data->'Time Series (5min)'->timestamp->>'4. close')::NUMERIC as close_price,
        (raw_data->'Time Series (5min)'->timestamp->>'5. volume')::NUMERIC as volume,
        extracted_at
    FROM source
    CROSS JOIN LATERAL jsonb_object_keys(raw_data->'Time Series (5min)') as timestamp
)

SELECT 
    symbol,
    interval,
    trading_timestamp,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    extracted_at,
    {{ dbt_utils.current_timestamp() }} as transformed_at
FROM parsed 