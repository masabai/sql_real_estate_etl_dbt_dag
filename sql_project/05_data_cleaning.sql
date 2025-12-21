-- Step 5: Perform Data Cleaning (exclude `opm_remarks`)
-- Purpose: Clean key columns based on profiling results.
-- Excludes `opm_remarks` due to low non-null percentage (~3.7%).
-- Cleans strings, standardizes casing, replaces empty strings, and rounds numeric columns.
DROP VIEW IF EXISTS staging.real_estate_clean;

CREATE OR REPLACE VIEW staging.real_estate_clean AS
SELECT
    serial_number,
    list_year,
    NULLIF(date_recorded, '')::DATE AS date_recorded,
    assessed_value,
    sale_amount,
    ROUND(sales_ratio::numeric, 2) AS sales_ratio,
    TRIM(town) AS town,
    INITCAP(address) AS address,
    COALESCE(NULLIF(TRIM(property_type), ''), 'Unknown') AS property_type,
    COALESCE(NULLIF(TRIM(residential_type), ''), 'Unknown') AS residential_type,
    COALESCE(NULLIF(TRIM(non_use_code), ''), 'Unknown') AS non_use_code,
    REGEXP_REPLACE(
        INITCAP(COALESCE(assessor_remarks, 'Unknown')),
        '\b(H\d{5}(-\d+)?|F\d{5}|G\d{5}-\d+|SFLA|AC|UNKNOWN|R/C/8|BAA|COMM|CONDO)\b',
        '\U\1',
        'gi'
    ) AS cleaned_remark,
    location
FROM staging.real_estate;
