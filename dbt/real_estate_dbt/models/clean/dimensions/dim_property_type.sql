{{ config(
    materialized='table'
) }}

SELECT
    DISTINCT property_type AS property_type_id
FROM {{ ref('stg_real_estate_clean') }}
WHERE property_type IS NOT NULL
