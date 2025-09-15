
{{ config(
    materialized='table',
    description='Mart: Quick view of market valuation per property.'
) }}

WITH sales_flag AS (
    SELECT *,
        CASE
            WHEN sales_ratio < 0.5 THEN 'Under-valued'
            WHEN sales_ratio BETWEEN 0.5 AND 0.8 THEN 'Fair'
            ELSE 'Over-valued'
        END AS ratio_flag
    FROM {{ ref('stg_real_estate_clean') }}
)
SELECT
    ratio_flag,
    COUNT(*) AS flag_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) || '%' AS pct
FROM sales_flag
GROUP BY ratio_flag
