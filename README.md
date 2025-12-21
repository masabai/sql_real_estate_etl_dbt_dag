# Real Estate Sales ETL Pipeline (Connecticut, 2001–2022)

## Project Summary
This project implements a mostly SQL/dbt ETL workflow on historical Connecticut real estate sales data (2001–2022), with Python only used for data ingestion and Airflow DAG orchestration.  
It demonstrates staging, transformation, and modeling of data into fact and dimension tables, along with automated testing and validation.  
A 10K sample seed is used for development, while the full dataset (~1M rows) is loaded for production-style ETL.

## Data Source & Coverage
Metadata last updated: December 20, 2024
Maintained by: Connecticut Office of Policy and Management

Covers all property sales ≥ $2,000 between October 1 and September 30 of each year.
Includes: Town, Address, Date of Sale, Property Type, Sale Amount, Assessed Value, and related remarks.
Governed by: Connecticut General Statutes §10-261a and §10-261b

Annual sales are reported by Grand List year (Oct 1 → Sep 30).
Some municipalities may not report sales for one year after a revaluation.

## Project Setup (High-Level)
This project demonstrates a real estate sales ETL pipeline using **Airflow**, **dbt**, and **Postgres**.

- This project demonstrates a real estate sales ETL pipeline using Airflow, dbt, and Postgres.
- The pipeline is fully containerized using Docker, with services - orchestrated via docker-compose.
- Airflow orchestrates the pipeline, dynamically fetching real estate sales data from a URL on data.gov at the start of each run.
- Postgres is used as the local data warehouse (containerized within Docker).
- The Airflow DAG is configured to send notifications to a designated Slack channel upon task failures, ensuring operational monitoring.
- dbt models are run within the Airflow environment for robust data transformation and testing.

## Notes / Tips
- Airflow containers do **not persist dbt installations** between restarts.  
- Installing dbt via the Dockerfile guarantees dbt is always available without manual intervention.

## Highlights
- Built Airflow DAGs to orchestrate ETL and SQL transformations:
- load_explore_dag → executes sequential SQL scripts for exploration, cleaning, and staging.
- dbt_realestate_dag → runs dbt build on the real_estate_dbt project inside Airflow.
- Sequential execution of 6 SQL scripts (data cleaning, profiling, staging).
- Demonstrates PythonOperator + BashOperator + Slack integration.

### DAG Slack Notifications
Both DAGs send success and failure messages to a Slack channel via SlackWebhookOperator.

### Initial Data Assessment (10K Sample, POSTGRES)
| Metric                     | Finding                     |
| -------------------------- | --------------------------- |
| Rows analyzed              | 10,000 (out of 1.14M total) |
| Date range                 | 2002-01-02 → 2021-12-31     |
| Distinct towns             | 149                         |
| Missing date\_recorded     | 0                           |
| Missing address            | 0                           |
| Max Sale Amount            | \$49,000,000                |
| Avg Sale Amount            | \$520,083                   |
| Missing Sale Amount        | 0                           |
| Max Assessed Value         | \$60,231,850                |
| Distinct Property Types    | 6                           |
| Distinct Residential Types | 36                          |
| Distinct Non-Use Codes     | 5                           |
| Rows with Assessor Remarks | 1,002                       |
| Rows with OPM Remarks      | 2,235                       |
| Rows with Location info    | 368                         |

### Key Observation
Data completeness is strong for sale amount, date recorded, address.
Categorical fields (property type, residential type) are populated but some values missing.
Rows with Location info are limited → missing values, NULLs are **not filled intentionally**
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

## PHASE II DBT  (Transformation & Modeling)

### Dataset
Same dataset as previously described (Connecticut Office of Policy and Management, property sales ≥ $2,000 from 2001–2022)

### PHASE II ETL Workflow

- **Airflow DAG** → Orchestrates the extract & load into the Airflow/Postgres DB; 
- triggers **Phase II transformations** via the bash command:
  ```bash
dbt build

#### Model inspection:
    ```bash
dbt list       # lists all models that will be built
dbt test       # runs all data tests on models
dbt docs generate && dbt docs serve  # generate and view dbt documentation locally  
`

## Data Model
Implemented a **star schema** for analytical queries:

- **fact_sales**
  - Measures: sale_amount, assessed_value, avg_sales_ratio  
  - Keys: list_year, date_recorded, town, property_type_id, residential_type_id  
  - Sources: stg_real_estate_clean joined with dim_town, dim_property_type, dim_residential_type
- **dim_town**  
  - town_id, town_name

- **dim_property_type**  
  - property_type_id, property_type_name

- **dim_residential_type**  
  - residential_type_id, residential_type_name

This model supports:
- Trend analysis by year, quarter
- Breakdown of sales by property type and town
- Average assessed vs. sale price comparisons

## Data Quality
- Dropped sparse fields (opm_remarks < 5% coverage)
- Replaced missing categories with Unknown
- Applied dbt tests:
  - Generic: not_null, unique, accepted_values, relationships
  - Custom: sales_ratio range, positive sale_amount, positive assessed_value
- Tests organized in dims.yml and facts.yml

### Data Models and Marts
Models are structured under the clean layer with dimensions, facts, and summary marts:

models/clean/
  ├── compare_current_previous.sql  
  ├── dimensions/  
  │     ├── dim_property_type.sql  
  │     ├── dim_residential_type.sql  
  │     ├── dim_town.sql  
  │     └── dims.yml  
  ├── facts/  
  │     ├── fact_sales.sql  
  │     └── facts.yml  
  ├── property_type_summary.sql  
  ├── sales_flag_summary.sql  
  ├── sales_over_time.sql  
  ├── schema.yml  
  └── top_ten_towns.sql  

- Fact and dimension models implement a star schema for analytical queries  
- Additional marts (summaries, comparisons, top N analysis) provide business insights  

## Tech Stack
This project implements an ETL workflow starting with extraction and progressing through transformation and loading:

- Airflow → ETL orchestration, manages DAGs for extraction, transformation, and loading
- Postgres → Central data storage for raw and transformed datasets
- dbt → Transformation, testing, documentation, and building production-ready marts
- Python → Data exploration, initial CSV loading, EDA, and visualization
- Slack → Channel integration for DAG success and failure notifications

## Documentation and Snapshots
Project artifacts are stored under the `docs` and `dbt` directories:

- **docs/airflow_screenshots** → Airflow DAG runs and orchestration flow:
### Figure 1: RealEstate dbt build DAG – Graph View
  - [![Airflow DAG Screenshot](docs/airflow_screenshots/dbt_realestate_dag.png)](docs/airflow_screenshots/dbt_realestate_dag.png)
### Figure 2: RealEstate SQL ETL DAG (Load and Explore Data) - Graph View
  - [![Load & Explore DAG Screenshot](docs/airflow_screenshots/load_explore_dag.png)](docs/airflow_screenshots/load_explore_dag.png)

- **docs/dbt_docs_screenshots** → dbt docs UI, lineage, test results, and ER diagram of the star schema:
### Figure 1: Entity-Relationship Diagram
  - [![Entity-Relationship Diagram](docs/dbt_docs_screenshots/ER_diagram.png)](docs/dbt_docs_screenshots/ER_diagram.png)
### Figure 2: dbt Custom Test Overview
  - [![dbt Custom Test Screenshot](docs/dbt_docs_screenshots/dbt_custom_test.png)](docs/dbt_docs_screenshots/dbt_custom_test.png)
### Figure 3: dbt Fact Sales Model
  - [![dbt Fact Sales Screenshot](docs/dbt_docs_screenshots/dbt_fact_sales.png)](docs/dbt_docs_screenshots/dbt_fact_sales.png)
### Figure 4: dbt Test Run – Set 1
  - [![dbt Test Run Set 1 Screenshot](docs/dbt_docs_screenshots/dbt_test_run_set1.png)](docs/dbt_docs_screenshots/dbt_test_run_set1.png)
### Figure 5: dbt Test Run – Set 2
  - [![dbt Test Run Set 2 Screenshot](docs/dbt_docs_screenshots/dbt_test_run_set2.png)](docs/dbt_docs_screenshots/dbt_test_run_set2.png)

- **dbt/real_estate_dbt/snapshots** → dbt snapshot CSVs for marts (historical tracking of fact and dimension tables):
 - [Staging Real Estate Snapshot CSV](https://github.com/masabai/RealEstate/blob/master/dbt/real_estate_dbt/snapshots/dbt/staging_real_estate.csv)
 - [Property Type Summary Snapshot CSV](https://github.com/masabai/RealEstate/blob/master/dbt/real_estate_dbt/snapshots/dbt/property_type_summary.csv)
 - [Fact Sales Snapshot CSV](https://github.com/masabai/RealEstate/blob/master/dbt/real_estate_dbt/snapshots/dbt/fact_sales.csv)
 - [Dim Property Type Snapshot CSV](https://github.com/masabai/RealEstate/blob/master/dbt/real_estate_dbt/snapshots/dbt/dim_property_type.csv)
