SELECT
    "Serial Number"          AS serial_number,
    "List Year"              AS list_year,
    {{ clean_date('"Date Recorded"') }} AS date_recorded,
    "Assessed Value"         AS assessed_value,
    "Sale Amount"            AS sale_amount,
    {{ round_numeric('"Sales Ratio"') }} AS sales_ratio,
    {{ clean_string('"Town"') }} AS town,
    {{ clean_string('"Address"') }} AS address,
    {{ clean_text('"Property Type"') }} AS property_type,
    {{ clean_text('"Residential Type"') }} AS residential_type,
    {{ clean_text('"Non Use Code"') }} AS non_use_code,

    REGEXP_REPLACE(
        INITCAP(COALESCE("Assessor Remarks", 'Unknown')),
        '\b(H\d{5}(-\d+)?|F\d{5}|G\d{5}-\d+|SFLA|AC|UNKNOWN|R/C/8|BAA|COMM|CONDO)\b',
        '\U\1',
        'gi'
    ) AS cleaned_remark,
    "Location" AS location
FROM {{ ref('realestate_sales') }}
