import pandas as pd
from sqlalchemy import create_engine
import os

csv_file = '/opt/airflow/plugins/etl/realestate_sales.csv'
def load_data(csv_file="/opt/airflow/plugins/etl/realestate_sales.csv", table_name="real_estate_dag"):
    engine = create_engine(
        "postgresql+psycopg2://airflow:airflow@airflow_postgres:5432/airflow"
        #"postgresql+psycopg2://airflow:airflow@airflow_postgres:6543/airflow"
    )

    df = pd.read_csv(csv_file)

    df.to_sql(
        table_name,
        con=engine,
        schema='staging',
        index=False,
        if_exists='replace'
    )

    print(f"Loaded {len(df)} rows into {table_name} successfully.")

if __name__ == "__main__":
    load_data()
