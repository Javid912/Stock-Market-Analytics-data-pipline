/*
    Dimension table for company information enriched with latest market data.
    This model combines static company information with dynamic market metrics
    to provide a comprehensive view of each company's current state.
    
    The model uses several CTEs to:
    1. Get base company information
    2. Calculate latest price metrics
    3. Compute 30-day average volumes
    4. Calculate market metrics (market cap, P/E ratio)
    
    Updated daily when new price data arrives.
*/

WITH company_info AS (
    -- Base company information from staging
    SELECT * FROM {{ ref('stg_company_info') }}
),

latest_prices AS (
    -- Get the most recent price data for each symbol
    -- Uses window function to identify latest prices
    SELECT 
        symbol,
        close_price as last_close_price,
        volume as last_volume,
        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY trading_date DESC) as rn
    FROM {{ ref('stg_daily_prices') }}
),

avg_volumes AS (
    -- Calculate 30-day average trading volume
    -- Used to understand typical trading activity
    SELECT
        symbol,
        AVG(volume) as avg_daily_volume
    FROM {{ ref('stg_daily_prices') }}
    WHERE trading_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY symbol
),

market_metrics AS (
    -- Calculate key market metrics:
    -- 1. Market capitalization (price * shares outstanding)
    -- 2. P/E ratio (price / earnings per share)
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

-- Final dimension table combining all metrics
-- Includes both static company data and dynamic market metrics
SELECT
    c.symbol,
    c.company_name,
    c.sector,
    c.industry,
    c.country,
    c.shares_outstanding,
    c.currency,
    'NASDAQ' as exchange,  -- Hardcoded for now, should be made dynamic in future
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