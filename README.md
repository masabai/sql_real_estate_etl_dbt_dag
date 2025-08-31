# REAL ESTATE SALES 2001–2022 (CONNECTICUT)

Metadata last updated: December 20, 2024
Maintained by: Connecticut Office of Policy and Management

Covers all property sales ≥ $2,000 between October 1 and September 30 of each year.
Includes: Town, Address, Date of Sale, Property Type, Sale Amount, Assessed Value, and related remarks.

Governed by: Connecticut General Statutes §10-261a and §10-261b

Annual sales are reported by Grand List year (Oct 1 → Sep 30).
Some municipalities may not report sales for one year after a revaluation.

# Real Estate ETL with Airflow + Postgres

## Highlights
- Built an Airflow DAG to orchestrate ETL and SQL transformations.
- Loads up to 1M rows of real estate data into Postgres.
- Sequential execution of 6 SQL scripts (data cleaning, profiling, staging).
- Scalable: 100k rows processed in 29 seconds.
- Demonstrates PythonOperator + BashOperator with Postgres integration.

![DAG Screenshot](docs/dag.png)

## DAG Performance Tests
| Sample Size | Duration  | Status          |
|-------------|-----------|-----------------|
| 10k         | 00:00:03  | Passed          |
| 100k        | 00:00:29  | Passed          |
| 1M          | Pending   | Requires tuning |


INITIAL DATA ASSESSMENT (10K SAMPLE, POSTGRES)
Metric	Finding
Rows analyzed	10,000 (out of 1.14M total)
Date range	2002-01-02 → 2021-12-31
Distinct towns	149
Missing date_recorded	0
Missing address	0
Max Sale Amount	$49,000,000
Avg Sale Amount	$520,083
Missing Sale Amount	0
Max Assessed Value	$60,231,850
Distinct Property Types	6
Distinct Residential Types	36
Distinct Non-Use Codes	5
Rows with Assessor Remarks	1,002
Rows with OPM Remarks	2,235
Rows with Location info	368
KEY OBSERVATIONS

Data completeness is strong for sale amount, date recorded, address.
Categorical fields (property type, residential type) are populated but some values missing.
Remarks fields are sparse (assessor, OPM) → not reliable for analysis.
Sale amounts span $2,000 → $49M, avg just over $500k.

ETL WORKFLOW (STEPS 1–6)

STEP 0: Load CSV to Postgres
Raw dataset (~1M rows) downloaded from official CT government source.
Sampled smaller CSV for development and testing.
Loaded CSV into Postgres using Python.
Logs written to sql_project.log for traceability.
Script: etl/load_real_estate.py

STEP 1: Explore Raw Data
Ran exploratory queries to understand schema, row counts, data types, date ranges, distinct values.
Checked for missing/invalid fields.
Script: 01_explore_raw_data.sql

STEP 2: Rename Columns
Renamed to snake_case for consistency.
Removed spaces/special characters.
Standardized casing.
Script: 02_rename_columns.sql

STEP 3: Create Clean View
Built a staging view from the raw dataset.
Preserved all original fields for downstream processing.
Script: 03_create_clean_view.sql

STEP 4: Profile Data Completeness
Counted NULLs and blanks across all columns.
Evaluated categorical coverage (property_type, residential_type, non_use_code).
Found opm_remarks very sparse (~3.7% coverage).
Script: 04_profile_data_completeness.sql

STEP 5: Data Cleaning
Trimmed whitespace, standardized casing.
Dropped opm_remarks based on profiling results.
Replaced blanks in categorical fields with 'Unknown'.
Cleaned assessor_remarks with regex + INITCAP.
Rounded sales_ratio to 2 decimals.
Script: 05_data_cleaning.sql

STEP 6: Exploratory Data Analysis (EDA)
Script: 06_eda.sql

************************************  END OF SQL PROJECT   ************************************************************

DBT IMPLEMENTATION

# Real Estate Sales ETL + Data Modeling

## Dataset
- Source: Connecticut Office of Policy and Management
- Coverage: Property sales ≥ $2,000 from 2001–2022
- Size: ~1.14M rows
- Features: Town, Address, Date of Sale, Property Type, Sale Amount, Assessed Value, Remarks

## ETL Workflow
- Airflow DAG → Orchestrates extract & load into Postgres
- SQL transformations → Cleaning, profiling, staging
- dbt → Modular models (staging → intermediate → marts)
- Performance tests: 100k rows processed in 29s

## Data Model
Implemented a **star schema** for analytical queries:

- **fact_sales**  
  - sale_amount, assessed_value, sales_ratio  
  - keys to dimension tables

- **dim_town**  
  - town_id, town_name

- **dim_property_type**  
  - property_type_id, property_type_name

- **dim_residential_type**  
  - residential_type_id, residential_type_name

- **dim_date**  
  - date_id, year, month, quarter, day_of_week

This model supports:
- Trend analysis by year, quarter
- Breakdown of sales by property type and town
- Average assessed vs. sale price comparisons

## Data Quality
- Dropped sparse fields (opm_remarks < 5% coverage)
- Replaced missing categories with `Unknown`
- Applied dbt tests: `not_null`, `unique`, `accepted_values`

## Tech Stack
- Airflow → ETL orchestration
- Postgres → Data storage
- dbt → Transformation, testing, documentation
- Python → Data exploration, EDA, visualization
- Future: PySpark/Databricks for scaling

## Next Steps
- Scale dbt models to full dataset (1.14M rows)
- Add indexes on date, town, property_type
- Deploy dbt docs & lineage
- Build dashboards → sales trends, property mix
