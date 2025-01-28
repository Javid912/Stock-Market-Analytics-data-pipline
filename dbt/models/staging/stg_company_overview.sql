WITH source AS (
    SELECT 
        symbol,
        raw_data,
        extracted_at
    FROM {{ source('raw', 'company_overview') }}
)

SELECT
    symbol,
    raw_data->>'Name' as company_name,
    raw_data->>'Description' as description,
    raw_data->>'Exchange' as exchange,
    raw_data->>'Currency' as currency,
    raw_data->>'Country' as country,
    raw_data->>'Sector' as sector,
    raw_data->>'Industry' as industry,
    (raw_data->>'MarketCapitalization')::NUMERIC as market_cap,
    (raw_data->>'EBITDA')::NUMERIC as ebitda,
    (raw_data->>'PERatio')::NUMERIC as pe_ratio,
    (raw_data->>'PEGRatio')::NUMERIC as peg_ratio,
    (raw_data->>'BookValue')::NUMERIC as book_value,
    (raw_data->>'DividendPerShare')::NUMERIC as dividend_per_share,
    (raw_data->>'DividendYield')::NUMERIC as dividend_yield,
    (raw_data->>'52WeekHigh')::NUMERIC as fifty_two_week_high,
    (raw_data->>'52WeekLow')::NUMERIC as fifty_two_week_low,
    raw_data->>'AnalystTargetPrice' as analyst_target_price,
    extracted_at,
    current_timestamp as transformed_at
FROM source 