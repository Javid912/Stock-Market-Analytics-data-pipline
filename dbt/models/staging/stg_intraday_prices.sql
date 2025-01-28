WITH source AS (
    SELECT
        id,
        symbol,
        interval,
        raw_data,
        extracted_at
    FROM {{ source('raw', 'intraday_prices') }}
),

parsed AS (
    SELECT
        id,
        symbol,
        interval,
        timestamp::timestamp as datetime,
        ((raw_data->'Time Series ('||interval||')')::jsonb->timestamp->>'1. open')::numeric as open_price,
        ((raw_data->'Time Series ('||interval||')')::jsonb->timestamp->>'2. high')::numeric as high_price,
        ((raw_data->'Time Series ('||interval||')')::jsonb->timestamp->>'3. low')::numeric as low_price,
        ((raw_data->'Time Series ('||interval||')')::jsonb->timestamp->>'4. close')::numeric as close_price,
        ((raw_data->'Time Series ('||interval||')')::jsonb->timestamp->>'5. volume')::numeric as volume,
        extracted_at
    FROM source
    CROSS JOIN LATERAL jsonb_object_keys((raw_data->'Time Series ('||interval||')')::jsonb) as timestamp
)

SELECT
    id,
    symbol,
    interval,
    datetime,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    extracted_at,
    current_timestamp as transformed_at
FROM parsed 