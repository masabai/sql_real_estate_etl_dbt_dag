-- Step 4: Profile Data Completeness
-- Purpose: Assess column-level completeness to guide cleaning decisions.
-- Calculates percentage of non-null values for each key column.

SELECT
  ROUND(100.0 * COUNT(serial_number) / COUNT(*), 1) AS pct_serial_number,
  ROUND(100.0 * COUNT(list_year) / COUNT(*), 1) AS pct_list_year,
  ROUND(100.0 * COUNT(date_recorded) / COUNT(*), 1) AS pct_date_recorded,
  ROUND(100.0 * COUNT(assessed_value) / COUNT(*), 1) AS pct_assessed_value,
  ROUND(100.0 * COUNT(sale_amount) / COUNT(*), 1) AS pct_sale_amount,
  ROUND(100.0 * COUNT(sales_ratio) / COUNT(*), 1) AS pct_sales_ratio,
  ROUND(100.0 * COUNT(town) / COUNT(*), 1) AS pct_town,
  ROUND(100.0 * COUNT(address) / COUNT(*), 1) AS pct_address,
  ROUND(100.0 * COUNT(property_type) / COUNT(*), 1) AS pct_property_type,
  ROUND(100.0 * COUNT(residential_type) / COUNT(*), 1) AS pct_residential_type,
  ROUND(100.0 * COUNT(non_use_code) / COUNT(*), 1) AS pct_non_use_code,
  ROUND(100.0 * COUNT(assessor_remarks) / COUNT(*), 1) AS pct_assessor_remarks,
  ROUND(100.0 * COUNT(opm_remarks) / COUNT(*), 1) AS pct_opm_remarks,
  ROUND(100.0 * COUNT(location) / COUNT(*), 1) AS pct_location
FROM staging.real_estate;
