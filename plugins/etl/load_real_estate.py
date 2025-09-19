from sqlalchemy import create_engine, text
from pathlib import Path
import pandas as pd
import requests
import logging
import yaml
import os

# --------------------------------------------------
# Configuration
# --------------------------------------------------
CSV_URL = 'https://data.ct.gov/api/views/5mzw-sjtu/rows.csv?accessType=DOWNLOAD'
RAW_CSV = 'large_file_million_rows.csv'
TABLE_NAME = "real_estate"
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLED_CSV ="realestate_sales.csv"

# ----------------------------
# Project root & YAML config
# ----------------------------
YML_FILE = PROJECT_ROOT / "config.yml"

if os.path.exists(YML_FILE):
    with open(YML_FILE) as f:
        cfg = yaml.safe_load(f)
        pg = cfg.get("postgres", {})
        DB_HOST = pg.get("host")
        DB_PORT = pg.get("port")
        DB_NAME = pg.get("database")
        DB_USER = pg.get("user")
        DB_PASSWORD = pg.get("password")
else:
    raise FileNotFoundError(f"DB config file '{YML_FILE}' not found!")

DB_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

"""
# Point to Airflow DB, trigger from Airflow UI
# DB_URI = 'postgresql+psycopg2://airflow:airflow@airflow_postgres:5432/airflow' #docker airflow
DB_URI = 'postgresql+psycopg2://airflow:airflow@localhost:6543/airflow'  # local IDE
TABLE_NAME = 'real_estate'
"""
# --------------------------------------------------
# Logging setup
# --------------------------------------------------
logging.basicConfig(
    filename='sql_project.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
# --------------------------------------------------
# Download CSV if missing
# --------------------------------------------------
def get_csv_data(url=CSV_URL, file_path=RAW_CSV):
    if os.path.exists(file_path):
        logging.info(f"File '{file_path}' already exists. Skipping download.")
    else:
        response = requests.get(url)
        if response.status_code == 200:
            logging.info(f"Successfully downloaded CSV from {url}")
            with open(file_path, 'wb') as f:
                f.write(response.content)
        else:
            logging.error(f"Failed to download CSV. Status: {response.status_code}")
            raise Exception("Download failed")


# --------------------------------------------------
# Sample CSV
# --------------------------------------------------
def sample_csv(filename=RAW_CSV, sample_size=10000, output=SAMPLED_CSV):
    df = pd.read_csv(filename, nrows=sample_size)
    df.to_csv(output, index=False)
    logging.info(f"Saved first {sample_size} rows to {output}")
    return df


# --------------------------------------------------
# Create schemas
# --------------------------------------------------
def create_schemas(engine):
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS clean"))
    logging.info("Schemas 'staging' and 'clean' created or verified.")


# --------------------------------------------------
# Load CSV to staging table
# --------------------------------------------------
def load_to_staging(engine, csv_file=SAMPLED_CSV, table_name=TABLE_NAME):
    full_table_name = f"staging.{table_name}"

    # Drop table if exists (transactional)
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {full_table_name} CASCADE;"))
        logging.info(f"Dropped table if existed: {full_table_name}")

    # Load CSV
    df = pd.read_csv(csv_file)

    # Pass engine directly to pandas.to_sql (works with pandas 2.3.2)
    df.to_sql(
        table_name,
        engine,  # pass engine, not connection
        schema='staging',
        index=False,
        if_exists='replace'
    )
    logging.info(f"Loaded {len(df)} rows into {full_table_name}")


# --------------------------------------------------
# ETL Pipeline trigger
# --------------------------------------------------
def etl_pipeline():
    main()  # calls main workflow


# --------------------------------------------------
# Main workflow
# --------------------------------------------------
def main():
    try:
        print("Downloading CSV...")
        get_csv_data()
        print("Sampling CSV...")
        sample_csv()
        print("Connecting to database...")
        engine = create_engine(DB_URI)
        print("Creating schemas...")
        create_schemas(engine)
        print("Loading to staging table...")
        load_to_staging(engine)
        engine.dispose()
        print("Pipeline complete.")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        print("Pipeline failed. Check logs.")


# --------------------------------------------------
if __name__ == "__main__":
    main()
