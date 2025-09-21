-- ========================================
-- Step 1: Data Exploration & Initial Assessment
-- ========================================
-- Purpose: Understand raw data schema, data types, ranges, distributions, and missing values.

-- Verify column names and data types
SELECT
  column_name,
  data_type,
  character_maximum_length,
  is_nullable
FROM information_schema.columns
WHERE table_schema = 'staging'


  AND table_name = 'real_estate'
ORDER BY ordinal_position;

-- Overview & data quality
SELECT COUNT(*) AS total_rows,
       MIN("Date Recorded") AS earliest_recorded_date,
       MAX("Date Recorded") AS latest_recorded_date,
       COUNT(*) FILTER (WHERE "Date Recorded" IS NULL) AS missing_date_recorded,
       COUNT(DISTINCT "Town") AS distinct_towns,
       COUNT(*) FILTER (WHERE "Address" IS NULL) AS missing_address,
       MIN("Sale Amount") AS min_sale_amount,
       MAX("Sale Amount") AS max_sale_amount,
       AVG("Sale Amount") AS avg_sale_amount,
       COUNT(*) FILTER (WHERE "Sale Amount" IS NULL) AS missing_sale_amount,
       MIN("Assessed Value") AS min_assessed_value,
       MAX("Assessed Value") AS max_assessed_value,
       COUNT(*) FILTER (WHERE "Assessed Value" IS NULL) AS missing_assessed_value,
       COUNT(DISTINCT "Property Type") AS distinct_property_types,
       COUNT(*) FILTER (WHERE "Property Type" IS NULL) AS missing_property_type,
       COUNT(DISTINCT "Residential Type") AS distinct_res_types,
       COUNT(*) FILTER (WHERE "Residential Type" IS NULL) AS missing_res_type,
       COUNT(*) FILTER (WHERE "Assessor Remarks" IS NOT NULL) AS with_assessor_remarks,
       COUNT(*) FILTER (WHERE "OPM remarks" IS NOT NULL) AS with_opm_remarks
FROM staging.real_estate;

