-- Step 1: Data Exploration & Initial Assessment
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
       MIN("Date_Recorded") AS earliest_recorded_date,
       MAX("Date_Recorded") AS latest_recorded_date,
       COUNT(*) FILTER (WHERE "Date_Recorded" IS NULL) AS missing_date_recorded,
       COUNT(DISTINCT "Town") AS distinct_towns,
       COUNT(*) FILTER (WHERE "Address" IS NULL) AS missing_address,
       MIN("Sale_Amount") AS min_sale_amount,
       MAX("Sale_Amount") AS max_sale_amount,
       AVG("Sale_Amount") AS avg_sale_amount,
       COUNT(*) FILTER (WHERE "Sale_Amount" IS NULL) AS missing_sale_amount,
       MIN("Assessed_Value") AS min_assessed_value,
       MAX("Assessed_Value") AS max_assessed_value,
       COUNT(*) FILTER (WHERE "Assessed_Value" IS NULL) AS missing_assessed_value,
       COUNT(DISTINCT "Property_Type") AS distinct_property_types,
       COUNT(*) FILTER (WHERE "Property_Type" IS NULL) AS missing_property_type,
       COUNT(DISTINCT "Residential_Type") AS distinct_res_types,
       COUNT(*) FILTER (WHERE "Residential_Type" IS NULL) AS missing_res_type,
       COUNT(*) FILTER (WHERE "Assessor_Remarks" IS NOT NULL) AS with_assessor_remarks,
       COUNT(*) FILTER (WHERE "OPM_remarks" IS NOT NULL) AS with_opm_remarks
FROM staging.real_estate;

