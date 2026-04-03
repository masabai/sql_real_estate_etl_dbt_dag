# Standard libraries for paths, logging, OS operations
# Pandas for CSV handling, requests for HTTP download
# SQLAlchemy for DB connection and execution
from sqlalchemy import create_engine, text
from pathlib import Path
import pandas as pd
import requests
import logging
import yaml
import os

# URL for raw CSV download from data.gov
CSV_URL = 'https://data.ct.gov/api/views/5mzw-sjtu/rows.csv?accessType=DOWNLOAD'

# Local file names for raw and sampled CSVs
RAW_CSV = 'large_file_million_rows.csv'
SAMPLED_CSV ="realestate_sales.csv"

# Table name in Postgres
TABLE_NAME = "real_estate"
CHUNK_SIZE=100000

# Project root & YAML config
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Load database credentials from config.yml at project root
# Raise FileNotFoundError if config missing
YML_FILE = PROJECT_ROOT / "config.yml"

# Extract Postgres connection details
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

# Construct SQLAlchemy DB URI
DB_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Logging setup
# Log to file 'sql_project.log', info level
logging.basicConfig(
    filename='sql_project.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Download CSV only if it doesn't exist, logging the result
def get_csv_data(url=CSV_URL, file_path=RAW_CSV):
    """
     Downloads a CSV file from a URL if it does not already exist locally.

     Checks the local filesystem for the file; if missing, it fetches the data
     via a GET request and saves it. Logs the outcome of the operation.

     Args:
         url (str): The web address to download the CSV from.
         file_path (str): The local destination path for the file.

     Raises:
         Exception: If the server returns a non-200 status code.
     """
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

def ingest_full_csv(filename=RAW_CSV, table_name=TABLE_NAME, chunk_size=CHUNK_SIZE):
    """
        Chunks a large CSV into PostgreSQL, enforcing string-first reads and
        cleaning numeric columns to prevent schema mismatches.

        Args:
            filename (str): Path to the source CSV file.
            table_name (str): Name of the destination table.
            chunk_size (int): Number of rows per processing batch.

        Raises:
            SQLAlchemyError: If the database connection or execution fails.
        """
    engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

    # Drop existing table to ensure a clean schema for the new ingest
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS staging.{table_name} CASCADE;"))

    # Process in chunks to manage memory; read as strings to avoid mixed-type inference
    for i, chunk in enumerate(pd.read_csv(filename, chunksize=chunk_size, dtype=str)):

        #Standardize Column Names (snake_case)
        chunk.columns = chunk.columns.str.strip().str.replace(" ", "_")

        # Clean and cast critical numeric columns
        numeric_cols = ['Assessed_Value', 'Sale_Amount', 'Sales_Ratio']

        for col in numeric_cols:
            if col in chunk.columns:
                # Remove commas and coerce non-numeric values to NaN
                chunk[col] = pd.to_numeric(
                    chunk[col].astype(str).str.replace(',', '', regex=False),
                    errors='coerce'
                )

        # Batch insert into the staging schema
        chunk.to_sql(
            table_name,
            engine,
            schema='staging',
            if_exists='append',
            index=False,
            method='multi'
        )
        logging.info(f"Chunk {i + 1} cleared. (Total: ~{(i + 1) * chunk_size:,} rows)")

    logging.info("Full 11M row ingestion complete.")

def create_schemas(engine):
    """
        Initializes the required database schemas for the data pipeline.

        Args:
            engine (sqlalchemy.engine.Engine): The database connection engine.
    """
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS clean"))
    logging.info("Schemas 'staging' and 'clean' created or verified.")


def load_to_staging_local(engine, csv_file=RAW_CSV, table_name=TABLE_NAME, chunk_size=CHUNK_SIZE):
    """
        Streams a large CSV into the staging schema using chunked processing.

        Drops the existing table to ensure a fresh schema, cleans headers,
        standardizes numeric formats by removing commas, and batch-inserts
        data into PostgreSQL.

        Args:
            engine (sqlalchemy.engine.Engine): The database connection engine.
            csv_file (str): Path to the source CSV file.
            table_name (str): Name of the target table in the staging schema.
            chunk_size (int): Number of rows to process per iteration.
        """
    full_table_name = f"staging.{table_name}"

    # Clear the old table to ensure a fresh schema for 11M rows
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {full_table_name} CASCADE;"))
        #logging.info(f"Dropped {full_table_name} for fresh 11M row load.")
        print(f"Dropped {full_table_name} for fresh 11M row load.")

    # Stream the CSV in chunks (low_memory=False prevents type-guessing errors)
    for i, chunk in enumerate(pd.read_csv(csv_file, chunksize=chunk_size, low_memory=False)):

        # Clean headers (Underscores instead of spaces)
        chunk.columns = chunk.columns.str.strip().str.replace(" ", "_")

        # Clean specific numeric columns
        numeric_cols = ['Assessed_Value', 'Sale_Amount', 'Sales_Ratio']
        for col in numeric_cols:
            if col in chunk.columns:
                # Force to string -> Remove commas -> Force to Numeric
                # errors='coerce' prevents a single "Bad Data" string from crashing the 11M load
                chunk[col] = pd.to_numeric(
                    chunk[col].astype(str).str.replace(',', '', regex=False),
                    errors='coerce'
                )

        # Load to Postgres: First chunk creates the table ('replace'), others 'append'
        mode = 'replace' if i == 0 else 'append'

        chunk.to_sql(
            table_name,
            engine,
            schema='staging',
            index=False,
            if_exists=mode,
            method='multi'  # Essential for 11M row performance
        )

        if (i + 1) % 10 == 0:
            logging.info(f"Progress: {(i + 1) * chunk_size:,} rows uploaded...")

    logging.info(f"Successfully loaded 11M+ rows into {full_table_name}")


def load_to_staging(engine, csv_file=RAW_CSV, table_name=TABLE_NAME, chunk_size=CHUNK_SIZE):
    """
    Uses Postgres COPY command for high-performance ingestion of 11M rows.

    Args:
        engine (sqlalchemy.engine.Engine): The database engine.
        csv_file (str): Path to the source CSV file.
        table_name (str): Destination table name.
        chunk_size (int): Rows per batch for memory management.
    """
    full_table_name = f"staging.{table_name}"

    # 1. Initialize schema using a 0-row dataframe
    first_chunk = next(pd.read_csv(csv_file, nrows=1))
    first_chunk.columns = first_chunk.columns.str.strip().str.replace(" ", "_")

    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {full_table_name} CASCADE;"))
        # Create table structure only
        first_chunk.iloc[:0].to_sql(table_name, engine, schema='staging', index=False, if_exists='replace')

    # 2. Bulk load using native COPY protocol
    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cur:
            for i, chunk in enumerate(pd.read_csv(csv_file, chunksize=chunk_size, low_memory=False)):
                # Cleanup headers and numeric columns
                chunk.columns = chunk.columns.str.strip().str.replace(" ", "_")
                numeric_cols = ['Assessed_Value', 'Sale_Amount', 'Sales_Ratio']
                for col in numeric_cols:
                    if col in chunk.columns:
                        chunk[col] = pd.to_numeric(
                            chunk[col].astype(str).str.replace(',', '', regex=False),
                            errors='coerce'
                        )

                # Convert cleaned chunk to memory buffer
                output = io.StringIO()
                chunk.to_csv(output, sep='\t', header=False, index=False)
                output.seek(0)

                # Stream buffer to Postgres
                cur.copy_from(output, full_table_name, sep='\t', null="")
                raw_conn.commit()

                if (i + 1) % 10 == 0:
                    logging.info(f"Fast Load: {(i + 1) * chunk_size:,} rows processed...")
    finally:
        raw_conn.close()

    logging.info(f"Bulk ingestion of 11M+ rows complete.")


def etl_pipeline():
    """
        Wrapper function for Airflow to trigger the full data pipeline.
     """
    main()

def main():
    """
        Orchestrates the end-to-end ETL process: downloading the raw data,
        preparing the database environment, and loading cleaned data into staging.

        Handles the lifecycle of the database connection and ensures all
        intermediate steps are logged or reported.

        Raises:
            Exception: If any step of the pipeline fails, it is caught,
                       logged, and reported before termination.
    """
    try:
        print("Downloading CSV...")
        get_csv_data()
        ingest_full_csv(filename=RAW_CSV, table_name=TABLE_NAME, chunk_size=CHUNK_SIZE)
        print("Connecting to database...")
        engine = create_engine(DB_URI)
        print("Creating schemas...")
        create_schemas(engine)
        print("Loading to staging table...")
        load_to_staging(engine, csv_file=RAW_CSV, table_name=TABLE_NAME, chunk_size=CHUNK_SIZE)
        engine.dispose()
        print("Pipeline complete.")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        print("Pipeline failed. Check logs.")

