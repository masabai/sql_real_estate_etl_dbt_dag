{{ config(
    materialized='table'
) }}

SELECT
    DISTINCT residential_type AS residential_type_id
FROM {{ ref('stg_real_estate_clean') }}
WHERE residential_type IS NOT NULL
