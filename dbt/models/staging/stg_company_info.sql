WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_company_info') }}
),

staged AS (
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
    WHERE symbol IS NOT NULL
      AND company_name IS NOT NULL
)

SELECT * FROM staged 