{{ config(
    materialized='table'
) }}

SELECT DISTINCT town
    FROM {{ ref('stg_real_estate_clean') }}
    WHERE town IS NOT NULL
