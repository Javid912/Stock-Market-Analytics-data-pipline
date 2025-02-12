WITH daily_changes AS (
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
    WHERE prev_close IS NOT NULL
    GROUP BY trading_date, sector
)

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