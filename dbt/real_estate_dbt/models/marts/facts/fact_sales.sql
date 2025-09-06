{{ config(
    materialized='table'
) }}

SELECT
    r.list_year,
    4.date_recorded,
    t.town,
    p.property_type_id,
    rt.residential_type_id,
    sale_amount,
    assessed_value,
    sale_amount / NULLIF(assessed_value,0)AS avg_sales_ratio
FROM {{ ref('stg_real_estate_clean') }} r
JOIN {{ ref('dim_town') }} t
    ON r.town = t.town
JOIN {{ ref('dim_property_type') }} p
    ON r.property_type = p.property_type_id
JOIN {{ ref('dim_residential_type') }} rt
    ON r.residential_type = rt.residential_type_id
