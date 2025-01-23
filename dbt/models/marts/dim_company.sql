WITH latest_company_data AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (
            PARTITION BY symbol 
            ORDER BY extracted_at DESC
        ) as rn
    FROM {{ ref('stg_company_overview') }}
),

latest_trading_stats AS (
    SELECT 
        symbol,
        MAX(close_price) as last_close_price,
        AVG(volume) as avg_daily_volume
    FROM {{ ref('stg_daily_prices') }}
    WHERE trading_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY symbol
)

SELECT
    -- Company identifiers
    c.symbol,
    c.company_name,
    
    -- Company categorization
    c.exchange,
    c.sector,
    c.industry,
    c.country,
    c.currency,
    
    -- Company description
    c.description,
    
    -- Financial metrics
    c.market_cap,
    c.ebitda,
    c.pe_ratio,
    c.peg_ratio,
    c.book_value,
    c.dividend_per_share,
    c.dividend_yield,
    
    -- Trading metrics
    c.fifty_two_week_high,
    c.fifty_two_week_low,
    c.analyst_target_price,
    t.last_close_price,
    t.avg_daily_volume,
    
    -- Metadata
    c.extracted_at,
    c.transformed_at as last_updated_at
FROM latest_company_data c
LEFT JOIN latest_trading_stats t
    ON c.symbol = t.symbol
WHERE c.rn = 1  -- Get only the latest record for each company 