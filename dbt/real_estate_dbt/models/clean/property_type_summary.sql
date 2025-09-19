

{{ config(
    materialized='table',
    description='Mart: Property type breakdown with running total'
) }}

WITH prop_stats AS (
    SELECT
        f.property_type_id,
        COUNT(*) AS count,
        ROUND(AVG(sale_amount::NUMERIC),2) AS avg_sale,
        ROUND(AVG(sale_amount::NUMERIC - assessed_value::NUMERIC),2) AS avg_price_difference,
        ROUND(AVG(sale_amount::NUMERIC / NULLIF(assessed_value::NUMERIC,0)),2) AS avg_sales_ratio
    FROM {{ ref('fact_sales') }}AS f
    JOIN {{ ref('dim_property_type') }} AS d
    ON f.property_type_id = d.property_type_id
    GROUP BY f.property_type_id
)
SELECT *,
       SUM(count) OVER (ORDER BY count DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_count
FROM prop_stats

