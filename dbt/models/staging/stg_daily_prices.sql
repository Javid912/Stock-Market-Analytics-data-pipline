WITH source AS (
    SELECT 
        symbol,
        raw_data,
        extracted_at
    FROM {{ source('raw', 'daily_prices') }}
),

parsed AS (
    SELECT
        symbol,
        date::DATE as trading_date,
        (raw_data->'Time Series (Daily)'->date->>'1. open')::NUMERIC as open_price,
        (raw_data->'Time Series (Daily)'->date->>'2. high')::NUMERIC as high_price,
        (raw_data->'Time Series (Daily)'->date->>'3. low')::NUMERIC as low_price,
        (raw_data->'Time Series (Daily)'->date->>'4. close')::NUMERIC as close_price,
        (raw_data->'Time Series (Daily)'->date->>'5. volume')::NUMERIC as volume,
        extracted_at
    FROM source
    CROSS JOIN LATERAL jsonb_object_keys(raw_data->'Time Series (Daily)') as date
)

SELECT 
    symbol,
    trading_date,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    extracted_at,
    current_timestamp as transformed_at
FROM parsed 