{{ config(
    materialized='table'
) }}

SELECT
    DISTINCT town AS town_id
FROM {{ ref('stg_real_estate_clean') }}
WHERE town IS NOT NULL
