# Real Estate Sales ETL Pipeline (Connecticut, 2001–2022)

Metadata last updated: December 20, 2024
Maintained by: Connecticut Office of Policy and Management

Covers all property sales ≥ $2,000 between October 1 and September 30 of each year.
Includes: Town, Address, Date of Sale, Property Type, Sale Amount, Assessed Value, and related remarks.
Governed by: Connecticut General Statutes §10-261a and §10-261b

Annual sales are reported by Grand List year (Oct 1 → Sep 30).
Some municipalities may not report sales for one year after a revaluation.

## Project Setup (High-Level)
This project demonstrates a real estate sales ETL pipeline using **Airflow**, **dbt**, and **Postgres**.

- **Airflow** is run in a Docker container using **Docker Desktop**.  
- **Postgres** is used as the local data warehouse (inside Docker).  
- **DAGs** and **dbt models** are mounted from the local project directory:
- **docker-compose.yml** is used to orchestrate Airflow, Postgres, and pgAdmin services.  
- **Dockerfile** ensures dbt and Postgres adapter are installed so the environment is reproducible across container restarts.


## Notes / Tips
- Airflow containers do **not persist dbt installations** between restarts.  
- Installing dbt via the Dockerfile guarantees dbt is always available without manual intervention.


## Highlights
- Built an Airflow DAG to orchestrate ETL and SQL transformations.
- Loads up to 1M rows of real estate data into Postgres.
- Sequential execution of 6 SQL scripts (data cleaning, profiling, staging).
- Scalable: 500k rows processed in 29 seconds.
- Demonstrates PythonOperator + BashOperator with Postgres integration.

## DAG Performance Tests
| Sample Size | Duration  | Status          |
|-------------|-----------|-----------------|
| 10k         | 00:00:03  | Passed          |
| 500k        | 00:00:29  | Passed          |
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
Rows with Location info are limited → missing values are **not filled intentionally**
Remarks fields are sparse (assessor, OPM) → not reliable for analysis.
Sale amounts span $2,000 → $49M, avg just over $500k.

## Project Phases

**Phase I – SQL (Raw Data Cleaning & Exploration)**  
- Data is loaded from CSV URLs into Postgres using **Python only for the loading step and DAG orchestration**.  
- All cleaning, validation, and exploratory transformations are performed **exclusively in SQL**.  
- Focus is on understanding the data, handling missing values, and generating baseline transformations without introducing additional tools.  

**Phase II – dbt (Transformation & Modeling)**
- Cleaning and transformations are **repeated and formalized in dbt models**.  
- Focus is on building a **maintainable pipeline for production-ready marts** while leveraging dbt features, including:  
  - `dbt seed`, `dbt run`, `dbt test` (default & custom tests), `dbt build`, `dbt docs`  
  - Use of `refs` and `macros` for modular, reusable transformations  
- **Note:** Snapshot feature is skipped because the data lacks reliable timestamps and to avoid altering government-provided data excessively.


### PHASE I ETL WORKFLOW (STEPS 1–6)

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

************************************  END OF PHASE I   ************************************************************

DBT IMPLEMENTATION

# Real Estate Sales ETL + Data Modeling

## Dataset
- Source: Connecticut Office of Policy and Management
- Coverage: Property sales ≥ $2,000 from 2001–2022
- Size: ~1.14M rows
- Features: Town, Address, Date of Sale, Property Type, Sale Amount, Assessed Value, Remarks

## PHASE II ETL Workflow

- **Airflow DAG** → Orchestrates the extract & load into the Airflow/Postgres DB; 
- triggers **Phase II transformations** via the bash command:  
  ```bash dbt build

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
This project implements an **ETL workflow starting with extraction** and progressing through transformation and loading:  

- **Airflow** → ETL orchestration, manages DAGs for extraction, transformation, and loading  
- **Postgres** → Central data storage for raw and transformed datasets  
- **dbt** → Transformation, testing, documentation, and building production-ready marts  
- **Python** → Data exploration, initial CSV loading, EDA, and visualization  
- **Future** → PySpark / Databricks for scaling to large datasets

## Next Steps
- Scale dbt models to full dataset (1.14M rows)
- Add indexes on date, town, property_type
- Deploy dbt docs & lineage
- Build dashboards → sales trends, property mix
