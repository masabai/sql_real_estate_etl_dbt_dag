
{{ config(
    materialized='table',
    description='Mart: Track market growth, sales over time'
) }}

WITH sales_by_year AS (
    SELECT
        list_year,
        COUNT(*) AS sales_count,
        ROUND(AVG(sale_amount::NUMERIC),2) AS avg_sale,
        ROUND(AVG(sale_amount::NUMERIC - assessed_value::NUMERIC),2) AS avg_price_difference,
        ROUND(AVG(sale_amount::NUMERIC / NULLIF(assessed_value::NUMERIC,0)),2) AS avg_sales_ratio
    FROM {{ ref('fact_sales') }}
    GROUP BY list_year
    ORDER BY list_year
)
SELECT *
FROM sales_by_year
