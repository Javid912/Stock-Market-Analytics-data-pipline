/*
    Custom dbt test to verify that a numeric column contains only positive values.
    
    This test is particularly useful for financial data where certain metrics
    should never be negative, such as:
    - Volume
    - Market capitalization
    - Share prices
    - Number of shares outstanding
    
    Args:
        model: The dbt model to test
        column_name: The name of the numeric column to verify
        
    Returns:
        Failing rows where the column value is either NULL or less than or equal to 0
        An empty result indicates a passing test
*/

{% test positive(model, column_name) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} <= 0
   OR {{ column_name }} IS NULL

{% endtest %} 