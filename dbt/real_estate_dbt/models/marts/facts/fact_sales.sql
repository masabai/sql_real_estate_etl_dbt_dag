{{ config(
    materialized='table'
) }}

SELECT
    r.list_year,
    t.town_id,
    p.property_type_id,
    rt.residential_type_id,
    COUNT(*) AS num_sales,
    SUM(sale_amount) AS total_sale_amount,
    AVG(sale_amount) AS avg_sale_amount,
    AVG(sale_amount - assessed_value) AS avg_price_difference,
    AVG(sale_amount / NULLIF(assessed_value,0)) AS avg_sales_ratio
FROM {{ ref('stg_real_estate_clean') }} r
JOIN {{ ref('dim_town') }} t
    ON r.town = t.town_id
JOIN {{ ref('dim_property_type') }} p
    ON r.property_type = p.property_type_id
JOIN {{ ref('dim_residential_type') }} rt
    ON r.residential_type = rt.residential_type_id
GROUP BY
    r.list_year,
    t.town_id,
    p.property_type_id,
    rt.residential_type_id
