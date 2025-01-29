WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_stock_prices') }}
),

staged AS (
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
    WHERE symbol IS NOT NULL
      AND date IS NOT NULL
      AND close IS NOT NULL
)

SELECT * FROM staged 