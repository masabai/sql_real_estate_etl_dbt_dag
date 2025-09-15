{{ config(
    materialized='table',
    description='Mart: Compare current vs previous sale and detect spikes or drops in property values'
) }}

SELECT
 list_year,
 date_recorded,
 town,
 address,
 property_type,
 sale_amount - LAG(sale_amount) OVER (PARTITION BY town ORDER BY date_recorded) AS price_change,
 LEAD(sale_amount) OVER (PARTITION BY town ORDER BY date_recorded) AS next_sale_price
FROM {{ ('staging.stg_real_estate_clean') }}

