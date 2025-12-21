-- Step 2: Rename Columns to Snake_Case
-- Purpose: Standardize column names for easier querying and consistency
-- All renames apply to the clean working view created in Step 2
-- Each column is renamed from the original format to snake_case:

ALTER TABLE staging.real_estate RENAME COLUMN "Serial Number"    TO serial_number;
ALTER TABLE staging.real_estate RENAME COLUMN "List Year"        TO list_year;
ALTER TABLE staging.real_estate RENAME COLUMN "Date Recorded"    TO date_recorded;
ALTER TABLE staging.real_estate RENAME COLUMN "Town"             TO town;
ALTER TABLE staging.real_estate RENAME COLUMN "Address"          TO address;
ALTER TABLE staging.real_estate RENAME COLUMN "Assessed Value"   TO assessed_value;
ALTER TABLE staging.real_estate RENAME COLUMN "Sale Amount"      TO sale_amount;
ALTER TABLE staging.real_estate RENAME COLUMN "Sales Ratio"      TO sales_ratio;
ALTER TABLE staging.real_estate RENAME COLUMN "Property Type"    TO property_type;
ALTER TABLE staging.real_estate RENAME COLUMN "Residential Type" TO residential_type;
ALTER TABLE staging.real_estate RENAME COLUMN "Non Use Code"     TO non_use_code;
ALTER TABLE staging.real_estate RENAME COLUMN "Assessor Remarks" TO assessor_remarks;
ALTER TABLE staging.real_estate RENAME COLUMN "OPM remarks"      TO opm_remarks;
ALTER TABLE staging.real_estate RENAME COLUMN "Location"         TO location;
