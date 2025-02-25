WITH company_info AS (
    SELECT * FROM {{ ref('stg_company_info') }}
),

latest_prices AS (
    SELECT 
        symbol,
        close_price as last_close_price,
        volume as last_volume,
        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY trading_date DESC) as rn
    FROM {{ ref('stg_daily_prices') }}
),

avg_volumes AS (
    SELECT
        symbol,
        AVG(volume) as avg_daily_volume
    FROM {{ ref('stg_daily_prices') }}
    WHERE trading_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY symbol
),

market_metrics AS (
    SELECT
        company_info.symbol,
        last_close_price * shares_outstanding as market_cap,
        CASE 
            WHEN earnings_per_share > 0 THEN last_close_price / earnings_per_share 
            ELSE NULL 
        END as pe_ratio
    FROM company_info
    JOIN latest_prices ON company_info.symbol = latest_prices.symbol
    WHERE rn = 1
)

SELECT
    c.symbol,
    c.company_name,
    c.sector,
    c.industry,
    c.country,
    c.shares_outstanding,
    c.currency,
    'NASDAQ' as exchange,
    m.market_cap,
    m.pe_ratio,
    lp.last_close_price,
    av.avg_daily_volume,
    c.created_at,
    c.updated_at as last_updated_at
FROM company_info c
LEFT JOIN market_metrics m ON c.symbol = m.symbol
LEFT JOIN latest_prices lp ON c.symbol = lp.symbol AND lp.rn = 1
LEFT JOIN avg_volumes av ON c.symbol = av.symbol 