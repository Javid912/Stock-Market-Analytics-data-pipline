/*
    Fact table for daily market metrics by sector.
    
    This model calculates key market performance indicators:
    - Daily price changes and percentage movements
    - Trading volume aggregations
    - Sector-level statistics
    - Market sentiment indicators (gainers vs losers)
    
    The model uses window functions to calculate:
    - Previous day's closing prices
    - Daily price changes
    - Running aggregations
    
    This fact table powers:
    - Market overview dashboards
    - Sector performance analysis
    - Trading volume analysis
    - Daily market sentiment reports
*/

WITH daily_changes AS (
    -- Calculate daily price changes and join with company info
    -- Uses window functions to get previous day's prices
    -- Includes sector and market cap for aggregations
    SELECT
        dp.trading_date,
        dp.symbol,
        dp.close_price,
        dp.volume,
        LAG(dp.close_price) OVER (PARTITION BY dp.symbol ORDER BY dp.trading_date) as prev_close,
        c.sector,
        c.market_cap
    FROM {{ ref('stg_daily_prices') }} dp
    JOIN {{ ref('dim_company') }} c ON dp.symbol = c.symbol
),

daily_metrics AS (
    -- Aggregate metrics by sector and trading date
    -- Calculates various market performance indicators:
    -- 1. Number of companies
    -- 2. Total market cap
    -- 3. Gainers vs Losers count
    -- 4. Volume statistics
    -- 5. Average price changes
    SELECT
        trading_date,
        sector,
        COUNT(DISTINCT symbol) as companies_count,
        SUM(market_cap) as total_market_cap,
        SUM(CASE WHEN close_price > prev_close THEN 1 ELSE 0 END) as gainers_count,
        SUM(CASE WHEN close_price < prev_close THEN 1 ELSE 0 END) as losers_count,
        SUM(volume) as total_volume,
        AVG((close_price - prev_close) / prev_close * 100) as avg_price_change_pct
    FROM daily_changes
    WHERE prev_close IS NOT NULL  -- Exclude first day of data where we can't calculate change
    GROUP BY trading_date, sector
)

-- Final fact table with all market metrics
-- Includes calculation timestamp for data freshness tracking
SELECT
    trading_date,
    sector,
    companies_count,
    total_market_cap,
    gainers_count,
    losers_count,
    total_volume,
    avg_price_change_pct,
    current_timestamp as calculated_at
FROM daily_metrics 