
{{ config(
    materialized='table',
    description='Mart: Identify top or bottom properties quickly'
) }}

WITH town_stats AS (
    SELECT
        f.town,
        COUNT(*) AS sales_count,
        ROUND(AVG(f.sale_amount::NUMERIC),2) AS avg_sale,
        ROUND(AVG(f.sale_amount::NUMERIC - f.assessed_value::NUMERIC),2) AS avg_price_difference,
        ROUND(AVG(f.sale_amount::NUMERIC / NULLIF(f.assessed_value::NUMERIC,0)),2) AS avg_sales_ratio,
        RANK() OVER (ORDER BY COUNT(*) DESC) AS town_rank
    FROM {{ ref('fact_sales') }} AS f
    JOIN {{ ref('dim_town') }} AS d
      ON f.town = d.town
    GROUP BY f.town
)
SELECT *
FROM town_stats
WHERE town_rank <= 10

